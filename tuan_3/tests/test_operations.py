"""Operational regression cases: released package baselines and log-filter gates."""
import base64
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from snapshot import reviewed_release, result_counts
from metric_filters import SAMPLES, configure, definitions, validate_match
from check_operations import expected_alerts, policy_allows, saved_object


class OperationsTests(unittest.TestCase):
    def test_saved_files_uses_actual_lambda_descriptor_and_rejects_unsafe_keys(self):
        key = 'raw/year=2026/month=10/day=18/data_example.json'
        self.assertEqual(saved_object({'s3_key': key, 'count': 3}), (key, 3))
        for item in (key, {'s3_key': '../../outside.json', 'count': 3}, {'s3_key': key, 'count': True}):
            with self.assertRaises(ValueError):
                saved_object(item)

    def test_partial_and_contradictory_results_are_not_complete_successes(self):
        summary = result_counts([{'collection_status': 'complete', 'failed_cities': 0},
                                 {'collection_status': 'partial', 'failed_cities': 1},
                                 {'collection_status': 'complete', 'failed_cities': 1}])
        self.assertEqual(summary['recent_success_log_results'], 1)
        self.assertEqual(summary['recent_result_log_entries'], 3)
        self.assertEqual(summary['recent_partial_log_results'], 1)

    def test_alert_or_condition_counts_each_city_only_once(self):
        records = [{'us_aqi': 100, 'pm2_5': 35.5}, {'us_aqi': 99, 'pm2_5': 35.5},
                   {'us_aqi': 100, 'pm2_5': 1}, {'us_aqi': 99, 'pm2_5': 35.4}]
        self.assertEqual(expected_alerts(records, 100, 35.5), 3)
        self.assertEqual(expected_alerts([{'us_aqi': 87, 'pm2_5': 23.2}], 100, 35.5), 0)

    def test_schedule_permission_requires_exact_rule_and_principal(self):
        statement = {'Effect': 'Allow', 'Principal': {'Service': 'events.amazonaws.com'},
                     'Action': 'lambda:InvokeFunction', 'Condition': {'ArnLike': {'AWS:SourceArn': 'expected-rule'}}}
        self.assertTrue(policy_allows({'Statement': [statement]}, 'expected-rule'))
        self.assertFalse(policy_allows({'Statement': [statement]}, 'another-rule'))
        statement['Principal']['Service'] = 'another-service'
        self.assertFalse(policy_allows({'Statement': [statement]}, 'expected-rule'))

    def test_snapshot_uses_published_cd_digest_without_local_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            proof = {'target': 'tien-son', 'status': 'PASS', 'final_aws_readback': 'PASS',
                     'commit': 'reviewed', 'deployed_package_sha256': 'ab' * 32}
            (path / 'tien-son.json').write_text(json.dumps(proof), encoding='utf-8')
            result = reviewed_release('default', path)
            self.assertEqual(result['code_sha256'], base64.b64encode(bytes.fromhex('ab' * 32)).decode())
            self.assertEqual(result['commit'], 'reviewed')

    def test_missing_or_wrong_environment_proof_never_matches_implicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            self.assertIsNone(reviewed_release('quyen', path))
            (path / 'quyen.json').write_text('{}', encoding='utf-8')
            self.assertIsNone(reviewed_release('quyen', path))
            (path / 'ngoc-quyen.json').write_text(json.dumps({'status': 'PASS', 'target': 'tien-son'}), encoding='utf-8')
            with self.assertRaises(ValueError):
                reviewed_release('quyen', path)

    def test_log_counters_have_fixed_cardinality_and_do_not_impute_zero(self):
        filters = definitions()
        self.assertEqual(len(filters), 2)
        self.assertEqual(len({f['filterName'] for f in filters}), 2)
        for item in filters:
            transform = item['metricTransformations'][0]
            self.assertEqual(transform['metricValue'], '1')
            self.assertNotIn('dimensions', transform)
            self.assertNotIn('defaultValue', transform)
            self.assertFalse(transform['metricNamespace'].startswith('AWS/'))

    def test_positive_and_negative_filter_matches_must_be_exact(self):
        response = {'matches': [{'eventMessage': SAMPLES[0]}, {'eventMessage': SAMPLES[1]}]}
        validate_match(response, SAMPLES[:2])
        with self.assertRaises(ValueError):
            validate_match({'matches': [{'eventMessage': SAMPLES[3]}]}, SAMPLES[:2])

    def filter_clients(self, existing):
        logs, sts, lamb = MagicMock(), MagicMock(), MagicMock()
        sts.get_caller_identity.return_value = {'Account': 'expected'}
        lamb.get_function_configuration.return_value = {'FunctionArn': 'arn:aws:lambda:us-east-1:expected:function:WeatherCollectorLambda'}
        logs.get_paginator.return_value.paginate.return_value = [{'metricFilters': existing}]
        factory = lambda sess, service: {'logs': logs, 'sts': sts, 'lambda': lamb}[service]
        return logs, factory

    def test_failed_second_pattern_prevents_both_filter_writes(self):
        logs, factory = self.filter_clients([])
        logs.test_metric_filter.side_effect = [{'matches': [{'eventMessage': m} for m in SAMPLES[:2]]}, {'matches': []}]
        with tempfile.TemporaryDirectory() as directory, patch('metric_filters.session'), patch('metric_filters.client', side_effect=factory):
            with self.assertRaises(ValueError):
                configure('default', Path(directory) / 'output', Path(directory) / 'backup')
        logs.put_metric_filter.assert_not_called()

    def test_existing_different_filter_is_not_overwritten(self):
        changed = definitions()[0]
        changed['metricTransformations'][0]['metricValue'] = '9'
        logs, factory = self.filter_clients([changed])
        logs.test_metric_filter.side_effect = [{'matches': [{'eventMessage': m} for m in SAMPLES[:2]]},
                                               {'matches': [{'eventMessage': SAMPLES[2]}]}]
        with tempfile.TemporaryDirectory() as directory, patch('metric_filters.session'), patch('metric_filters.client', side_effect=factory):
            with self.assertRaises(ValueError):
                configure('default', Path(directory) / 'output', Path(directory) / 'backup')
        logs.put_metric_filter.assert_not_called()


if __name__ == '__main__':
    unittest.main()
