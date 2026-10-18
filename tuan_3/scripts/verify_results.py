"""Offline reconciliation for retained Week 3 evidence and CSV/figure manifests."""
import json
import math
from datetime import datetime

from benchmark import assert_equal_groups
from common import ROOT, digest, ndjson_rows, read_csv
from dashboard import ERROR_RATE, metric_consistency, reconcile_periods
from forecast import evaluate, future_forecast
from quality import inspect_rows
from reconcile_analysis import VARIABLES, WEATHER, correlation, descriptive, hourly_rows, partial_comparison, ranks, recursive_mean
from forecast import score
from forecast_followup import summarize
from monitoring_followup import point_map


def verify_followups(root):
    monitoring=root/'monitoring_followup_2026_10_18'
    forecast=root/'forecast_followup_2026_10_18'
    count=verify_manifest(monitoring)+verify_manifest(forecast)
    for profile in ('default','quyen'):
        base=monitoring/profile
        native=read_csv(base/'native_statistics.csv')
        proof=json.loads((base/'summary.json').read_text(encoding='utf-8'))
        aligned=reconcile_periods(native)
        if aligned!=proof['period_reconciliation'] or metric_consistency(native)!=proof['native_summary']:
            raise ValueError('Followup native reconciliation differs from source points')
        if not proof['api_parity'] or point_map(native)!=point_map(read_csv(base/'native_data.csv')):
            raise ValueError('Followup metric APIs differ')
        resource_equal=point_map(native)==point_map(read_csv(base/'resource_statistics.csv'))
        if proof['resource_dimension_same_points']!=resource_equal:
            raise ValueError('Followup resource-dimension proof differs')
        minute=read_csv(base/'minute_statistics.csv')
        if proof['minute_totals']!={name:sum(float(r['value']) for r in minute if r['metric']==name) for name in ('Invocations','Errors','Throttles')}:
            raise ValueError('Followup minute totals differ')
        saved=read_csv(base/'period_reconciliation.csv')
        if len(saved)!=len(aligned['periods']) or any(a[k]!=('' if v is None else str(v)) for a,b in zip(saved,aligned['periods']) for k,v in b.items()):
            raise ValueError('Followup period CSV differs')
        start=datetime.fromisoformat(proof['window_start_utc']);end=datetime.fromisoformat(proof['window_end_exclusive_utc'])
        if start>=end or any(t.minute%5 or t.second or t.microsecond for t in (start,end)):
            raise ValueError('Followup metric window is not aligned')
        if any(not start<=datetime.fromisoformat(r['timestamp_utc'])<end for r in native):
            raise ValueError('Followup native point outside requested window')
        lifecycle=read_csv(base/'log_lifecycle.csv')
        log=proof['log_summary']
        ids={kind:{r['request_hash'] for r in lifecycle if r['kind']==kind} for kind in ('START','END','REPORT')}
        if log['matched_start_end_report']!=len(set.intersection(*ids.values())):
            raise ValueError('Followup lifecycle identity match differs')
        for key,kind in (('unique_start_requests','START'),('unique_end_requests','END'),('unique_report_requests','REPORT')):
            if log[key]!=len(ids[kind]): raise ValueError('Followup unique request count differs')
        if log['result_lines']!=sum(r['kind']=='RESULT' for r in lifecycle) or log['complete_results']!=sum(r['kind']=='RESULT' and r['status']=='complete' for r in lifecycle):
            raise ValueError('Followup Result-line counts differ')
        dashboard=json.loads((base/'dashboard.json').read_text(encoding='utf-8'))
        rate=dashboard['widgets'][3]['properties']['metrics'][2][0]['expression']
        diagnostics=dashboard['widgets'][7]['properties']['metrics']
        if rate!='IF(inv>0,IF(FILL(err,-1)>=0,IF(err<=inv,100*err/inv)))' or diagnostics[2][0]['expression']!='IF(FILL(inv,-1)<0,err)' or not proof['dashboard_update']['readback_matches']:
            raise ValueError('Initial dashboard attempt identity differs; use repaired proof for acceptance')
        if proof['lambda_invoked'] or proof['synthetic_events_injected'] or proof['lambda_code_or_configuration_changed']:
            raise ValueError('Followup observation unexpectedly changed Lambda or generated data')
    repaired=root/'monitoring_dashboard_repair_2026_10_18'
    count+=verify_manifest(repaired)
    for profile in ('default','quyen'):
        body=json.loads((repaired/profile/'dashboard.json').read_text(encoding='utf-8'))
        proof=json.loads((repaired/profile/'verification.json').read_text(encoding='utf-8'))
        math_checks=json.loads((repaired/profile/'metric_math_checks.json').read_text(encoding='utf-8'))
        if body['widgets'][3]['properties']['metrics'][2][0]['expression']!=ERROR_RATE or not proof['readback_matches']:
            raise ValueError('Final dashboard flat guard/readback differs')
        if math_checks['status']!='PASS' or len(math_checks['checks'])!=6 or math_checks['synthetic_metrics_or_events_written']:
            raise ValueError('Read-only metric math tests incomplete')
        native_inputs={r['timestamp_utc']:float(r['value']) for r in read_csv(monitoring/profile/'native_statistics.csv') if r['metric']=='Invocations'}
        if math_checks['native_input_points']!=native_inputs or not native_inputs or any(v<=0 for v in native_inputs.values()):
            raise ValueError('Metric math test inputs differ from retained positive native counts')
        cases={'missing_errors','errors_above_invocations','missing_invocations','zero_invocations','valid_zero_errors','valid_half_errors'}
        if {r['case'] for r in math_checks['checks']}!=cases:
            raise ValueError('Metric math verification cases missing or repeated')
        for row in math_checks['checks']:
            if row['case'] in ('missing_errors','missing_invocations'):
                expected_values={t:0.0 for t in native_inputs if datetime.fromisoformat(t).hour==8}
            elif row['case'] in ('errors_above_invocations','zero_invocations'):
                expected_values={}
            else:
                expected_values={t:50.0 if row['case']=='valid_half_errors' else 0.0 for t in native_inputs}
            if row['status']!='PASS' or row['repaired_output']!=expected_values or row['expected']!=expected_values:
                raise ValueError('Metric math repaired output differs from expected data gaps')
    provenance=json.loads((forecast/'provenance.json').read_text(encoding='utf-8'))
    issued_path=ROOT/provenance['issued_path']
    if not issued_path.resolve().is_relative_to(ROOT) or digest(issued_path.read_bytes())!=provenance['issued_sha256']:
        raise ValueError('Issued forecast source changed')
    issued=read_csv(issued_path);later=read_csv(forecast/'history.csv')
    cutoff=datetime.fromisoformat(provenance['cutoff_exclusive_utc'])
    if cutoff!=min(datetime.fromisoformat(s['historical_cutoff_exclusive_utc']) for s in provenance['sources']):
        raise ValueError('Followup source cutoffs differ')
    for source in provenance['sources']:
        payload=json.loads((forecast/'model_source'/f"{source['city']}_api.json").read_text(encoding='utf-8'))
        records=[r for r in later if r['city']==source['city']]
        if payload['utc_offset_seconds']!=0 or len(records)!=source['retained_hours']:
            raise ValueError('Followup model source count/timezone differs')
        times={datetime.fromisoformat(t).replace(tzinfo=cutoff.tzinfo).isoformat():i for i,t in enumerate(payload['hourly']['time'])}
        for row in records:
            if datetime.fromisoformat(row['timestamp_utc'])>=datetime.fromisoformat(source['historical_cutoff_exclusive_utc']):
                raise ValueError('Followup includes an uncompleted model hour')
            i=times[row['timestamp_utc']]
            if any(not math.isclose(float(row[k]),float(payload['hourly'][k][i]),rel_tol=1e-11,abs_tol=1e-9) for k in ('us_aqi','pm2_5')):
                raise ValueError('Followup model CSV differs from retained API payload')
    expected=partial_comparison(issued,later,cutoff);saved=read_csv(forecast/'comparison.csv')
    if len(saved)!=len(expected) or any(a[k]!=str(v) for a,b in zip(saved,expected) for k,v in b.items()):
        raise ValueError('Followup comparison differs from unchanged issued values and completed model hours')
    hours=len({r['timestamp_utc'] for r in saved})
    if provenance['matched_values']!=len(saved) or provenance['matched_target_hours']!=hours or len(saved)!=hours*6 or len(issued)!=144:
        raise ValueError('Followup coverage dimensions differ')
    metrics=read_csv(forecast/'comparison_metrics.csv');expected_metrics=summarize(issued,expected)
    if len(metrics)!=6 or len(metrics)!=len(expected_metrics): raise ValueError('Followup score dimensions differ')
    for a,b in zip(metrics,expected_metrics):
        for k,v in b.items():
            if isinstance(v,(int,float)):
                if not math.isclose(float(a[k]),v,rel_tol=1e-11,abs_tol=1e-9): raise ValueError('Followup score differs')
            elif a[k]!=v: raise ValueError('Followup score key differs')
    return count,hours,len(saved)


def verify_refresh(folder):
    count = verify_manifest(folder)
    analysis = folder / 'analysis'
    stats = read_csv(analysis / 'descriptive.csv')
    corrs = read_csv(analysis / 'correlations.csv')
    if len(stats) != 96 or len(corrs) != 120:
        raise ValueError('Supplementary statistics dimensions differ')
    for profile in ('default', 'quyen'):
        raw = read_csv(folder / 'snapshot' / profile / 'raw_all.csv')
        saved = json.loads((folder / 'snapshot' / profile / 'snapshot.json').read_text(encoding='utf-8'))
        quality, _ = inspect_rows(raw)
        if any(quality[k] != saved[k] for k in ('records', 'issues', 'week3_calendar_records', 'city_hour_groups')) or not saved['lambda']['matches_reviewed_release_package']:
            raise ValueError('Refreshed raw/source proof differs')
        for scope, records in (('raw', raw), ('city_hour', hourly_rows(raw))):
            for city in sorted({r['city'] for r in records}):
                group = [r for r in records if r['city'] == city]
                for variable in VARIABLES:
                    selected = [r for r in stats if (r['profile'], r['scope'], r['city'], r['variable']) == (profile, scope, city, variable)]
                    if len(selected) != 1:
                        raise ValueError('Descriptive key missing or repeated')
                    for key, value in descriptive([r[variable] for r in group]).items():
                        if value is None and selected[0][key] != '' or value is not None and not math.isclose(float(selected[0][key]), value, rel_tol=1e-11, abs_tol=1e-9):
                            raise ValueError('Descriptive value differs from retained raw')
                for target in ('pm2_5', 'us_aqi'):
                    for variable in WEATHER:
                        selected = [r for r in corrs if (r['profile'], r['scope'], r['city'], r['target'], r['variable']) == (profile, scope, city, target, variable)]
                        if len(selected) != 1:
                            raise ValueError('Correlation key missing or repeated')
                        x, y = [float(r[variable]) for r in group], [float(r[target]) for r in group]
                        for key, value in (('pearson_r', correlation(x, y)), ('spearman_rho', correlation(ranks(x), ranks(y)))):
                            if value is None and selected[0][key] != '' or value is not None and not math.isclose(float(selected[0][key]), value, rel_tol=1e-11, abs_tol=1e-9):
                                raise ValueError('Correlation differs from retained raw')
    history = read_csv(folder.parent / 'integration_2026_10_18/forecast/hourly_model_history.csv')
    predictions = read_csv(analysis / 'ma_comparison_predictions.csv')
    metrics = read_csv(analysis / 'ma_comparison_metrics.csv')
    if len(predictions) != 576 or len(metrics) != 24:
        raise ValueError('MA experiment dimensions differ')
    for city in sorted({r['city'] for r in history}):
        series = sorted((r for r in history if r['city'] == city), key=lambda r:r['timestamp_utc'])
        for variable in ('us_aqi', 'pm2_5'):
            _, expected, _ = evaluate(series, variable)
            estimates = recursive_mean([r[variable] for r in series[:-24]], 3)
            expected.extend({'model':'moving_average_3h', 'timestamp_utc':r['timestamp_utc'], 'actual':float(r[variable]), 'predicted':p}
                            for r,p in zip(series[-24:], estimates))
            for row in expected:
                selected = [r for r in predictions if (r['city'], r['variable'], r['model'], r['timestamp_utc']) == (city, variable, row['model'], row['timestamp_utc'])]
                if len(selected) != 1 or any(not math.isclose(float(selected[0][k]),row[k],rel_tol=1e-11,abs_tol=1e-9) for k in ('actual','predicted')):
                    raise ValueError('MA experiment prediction/target differs')
            for model in {r['model'] for r in expected}:
                group = [r for r in expected if r['model'] == model]
                selected = [r for r in metrics if (r['city'],r['variable'],r['model']) == (city,variable,model)]
                calculated = score([r['actual'] for r in group],[r['predicted'] for r in group])
                if len(selected) != 1 or any(not math.isclose(float(selected[0][k]),v,rel_tol=1e-11,abs_tol=1e-9) for k,v in calculated.items()):
                    raise ValueError('MA experiment score differs')
    later = read_csv(analysis / 'later_model/history.csv')
    provenance = json.loads((analysis / 'later_model/provenance.json').read_text(encoding='utf-8'))
    for source in provenance['sources']:
        payload = json.loads((analysis / 'later_model' / f"{source['city']}_api.json").read_text(encoding='utf-8'))
        actual = [r for r in later if r['city'] == source['city']]
        cutoff = datetime.fromisoformat(source['historical_cutoff_exclusive_utc'])
        hourly = payload['hourly']
        indexed = {datetime.fromisoformat(t).replace(tzinfo=cutoff.tzinfo).isoformat():i for i,t in enumerate(hourly['time'])}
        if payload['utc_offset_seconds'] != 0 or len(actual) != source['retained_hours']:
            raise ValueError('Later-model source timezone/row count differs')
        for row in actual:
            if datetime.fromisoformat(row['timestamp_utc']) >= cutoff or row['timestamp_utc'] not in indexed:
                raise ValueError('Later-model history includes unavailable hour')
            i = indexed[row['timestamp_utc']]
            if any(not math.isclose(float(row[k]),float(hourly[k][i]),rel_tol=1e-11,abs_tol=1e-9) for k in ('pm2_5','us_aqi')):
                raise ValueError('Later-model CSV differs from archived API response')
    issued = read_csv(folder.parent / 'forecast_issued_2026_10_18/forecast_24h.csv')
    expected = partial_comparison(issued,later,datetime.fromisoformat(provenance['cutoff_exclusive_utc']))
    saved = read_csv(analysis / 'later_model/comparison.csv')
    if len(saved) != len(expected) or not saved or len(saved) >= len(issued):
        raise ValueError('Partial later-model comparison must remain explicitly partial')
    for a,b in zip(saved,expected):
        if any(a[k] != str(b[k]) for k in b):
            raise ValueError('Later-model comparison differs from issued predictions/history')
    worklog = read_csv(ROOT / 'tuan_3/worklog.csv')
    if worklog != read_csv(ROOT / 'tuan_3/docs/worklog.csv') or len(worklog) != 2:
        raise ValueError('Week3 confirmed-hour mirrors differ')
    if ({r['student_id']:float(r['duration_hours']) for r in worklog} != {'24110054':10.0,'24110051':10.0}
            or any(r['time_basis'] != 'Tổng theo tuần đã xác nhận' or r['status'] != 'Đã hoàn thành kế hoạch công việc tích hợp Tuần 3' for r in worklog)):
        raise ValueError('Week3 hours or status differ from confirmed weekly totals')
    if any(r.get('date') for r in worklog):
        raise ValueError('Confirmed weekly totals must not invent work dates')
    return count


def verify_raw_export(folder):
    count = verify_manifest(folder)
    proof = json.loads((folder / 'export.json').read_text(encoding='utf-8'))
    for profile in ('default', 'quyen'):
        base = folder / 'snapshot' / profile
        inventory = read_csv(base / 'object_inventory.csv')
        flattened = []
        for item in inventory:
            target = (base / 'objects' / item['key']).resolve()
            if not target.is_relative_to((base / 'objects').resolve()):
                raise ValueError('Raw archive path leaves snapshot')
            blob = target.read_bytes()
            objects = ndjson_rows(blob)
            if digest(blob) != item['sha256'] or len(blob) != int(item['bytes']) or len(objects) != int(item['records']):
                raise ValueError('Archived NDJSON differs from S3 inventory')
            flattened.extend({k: '' if v is None else str(v) for k,v in r.items()} for r in objects)
        raw = read_csv(base / 'raw_all.csv')
        if raw != flattened or len(inventory) != len(list((base / 'objects').rglob('*.json'))):
            raise ValueError('Raw CSV differs from original NDJSON archive')
        summary, groups = inspect_rows(raw)
        saved = json.loads((base / 'snapshot.json').read_text(encoding='utf-8'))
        if any(saved[k] != summary[k] for k in summary) or len(groups) != len(read_csv(base / 'hourly_city.csv')):
            raise ValueError('Raw export quality summary differs')
        if not saved['lambda']['matches_reviewed_release_package'] or proof['profiles'][profile]['records'] != len(raw):
            raise ValueError('Raw export source/count proof differs')
        previous = read_csv(folder.parent / 'refresh_2026_10_18/snapshot' / profile / 'raw_all.csv')
        current = {r['record_id']:r for r in raw}
        if any(current.get(r['record_id']) != r for r in previous):
            raise ValueError('Previously retained raw records changed or disappeared')
    return count


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


def verify_post_repair(folder):
    count = verify_manifest(folder)
    proof = json.loads((folder / 'post-repair-observation.json').read_text(encoding='utf-8'))
    repair = json.loads((folder.parent / 'operations_2026_10_18/configuration-format-repair.json').read_text(encoding='utf-8'))
    collected = json.loads((folder / 'collection_check/quyen/verification.json').read_text(encoding='utf-8'))
    checks = read_csv(folder / 'collection_check/quyen/collection_checks.csv')
    raw = read_csv(folder / 'collection_check/quyen/raw_verified.csv')
    metrics = read_csv(folder / 'filter_observation/quyen/log_metrics.csv')
    observed = json.loads((folder / 'filter_observation/quyen/observation.json').read_text(encoding='utf-8'))
    if (proof['status'] != 'OBSERVED' or proof['lambda_invoked'] or not proof['custom_result_metric_observed']
            or proof['config_fallback_warning_events_returned'] != 0 or proof['warning_query_has_more_pages']):
        raise ValueError('Post-repair observation is incomplete or reports configuration fallback')
    if (collected['invoked_by_this_check'] or not collected['package_matches_reviewed_release']
            or collected['rule'] != {'state': 'ENABLED', 'schedule': 'rate(1 hour)',
                                    'matching_targets': 1, 'source_rule_permission': True}
            or collected['result_entries'] != 1 or len(checks) != 1 or len(raw) != 3):
        raise ValueError('Post-repair rule/release/collection evidence differs')
    row = checks[0]
    stamp = datetime.fromisoformat(row['timestamp_utc'])
    if (stamp <= datetime.fromisoformat(repair['checked_at']) or row['timestamp_utc'] != proof['result_timestamp_utc']
            or not datetime.fromisoformat(collected['window_start']) <= stamp <= datetime.fromisoformat(collected['window_end'])
            or row['collection_status'] != 'complete' or proof['collection_status'] != 'complete'
            or any(row[k] != 'True' for k in ('record_count_matches', 'alert_count_matches_current_thresholds', 'after_current_lambda_update'))
            or any(int(row[k]) != 3 for k in ('reported_records', 's3_verified_records', 'cities'))
            or int(row['failed_cities']) != 0 or proof['reported_records'] != 3):
        raise ValueError('Post-repair result does not prove a complete three-city collection')
    quality, _ = inspect_rows(raw)
    if any(quality['issues'].values()) or len({r['city'] for r in raw}) != 3 or sum(r['records'] for r in collected['objects']) != 3:
        raise ValueError('Post-repair raw quality/count mismatch')
    thresholds = collected['thresholds_at_verification']
    alerts = sum(float(r['us_aqi']) >= thresholds['aqi'] or float(r['pm2_5']) >= thresholds['pm2_5'] for r in raw)
    if any(alerts != value for value in (int(row['expected_alerts']), int(row['reported_alerts_sent']), proof['reported_alerts_sent'])):
        raise ValueError('Post-repair alert predicate disagrees with raw/result')
    total = sum(float(r['value']) for r in metrics if r['metric'] == 'ResultLogLines')
    if not observed['result_ingestion_observed'] or total <= 0 or total != observed['metric_sums']['ResultLogLines']:
        raise ValueError('Post-repair custom result metric not observed')
    return count


def verify_issued_forecast(folder):
    count = verify_manifest(folder)
    history = read_csv(folder / 'hourly_model_history.csv')
    forecasts = read_csv(folder / 'forecast_24h.csv')
    metrics = read_csv(folder / 'forecast_metrics.csv')
    if len(forecasts) != 144 or len(metrics) != 18:
        raise ValueError('Issued forecast/evaluation dimensions differ')
    for city in sorted({r['city'] for r in history}):
        selected = [r for r in history if r['city'] == city]
        for variable in ('us_aqi', 'pm2_5'):
            rows = [r for r in forecasts if r['city'] == city and r['variable'] == variable]
            if len(rows) != 24 or len({r['issued_at_utc'] for r in rows}) != 1:
                raise ValueError('Forecast must have exactly 24 targets for one issuance')
            issued = datetime.fromisoformat(rows[0]['issued_at_utc'])
            expected = future_forecast(selected, variable, issued)
            for actual, calculated in zip(rows, expected):
                if (datetime.fromisoformat(actual['timestamp_utc']) <= issued or actual['timestamp_utc'] != calculated['timestamp_utc']
                        or int(actual['forecast_hour']) != calculated['forecast_hour']
                        or int(actual['horizon_hours']) != calculated['horizon_hours']
                        or not math.isclose(float(actual['predicted']), calculated['predicted'], rel_tol=1e-11, abs_tol=1e-9)):
                    raise ValueError('Forecast target/issuance/recursive prediction mismatch')
            expected_metrics, _, _ = evaluate(selected, variable)
            for item in expected_metrics:
                saved = next(r for r in metrics if r['city'] == city and r['variable'] == variable and r['model'] == item['model'])
                if any(not math.isclose(float(saved[k]), item[k], rel_tol=1e-11, abs_tol=1e-9) for k in ('mae', 'rmse', 'bias')):
                    raise ValueError('Updated holdout metrics mismatch')
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
    file_count += verify_issued_forecast(folder.parent / 'forecast_issued_2026_10_18')
    file_count += verify_post_repair(folder.parent / 'post_repair_2026_10_18')
    file_count += verify_refresh(folder.parent / 'refresh_2026_10_18')
    file_count += verify_raw_export(folder.parent / 'raw_export_2026_10_18')
    added,followup_hours,followup_values=verify_followups(folder.parent)
    file_count+=added
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
            'forecast_metrics': len(metrics), 'cd_environments': 2, 'temporary_secrets_remaining': 0,
            'supplementary_descriptive_rows': 96, 'supplementary_ma_metrics': 24,
            'later_model_comparison_rows': len(read_csv(folder.parent / 'refresh_2026_10_18/analysis/later_model/comparison.csv')),
            'week3_confirmed_hours': 20,'followup_target_hours':followup_hours,'followup_comparison_values':followup_values}


if __name__ == '__main__':
    print(json.dumps(verify(ROOT / 'tuan_3/results/integration_2026_10_18')))
