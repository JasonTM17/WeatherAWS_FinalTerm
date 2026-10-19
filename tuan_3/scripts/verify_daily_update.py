"""Offline source reconciliation for the 19 October AWS and forecast evidence."""
import base64
from collections import Counter
from datetime import datetime, timedelta
import json
import math

from common import ROOT, digest, ndjson_rows, read_csv
from daily_snapshot import day_window, preserve_previous, select_day, summarize_daily
from forecast_followup import summarize
from forecast import CITIES
from quality import inspect_rows, instant
from reconcile_analysis import partial_comparison


def equal_table(actual, expected):
    if len(actual) != len(expected):
        raise ValueError('Derived table row count differs')
    for observed, calculated in zip(actual, expected):
        if set(observed) != set(calculated):
            raise ValueError('Derived table schema differs')
        for key, value in calculated.items():
            if value is None:
                if observed[key] != '':
                    raise ValueError('Missing value was imputed')
            elif isinstance(value, (int, float)):
                if not math.isclose(float(observed[key]), value, rel_tol=1e-11, abs_tol=1e-9):
                    raise ValueError('Derived numeric value differs')
            elif observed[key] != str(value):
                raise ValueError('Derived identifier differs')


def verify_daily(root, manifest_check):
    folder = root / 'daily_update_2026_10_19'
    count = manifest_check(folder)
    summary = json.loads((folder / 'summary.json').read_text(encoding='utf-8'))
    day = summary['day_local']
    start, end = day_window(day)
    if (summary['day_start_utc'], summary['day_end_exclusive_utc']) != (start.isoformat(), end.isoformat()):
        raise ValueError('Local reporting-day boundaries differ')
    for profile, target in (('default', 'tien-son'), ('quyen', 'ngoc-quyen')):
        base = folder / 'snapshot' / profile
        raw = read_csv(base / 'raw_all.csv')
        snap = json.loads((base / 'snapshot.json').read_text(encoding='utf-8'))
        quality, _ = inspect_rows(raw)
        if any(snap[key] != quality[key] for key in quality) or any(quality['issues'].values()):
            raise ValueError('Full raw quality mismatch')
        flattened = []
        objects = {}
        for item in read_csv(base / 'object_inventory.csv'):
            path = (base / 'objects' / item['key']).resolve()
            if not path.is_relative_to((base / 'objects').resolve()):
                raise ValueError('Archived object escapes snapshot')
            blob = path.read_bytes()
            rows = ndjson_rows(blob)
            if digest(blob) != item['sha256'] or len(blob) != int(item['bytes']) or len(rows) != int(item['records']):
                raise ValueError('Archived S3 object differs from inventory')
            objects[item['key']] = rows
            flattened.extend({k: '' if v is None else str(v) for k, v in row.items()} for row in rows)
        if flattened != raw or len(objects) != len(list((base / 'objects').rglob('*.json'))):
            raise ValueError('Full CSV differs from original S3 objects')
        previous = read_csv(root / 'raw_export_2026_10_18/snapshot' / profile / 'raw_all.csv')
        preserved = preserve_previous(previous, raw)
        observed = summary['profiles'][profile]
        today = select_day(raw, day, snap['captured_at'])
        if today != read_csv(folder / 'daily' / profile / 'raw_today.csv'):
            raise ValueError('Daily raw selection differs')
        daily_quality, hours, stats = summarize_daily(today, observed['analysis_completed_before_utc'])
        analysis_cutoff = instant(snap['captured_at']).replace(minute=0, second=0, microsecond=0)
        if instant(observed['analysis_completed_before_utc']) != analysis_cutoff:
            raise ValueError('Completed-hour cutoff differs from actual capture')
        if daily_quality != json.loads((folder / 'daily' / profile / 'quality.json').read_text(encoding='utf-8')):
            raise ValueError('Daily quality differs')
        equal_table(read_csv(folder / 'daily' / profile / 'hourly_city.csv'), hours)
        equal_table(read_csv(folder / 'daily' / profile / 'descriptive.csv'), stats)
        for key, value in {'all_records': len(raw), 'previous_snapshot_records_preserved': preserved,
                           'day_records': len(today), 'completed_city_hour_groups': len(hours),
                           'completed_day_records': sum(instant(r['timestamp_utc']) < analysis_cutoff for r in today),
                           'current_hour_records': sum(instant(r['timestamp_utc']) >= analysis_cutoff for r in today),
                           'original_objects': len(objects)}.items():
            if observed[key] != value:
                raise ValueError('Daily headline count differs')
        sources = read_csv(folder / 'daily' / profile / 'record_sources.csv')
        if Counter(r['record_id'] for r in sources) != Counter(r['record_id'] for r in today):
            raise ValueError('Daily record provenance coverage differs')
        proof = json.loads((folder / 'collection' / f'{profile}.json').read_text(encoding='utf-8'))
        if (proof['status'] != 'PASS' or proof['mode'] != 'manual_model_backfill' or proof['alerts_sent'] != 0
                or proof['failed_cities'] or proof['records_collected'] != proof['backfill_hours'] * 3):
            raise ValueError('Backfill result is incomplete or raised historical alerts')
        keys = {item['s3_key'] for item in proof['saved_files']}
        stored = [r for key in keys for r in objects[key]]
        if len(stored) != proof['records_collected'] or len(keys) != len(proof['saved_files']):
            raise ValueError('Lambda result disagrees with S3')
        expected_hours = proof['backfill_hours']
        requested_start, requested_end = map(datetime.fromisoformat, (proof['requested_window_start_utc'], proof['requested_window_end_exclusive_utc']))
        if {r['city'] for r in stored} != set(CITIES):
            raise ValueError('Backfill city coverage differs')
        expected_times = [requested_start + timedelta(hours=i) for i in range(expected_hours)]
        for city in {r['city'] for r in stored}:
            times = sorted(datetime.fromisoformat(r['timestamp_utc']).replace(tzinfo=requested_start.tzinfo) for r in stored if r['city'] == city)
            if times != expected_times or requested_end != requested_start + timedelta(hours=expected_hours):
                raise ValueError('Backfill requested-hour coverage differs')
        for item in sources:
            if item['object_key'] not in objects or item['record_id'] not in {r['record_id'] for r in objects[item['object_key']]}:
                raise ValueError('Record provenance points to another S3 object')
            if item['collection_mode'] != ('manual_model_backfill' if item['object_key'] in keys else 'other_S3_object'):
                raise ValueError('Backfill incorrectly labeled as another collection')
        release = json.loads((folder / 'release' / f'{target}.json').read_text(encoding='utf-8'))
        if (release['status'] != 'PASS' or not release['configuration_unchanged'] or release['final_aws_readback'] != 'PASS'
                or release['commit'] != proof['source_commit'] or release['requested_package_sha256'] != release['deployed_package_sha256']
                or release['deployed_package_sha256'] != base64.b64decode(snap['lambda']['code_sha256']).hex()
                or not snap['lambda']['matches_reviewed_release_package'] or release['thresholds_schedule_environment_changed']):
            raise ValueError('New release identity/configuration proof differs')
    forecast = root / 'forecast_followup_2026_10_19'
    count += manifest_check(forecast)
    provenance = json.loads((forecast / 'provenance.json').read_text(encoding='utf-8'))
    issued_path = ROOT / provenance['issued_path']
    if not issued_path.resolve().is_relative_to(ROOT) or digest(issued_path.read_bytes()) != provenance['issued_sha256']:
        raise ValueError('Original issued forecast changed')
    issued, history = read_csv(issued_path), read_csv(forecast / 'history.csv')
    cutoff = datetime.fromisoformat(provenance['cutoff_exclusive_utc'])
    for source in provenance['sources']:
        payload = json.loads((forecast / 'model_source' / f"{source['city']}_api.json").read_text(encoding='utf-8'))
        rows = [r for r in history if r['city'] == source['city']]
        times = {datetime.fromisoformat(t).replace(tzinfo=cutoff.tzinfo).isoformat(): i for i, t in enumerate(payload['hourly']['time'])}
        if payload['utc_offset_seconds'] != 0 or len(rows) != source['retained_hours']:
            raise ValueError('Model source scope differs')
        for row in rows:
            if datetime.fromisoformat(row['timestamp_utc']) >= cutoff:
                raise ValueError('Uncompleted model hour included')
            i = times[row['timestamp_utc']]
            if any(float(row[k]) != float(payload['hourly'][k][i]) for k in ('us_aqi', 'pm2_5')):
                raise ValueError('Model history differs from archived response')
    expected = partial_comparison(issued, history, cutoff)
    equal_table(read_csv(forecast / 'comparison.csv'), expected)
    equal_table(read_csv(forecast / 'comparison_metrics.csv'), summarize(issued, expected))
    if len(expected) != 144 or len({r['timestamp_utc'] for r in expected}) != 24 or provenance['matched_values'] != 144 or provenance['matched_target_hours'] != 24:
        raise ValueError('Full issued-forecast horizon not covered')
    return count, {'daily_local_date': day, 'daily_records': {p: v['day_records'] for p, v in summary['profiles'].items()},
                   'all_records': {p: v['all_records'] for p, v in summary['profiles'].items()},
                   'target_hours': len({r['timestamp_utc'] for r in expected}), 'comparison_values': len(expected)}
