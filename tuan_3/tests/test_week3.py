"""Focused invariants: source quality, benchmark parity, metric dimensions."""
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from benchmark import assert_equal_groups, projection, typed_rows
from dashboard import build_dashboard
from quality import REQUIRED, WEEK3_START, WEEK3_END, inspect_rows
from forecast import evaluate, predict, score, consecutive_tail
from release import deployment, package
from unittest.mock import MagicMock, patch
import base64
import hashlib
import tempfile
import io
import zipfile


def row():
    data = {k: 0 for k in REQUIRED}
    data.update({'record_id': 'r1', 'city': 'HaNoi', 'timestamp_utc': '2026-10-18 16:00:00',
                 'timestamp_vn': '2026-10-18 23:00:00', 'collected_at': '2026-10-18T16:00:02+00:00',
                 'year': '2026', 'month': '10', 'day': '18', 'hour': 16, 'aqi_category': 'Good'})
    return data


class Week3Tests(unittest.TestCase):
    def release_fixture(self):
        previous, requested = package(b'old'), package(b'new')
        sha = lambda blob: base64.b64encode(hashlib.sha256(blob).digest()).decode()
        before = {'Runtime': 'python3.12', 'Handler': 'lambda_function.lambda_handler', 'State': 'Active',
                  'RevisionId': 'before', 'CodeSha256': sha(previous), 'LastUpdateStatus': 'Successful'}
        after = {**before, 'RevisionId': 'owned', 'CodeSha256': sha(requested)}
        sts, client, sess = MagicMock(), MagicMock(), MagicMock()
        sts.get_caller_identity.return_value = {'Account': 'expected'}
        sess.client.side_effect = lambda name, **kwargs: sts if name == 'sts' else client
        client.get_function.return_value = {'Configuration': before, 'Code': {'Location': 'https://example.invalid/package'}}
        client.update_function_code.return_value = {'RevisionId': 'owned', 'CodeSha256': sha(requested)}
        client.get_function_configuration.return_value = after
        response = MagicMock(); response.__enter__.return_value.read.return_value = previous
        return sess, client, requested, before, after, response

    def test_release_account_mismatch_prevents_backup_and_mutation(self):
        sess, client, blob, _, _, _ = self.release_fixture()
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                deployment(sess, 'wrong', blob, Path(folder) / 'evidence')
            self.assertFalse((Path(folder) / 'evidence').exists())
        client.get_function.assert_not_called()
        client.update_function_code.assert_not_called()

    def test_release_verifies_exact_package_and_guards_initial_revision(self):
        sess, client, blob, _, _, response = self.release_fixture()
        with tempfile.TemporaryDirectory() as folder, patch('release.urllib.request.urlopen', return_value=response):
            result = deployment(sess, 'expected', blob, Path(folder) / 'evidence')
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(client.update_function_code.call_args.kwargs['RevisionId'], 'before')
        self.assertEqual(client.update_function_code.call_count, 1)

    def test_release_waiter_failure_restores_only_owned_revision(self):
        sess, client, blob, before, after, response = self.release_fixture()
        client.get_waiter.return_value.wait.side_effect = [RuntimeError('timeout'), None]
        client.get_function_configuration.side_effect = [after, before]
        with tempfile.TemporaryDirectory() as folder, patch('release.urllib.request.urlopen', return_value=response):
            evidence = Path(folder) / 'evidence'
            with self.assertRaises(RuntimeError):
                deployment(sess, 'expected', blob, evidence)
            import json
            self.assertTrue(json.loads((evidence / 'release.json').read_text())['rollback_verified'])
        self.assertEqual(client.update_function_code.call_args.kwargs['RevisionId'], 'owned')
        self.assertEqual(client.update_function_code.call_count, 2)

    def test_release_never_rolls_back_another_operators_revision(self):
        sess, client, blob, _, after, response = self.release_fixture()
        client.get_function_configuration.return_value = {**after, 'RevisionId': 'another-operator', 'CodeSha256': 'changed'}
        with tempfile.TemporaryDirectory() as folder, patch('release.urllib.request.urlopen', return_value=response):
            evidence = Path(folder) / 'evidence'
            with self.assertRaises(RuntimeError):
                deployment(sess, 'expected', blob, evidence)
            import json
            self.assertEqual(json.loads((evidence / 'release.json').read_text())['rollback_status'], 'BLOCKED_CONCURRENT_REVISION')
        self.assertEqual(client.update_function_code.call_count, 1)

    def test_release_package_is_reproducible_and_has_only_handler(self):
        blob = package(b'print("example")\n')
        self.assertEqual(blob, package(b'print("example")\n'))
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            self.assertEqual(archive.namelist(), ['lambda_function.py'])
            self.assertEqual(archive.read('lambda_function.py'), b'print("example")\n')
            entry = archive.infolist()[0]
            self.assertEqual(entry.create_system, 3)
            self.assertEqual(entry.compress_type, zipfile.ZIP_STORED)
    def test_forecast_recurses_using_predictions_not_holdout(self):
        values = list(range(120))
        result = predict(values)
        self.assertAlmostEqual(result[0], sum(values[-24:]) / 24)
        self.assertAlmostEqual(result[1], (sum(values[-23:]) + result[0]) / 24)

    def test_future_target_changes_cannot_change_holdout_predictions(self):
        from datetime import timedelta
        start = datetime(2026, 10, 1, tzinfo=timezone.utc)
        rows = [{'timestamp_utc': (start + timedelta(hours=i)).isoformat(), 'us_aqi': i} for i in range(120)]
        _, before, _ = evaluate(rows, 'us_aqi')
        changed = [{**r, 'us_aqi': 9999} if i >= 96 else r.copy() for i, r in enumerate(rows)]
        _, after, _ = evaluate(changed, 'us_aqi')
        self.assertEqual([r['predicted'] for r in before], [r['predicted'] for r in after])
        self.assertNotEqual([r['actual'] for r in before], [r['actual'] for r in after])

    def test_forecast_gap_cannot_be_hidden_as_contiguous_hours(self):
        from datetime import timedelta
        start = datetime(2026, 10, 1, tzinfo=timezone.utc)
        rows = [{'timestamp_utc': (start + timedelta(hours=i)).isoformat(), 'pm2_5': i} for i in range(120) if i != 100]
        self.assertEqual(len(consecutive_tail(rows, 'pm2_5')), 19)
        with self.assertRaises(ValueError):
            evaluate(rows, 'pm2_5')

    def test_forecast_errors_use_same_samples(self):
        self.assertEqual(score([1, 3], [2, 4]), {'mae': 1, 'rmse': 1, 'bias': 1})
        with self.assertRaises(ValueError):
            score([1, 2], [3])

    def test_calendar_boundaries_use_vietnam_week(self):
        self.assertEqual(WEEK3_START, datetime(2026, 10, 18, 17, tzinfo=timezone.utc))
        self.assertEqual(WEEK3_END, datetime(2026, 10, 25, 17, tzinfo=timezone.utc))
        self.assertEqual(inspect_rows([row()])[0]['week3_calendar_records'], 0)

    def test_timezone_and_partition_disagreement_are_detected(self):
        data = row(); data['timestamp_vn'] = '2026-10-18 16:00:00'; data['day'] = '19'
        issues = inspect_rows([data])[0]['issues']
        self.assertEqual(issues['timezone_mismatch_rows'], 1)
        self.assertEqual(issues['partition_mismatch_rows'], 1)

    def test_nonfinite_and_missing_not_reported_as_good(self):
        data = row(); data['pm2_5'] = 'NaN'; data['pm10'] = None
        summary, groups = inspect_rows([data])
        self.assertEqual(summary['issues']['invalid_numeric_cells'], 1)
        self.assertEqual(summary['issues']['missing_numeric_cells'], 1)
        self.assertEqual(groups[0]['avg_pm2_5'], '')

    def test_same_city_hour_is_retained_not_deleted(self):
        a, b = row(), row(); b['record_id'] = 'r2'
        summary, groups = inspect_rows([a, b])
        self.assertEqual(summary['records'], 2)
        self.assertEqual(summary['issues']['duplicate_record_ids'], 0)
        self.assertEqual(groups[0]['sample_count'], 2)

    def test_projection_keeps_padded_hive_paths(self):
        props = projection('s3://example/raw/', [2025, 2026])
        self.assertEqual(props['projection.month.digits'], '2')
        self.assertEqual(props['projection.year.range'], '2025,2026')
        self.assertTrue(props['storage.location.template'].endswith('day=${day}/'))

    def test_parquet_typing_rejects_fractional_int(self):
        data = row(); data['us_aqi'] = '10.5'
        with self.assertRaises(ValueError):
            typed_rows([data])

    def test_parquet_typing_keeps_null_and_zero_distinct(self):
        data = row(); data['pm2_5'] = ''; data['pm10'] = '0'
        typed = typed_rows([data])[0]
        self.assertIsNone(typed['pm2_5']); self.assertEqual(typed['pm10'], 0)

    def test_benchmark_detects_changed_mean(self):
        a = [{'city': 'HaNoi', 'samples': 3, 'avg_aqi': 100}]
        with self.assertRaises(ValueError):
            assert_equal_groups(a, [{'city': 'HaNoi', 'samples': 3, 'avg_aqi': 101}])

    def test_error_rate_uses_same_function_and_period(self):
        body = build_dashboard('topic')
        rate = body['widgets'][3]['properties']
        self.assertEqual(rate['period'], 300)
        for metric in rate['metrics'][:2]:
            self.assertEqual(metric[0], 'AWS/Lambda')
            self.assertEqual(metric[2:4], ['FunctionName', 'WeatherCollectorLambda'])
            self.assertEqual(metric[-1]['stat'], 'Sum')
        self.assertEqual(rate['metrics'][2][0]['expression'], 'IF(inv>0,100*err/inv)')


if __name__ == '__main__':
    unittest.main()
