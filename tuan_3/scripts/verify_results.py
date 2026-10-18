"""Offline reconciliation for retained Week 3 evidence and CSV/figure manifests."""
import json
import math
from datetime import datetime

from benchmark import assert_equal_groups
from common import ROOT, digest, read_csv
from dashboard import metric_consistency
from forecast import evaluate
from quality import inspect_rows


def verify_manifest(folder):
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        path = (folder / item['path']).resolve()
        if not path.is_relative_to(folder.resolve()) or digest(path.read_bytes()) != item['sha256'] or path.stat().st_size != item['bytes']:
            raise ValueError('Retained evidence path/hash mismatch')
    return len(manifest['files'])


def verify_operations(folder):
    count = verify_manifest(folder)
    for profile in ('default', 'quyen'):
        filters = json.loads((folder / 'filters' / profile / 'configuration.json').read_text(encoding='utf-8'))
        if (not filters['configuration_verified'] or filters['synthetic_events_ingested'] or filters['lambda_invoked']
                or [(r['expected_matches'], r['observed_matches'], r['status']) for r in filters['pattern_tests']] != [(2, 2, 'PASS'), (1, 1, 'PASS')]):
            raise ValueError('Log-filter configuration/test evidence mismatch')
        raw = read_csv(folder / 'snapshot' / profile / 'raw_all.csv')
        summary, _ = inspect_rows(raw)
        saved = json.loads((folder / 'snapshot' / profile / 'snapshot.json').read_text(encoding='utf-8'))
        if summary['records'] != saved['records'] or summary['issues'] != saved['issues'] or not saved['lambda']['matches_reviewed_release_package']:
            raise ValueError('Current raw quality or published release baseline mismatch')
        cross = json.loads((folder / 'metric_cross_api' / f'{profile}.json').read_text(encoding='utf-8'))
        if cross['next_token']:
            raise ValueError('Metric cross-check is incomplete')
        for item in cross['results']:
            point_set = lambda values: sorted((datetime.fromisoformat(t), float(v)) for t, v in values)
            expected_id = {'Invocations': 'inv', 'Errors': 'err'}[item['metric']]
            if item['status'] != 'Complete' or item['get_metric_data_id'] != expected_id or point_set(item['data_values']) != point_set(item['statistics_values']):
                raise ValueError('Metric methods/identities differ')
        checks = read_csv(folder / 'scheduled_followup/collections' / profile / 'collection_checks.csv')
        raw = read_csv(folder / 'scheduled_followup/collections' / profile / 'raw_verified.csv')
        proof = json.loads((folder / 'scheduled_followup/collections' / profile / 'verification.json').read_text(encoding='utf-8'))
        objects = {item['key']: item['records'] for item in proof['objects']}
        if len(raw) != sum(objects.values()) or len(checks) != proof['result_entries']:
            raise ValueError('Result/S3 record reconciliation mismatch')
        if any(r['record_count_matches'] != 'True' or int(r['reported_records']) != int(r['s3_verified_records']) for r in checks):
            raise ValueError('Saved log count disagrees with S3')
        actual_alerts = sum(float(r['us_aqi']) >= proof['thresholds_at_verification']['aqi']
                            or float(r['pm2_5']) >= proof['thresholds_at_verification']['pm2_5'] for r in raw)
        if actual_alerts != sum(int(r['expected_alerts']) for r in checks):
            raise ValueError('Alert predicate does not reconcile with retained raw')
    repair = json.loads((folder / 'configuration-format-repair.json').read_text(encoding='utf-8'))
    if repair['before_json_valid'] or not all(repair[k] for k in ('after_json_valid', 'operational_fields_unchanged', 'previous_version_retained_and_readback_equal', 'current_version_readback_equal')):
        raise ValueError('Configuration format repair evidence missing')
    return count


def verify(folder):
    file_count = verify_manifest(folder)
    for profile in ('default', 'quyen'):
        raw = read_csv(folder / 'snapshot' / profile / 'raw_all.csv')
        actual, groups = inspect_rows(raw)
        saved = json.loads((folder / 'snapshot' / profile / 'snapshot.json').read_text(encoding='utf-8'))
        for key in ('records', 'week3_calendar_records', 'issues', 'city_hour_groups'):
            if actual[key] != saved[key]:
                raise ValueError('Snapshot quality mismatch')
        if len(groups) != len(read_csv(folder / 'snapshot' / profile / 'hourly_city.csv')):
            raise ValueError('Snapshot hourly group count mismatch')
        benchmark = read_csv(folder / 'benchmark' / profile / 'benchmark.csv')
        if len(benchmark) != 9 or any(r['result_reused'].lower() != 'false' for r in benchmark):
            raise ValueError('Benchmark trial count/reuse mismatch')
        tables = json.loads((folder / 'benchmark' / profile / 'tables.json').read_text())
        if any(item['registered_partitions'] for item in tables.values() if item['projected']):
            raise ValueError('Projection evidence uses registered partitions')
        reference = read_csv(folder / 'benchmark' / profile / 'queries/registered_json_1.csv')
        for trial in benchmark:
            observed = read_csv(folder / 'benchmark' / profile / 'queries' / f"{trial['format']}_{trial['trial']}.csv")
            assert_equal_groups(reference, observed)
    history = read_csv(folder / 'forecast/hourly_model_history.csv')
    metrics = read_csv(folder / 'forecast/forecast_metrics.csv')
    for city in sorted({r['city'] for r in history}):
        for variable in ('us_aqi', 'pm2_5'):
            expected, _, _ = evaluate([r for r in history if r['city'] == city], variable)
            for row in expected:
                saved = next(r for r in metrics if r['city'] == city and r['variable'] == variable and r['model'] == row['model'])
                for field in ('mae', 'rmse', 'bias'):
                    if not math.isclose(float(saved[field]), row[field], rel_tol=1e-11, abs_tol=1e-9):
                        raise ValueError('Forecast holdout error mismatch')
    monitoring = folder.parent / 'monitoring_2026_10_18'
    cd = folder.parent / 'cd_2026_10_18'
    file_count += verify_manifest(monitoring) + verify_manifest(cd)
    file_count += verify_operations(folder.parent / 'operations_2026_10_18')
    for profile in ('default', 'quyen'):
        observed = metric_consistency(read_csv(monitoring / profile / 'metrics.csv'))
        saved = json.loads((monitoring / profile / 'metric-consistency.json').read_text())
        if observed != saved or (observed['error_rate_status'] != 'VALID' and observed['error_rate_percent'] is not None):
            raise ValueError('Metric consistency/undefined rate mismatch')
    artifact = json.loads((cd / 'ci-artifact-verification.json').read_text())
    if not artifact['linux_ci_equals_windows_build']:
        raise ValueError('Cross-platform artifact verification missing')
    for target in ('tien-son', 'ngoc-quyen'):
        proof = json.loads((cd / f'{target}.json').read_text())
        if (proof['target'] != target or proof['status'] != 'PASS' or not proof['configuration_unchanged']
                or proof['commit'] != artifact['commit'] or proof['final_aws_readback'] != 'PASS'
                or proof['deployed_package_sha256'] != artifact['package_sha256']):
            raise ValueError('CD proof identity mismatch')
    for name in ('secret-cleanup.json', 'initial-secret-cleanup.json'):
        cleanup = json.loads((cd / name).read_text())
        if (not cleanup['all_temporary_secrets_removed'] or cleanup['created_secret_count'] != 8
                or cleanup['delete_success_count'] != 8 or any(cleanup['remaining_secret_names'].values())):
            raise ValueError('Temporary secret cleanup incomplete')
    return {'status': 'PASS', 'manifest_files': file_count, 'profiles': 2, 'benchmark_trials': 18,
            'forecast_metrics': len(metrics), 'cd_environments': 2, 'temporary_secrets_remaining': 0}


if __name__ == '__main__':
    print(json.dumps(verify(ROOT / 'tuan_3/results/integration_2026_10_18')))
