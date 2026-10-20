"""Replay saved advanced evidence offline; never invoke AWS from verification."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import statistics
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tuan_3/scripts'))
from common import ndjson_rows
from backtest_three_windows import evaluate


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(folder):
    expected = load(folder / 'manifest.json')
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*')
              if p.is_file() and p != folder / 'manifest.json'}
    if set(expected) != actual:
        raise ValueError('Evidence manifest membership differs')
    for name, value in expected.items():
        path = (folder / name).resolve()
        if not path.is_relative_to(folder.resolve()) or sha(path) != value:
            raise ValueError('Evidence manifest path/hash differs')


def compare(expected, observed):
    if len(expected) != len(observed):
        raise ValueError('Replayed table length differs')
    for left, right in zip(expected, observed):
        if set(left) != set(right):
            raise ValueError('Replayed table columns differ')
        for key, value in left.items():
            if isinstance(value, (float, int)):
                if not math.isclose(float(value), float(right[key]), abs_tol=1e-9, rel_tol=1e-11):
                    raise ValueError('Replayed number differs')
            elif str(value) != right[key]:
                raise ValueError('Replayed metadata differs')


def stack_bindings(folder, profile, environment, proof, deployment, raw):
    invocation = load(folder / 'invocation.json')
    runtime = load(folder / 'runtime_controls.json')
    configuration = load(folder / 'configuration.json')
    expected_function = f'weather-w4-{environment}-collector'
    expected_stack = f'weather-w4-{environment}'
    if any(value.get('profile') != profile for value in (proof, deployment, runtime, configuration)):
        raise ValueError('Stack profile differs across evidence')
    if any(value.get('function_name') != expected_function for value in (proof, runtime, configuration, invocation)):
        raise ValueError('Stack function differs across evidence')
    if any(value.get('stack_name') != expected_stack for value in (proof, deployment, configuration)):
        raise ValueError('Stack identity differs across evidence')
    if (deployment.get('stack_status') != 'CREATE_COMPLETE' or not deployment.get('stack_created')
            or deployment.get('initial_schedule') != 'DISABLED'):
        raise ValueError('Deployment lifecycle differs')
    for key, value in configuration.items():
        if key != 'invocation_executed' and proof.get(key) != value:
            raise ValueError('Runtime summary differs from configuration readback')
    if load(folder / 'athena_exact.json') != proof['athena']:
        raise ValueError('Standalone Athena proof differs from summary')
    if (not invocation.get('request_hash') or invocation['request_hash'] != runtime['request_hash']
            or invocation['source_sha256'] != proof['source_sha256']
            or deployment['source_sha256'] != proof['source_sha256']):
        raise ValueError('Invocation/request/source binding differs')
    expected_alerts = sum(float(row['us_aqi']) >= invocation['threshold_aqi'] or
                          float(row['pm2_5']) >= invocation['threshold_pm2_5'] for row in raw)
    if (invocation['status'] != 'PASS' or invocation['records'] != len(raw)
            or expected_alerts != invocation['expected_alerts']
            or expected_alerts != invocation['reported_sns_acceptances']
            or any(invocation.get(k) != v for k, v in proof['alerts'].items())):
        raise ValueError('Raw threshold evaluation differs from invocation')
    objects = {p.relative_to(folder / 'objects').as_posix(): len(ndjson_rows(p.read_bytes()))
               for p in (folder / 'objects').rglob('*.json')}
    if objects != {item['s3_key']: item['count'] for item in invocation['saved_files']}:
        raise ValueError('Invocation refers to another raw object')
    if runtime['matching_result_logs'] != [{'records': len(raw), 'alerts': expected_alerts,
                                            'collection_status': 'complete'}]:
        raise ValueError('Result log differs from invocation')
    if (runtime['metric_period_seconds'] != 300 or
            runtime['native_metrics']['Invocations'][0]['timestamp_utc'] !=
            runtime['native_metrics']['Errors'][0]['timestamp_utc']):
        raise ValueError('Native metric periods differ')
    return runtime


def email_binding(live, profile, environment):
    publish = load(live / 'email' / f'{profile}.json')
    receipt = load(live / 'email' / 'recipient_confirmation.json')
    if (publish['profile'] != profile or publish['topic_name'] != f'weather-w4-{environment}-alerts'
            or not publish['subscription_confirmed'] or publish['publish_status'] != 'ACCEPTED'
            or publish['kind'] != 'explicit_email_channel_test' or not publish['not_a_threshold_alert']
            or len(publish['message_id_hash']) != 64 or receipt['kind'] != publish['kind']
            or not receipt['not_a_threshold_alert'] or not receipt['profiles'][profile]['subscription_confirmed']
            or receipt['profiles'][profile]['recipient_receipt'] != 'CONFIRMED_BY_RECIPIENT'):
        raise ValueError('New-topic channel test/recipient evidence differs')


def benchmark_trials(folder, source_rows, summary, trials, trial_ids):
    selected_date = summary['selected_date']
    selected = [r for r in source_rows if '-'.join(r[k] for k in ('year', 'month', 'day')) == selected_date]
    expected = []
    for city in sorted({r['city'] for r in selected}):
        group = [r for r in selected if r['city'] == city]
        expected.append({'city': city, 'samples': len(group),
                         'avg_aqi': statistics.mean(float(r['us_aqi']) for r in group),
                         'avg_pm2_5': statistics.mean(float(r['pm2_5']) for r in group)})
    if not selected or len(selected) != summary['selected_records']:
        raise ValueError('Selected benchmark input differs')
    for row in trials:
        name = f"{row['format']}_{row['trial']}"
        query = load(folder / 'queries' / f'{name}.json')
        if (query['name'] != name or query['query_id'] != row['query_id']
                or query['status'] != 'SUCCEEDED' or query['result_reused']
                or row['result_reused'] != 'False' or row['query_id'] in trial_ids
                or row['selected_date'] != selected_date or int(row['input_rows']) != len(selected)):
            raise ValueError('Benchmark query identity/status differs')
        for metric in ('bytes_scanned', 'engine_ms', 'total_ms', 'planning_ms'):
            if query[metric] != int(row[metric]):
                raise ValueError('Benchmark statistics differ from query proof')
        compare(expected, rows(folder / 'queries' / f'{name}.csv'))
        trial_ids.add(row['query_id'])
    for kind, medians in summary['medians'].items():
        for metric, value in medians.items():
            if value != statistics.median(int(r[metric]) for r in trials if r['format'] == kind):
                raise ValueError('Benchmark median differs from measured trials')
    expected_change = (summary['medians']['projected_parquet']['bytes_scanned'] /
                       summary['medians']['projected_json']['bytes_scanned'] - 1) * 100
    if not math.isclose(summary['parquet_scan_change_percent'], expected_change, abs_tol=1e-9):
        raise ValueError('Benchmark scan percentage differs')


def validate():
    live = ROOT / 'tuan_4/results/advanced_live_2026_10_20'
    backtest = ROOT / 'tuan_4/results/backtest_2026_10_20'
    manifest(live)
    manifest(backtest)
    source = (ROOT / 'tuan_2/lambda/lambda_function.py').read_text(encoding='utf-8').replace('\r\n', '\n').encode()
    template = (ROOT / 'tuan_4/infrastructure/weather-stack.json').read_text(encoding='utf-8').encode()
    trial_ids = set()
    for profile, environment in [('default', 'son'), ('quyen', 'quyen')]:
        folder = live / 'stacks' / profile
        proof, deployment = load(folder / 'summary.json'), load(folder / 'deployment_summary.json')
        if (proof['source_sha256'] != hashlib.sha256(source).hexdigest()
                or deployment['template_sha256'] != hashlib.sha256(template).hexdigest()
                or deployment['artifact_sha256'] != proof['artifact_sha256']
                or proof['stack_status'] != 'CREATE_COMPLETE'
                or not proof['invocation_executed'] or proof['schedule_state'] != 'DISABLED'):
            raise ValueError('Deployed source, template or runtime evidence differs')
        raw = rows(folder / 'raw_invocation.csv')
        query = rows(folder / 'athena_exact.csv')
        objects = list((folder / 'objects').rglob('*.json'))
        original = [r for path in objects for r in ndjson_rows(path.read_bytes())]
        if len(raw) != 3 or len(original) != 3 or len(query) != 3:
            raise ValueError('Isolated stack row coverage differs')
        compare(original, raw)
        actual = {r['record_id']: r for r in query}
        for r in raw:
            q = actual[r['record_id']]
            if q['city'] != r['city'] or any(float(q[k]) != float(r[k]) for k in ('us_aqi', 'pm2_5')):
                raise ValueError('Exact Athena parity differs')
        if (proof['athena']['database'] != f'weather_w4_{environment}'
                or proof['athena']['workgroup'] != f'weather-w4-{environment}'
                or proof['athena']['result_reused']):
            raise ValueError('Athena proof is not bound to the new stack')
        trial_ids.add(proof['athena']['query_id'])
        runtime = stack_bindings(folder, profile, environment, proof, deployment, raw)
        email_binding(live, profile, environment)
        if not all(runtime[k] for k in ('https_only_policy_observed', 'bucket_owner_enforced', 'rule_source_arn_and_account_bound')):
            raise ValueError('Observed security control differs')
        if set(runtime['matched_lifecycle']) != {'START', 'END', 'REPORT'}:
            raise ValueError('Request lifecycle incomplete')
        for metric, expected in [('Invocations', 1), ('Errors', 0)]:
            if [p['sum'] for p in runtime['native_metrics'][metric]] != [expected]:
                raise ValueError('Exact native metric period differs')
        state = load(live / 'session' / f'{profile}.json')
        if (state['before_state'] != state['final_state'] or not state['binding_unchanged']
                or state['paused']['current_state'] != 'DISABLED' or state['data_deleted']):
            raise ValueError('Session restore evidence differs')
        snapshot = live / 'snapshot' / profile
        source_rows = rows(snapshot / 'raw_all.csv')
        archived = []
        for item in rows(snapshot / 'object_inventory.csv'):
            path = snapshot / 'objects' / item['key']
            records = ndjson_rows(path.read_bytes())
            if sha(path) != item['sha256'] or len(records) != int(item['records']):
                raise ValueError('Frozen raw inventory differs')
            archived.extend(records)
        compare(archived, source_rows)
        summary = load(live / 'benchmark' / profile / 'summary.json')
        trials = rows(live / 'benchmark' / profile / 'benchmark.csv')
        if (summary['source_sha256'] != sha(snapshot / 'raw_all.csv')
                or summary['input_records'] != len(source_rows) or summary['result_parity'] != 'PASS'
                or len(trials) != 9 or {(r['format'], r['trial']) for r in trials} != {
                    (kind, str(n)) for kind in ('registered_json', 'projected_json', 'projected_parquet') for n in (1, 2, 3)}):
            raise ValueError('Frozen-input benchmark coverage differs')
        benchmark_trials(live / 'benchmark' / profile, source_rows, summary, trials, trial_ids)
    protocol = load(backtest / 'protocol.json')
    if (protocol['operational_issued_forecasts'] or protocol['station_observations']
            or protocol['model'] != 'moving_average_24h' or protocol['windows'] != 3):
        raise ValueError('Backtest protocol differs')
    backtest_summary = load(backtest / 'summary.json')
    cutoff = datetime.fromisoformat(backtest_summary['shared_cutoff_exclusive_utc'])
    history = rows(backtest / 'history.csv')
    source_values = {}
    for source in backtest_summary['sources']:
        if cutoff > datetime.fromisoformat(source['captured_at']).replace(minute=0, second=0, microsecond=0):
            raise ValueError('Backtest cutoff includes an incomplete hour')
        hourly = load(backtest / 'model_source' / f"{source['city']}_api.json")['hourly']
        for index, stamp in enumerate(hourly['time']):
            parsed = datetime.fromisoformat(stamp).replace(tzinfo=timezone.utc)
            if parsed < cutoff:
                source_values[source['city'], parsed] = {k: hourly[k][index] for k in ('us_aqi', 'pm2_5')}
    if len(history) != len(source_values):
        raise ValueError('Historical source coverage differs')
    for item in history:
        expected = source_values[item['city'], datetime.fromisoformat(item['timestamp_utc'])]
        if any(float(item[k]) != float(expected[k]) for k in expected):
            raise ValueError('History differs from saved API response')
    predictions, metrics = evaluate(history)
    compare(predictions, rows(backtest / 'predictions.csv'))
    compare(metrics, rows(backtest / 'metrics.csv'))
    return {'status': 'PASS', 'stacks': 2, 'benchmark_trials': 18,
            'backtest_predictions': len(predictions), 'backtest_metrics': len(metrics), 'aws_calls': False}


if __name__ == '__main__':
    print(json.dumps(validate()))
