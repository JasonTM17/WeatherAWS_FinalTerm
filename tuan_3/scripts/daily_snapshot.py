"""Build a dated report from archived S3 records without rewriting prior snapshots."""
import argparse
from collections import Counter
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from common import ROOT, PROFILES, digest, ndjson_rows, read_csv, write_csv, write_json
from forecast import CITIES, LABELS
from quality import instant, inspect_rows
from reconcile_analysis import VARIABLES, descriptive, hourly_rows

VIETNAM = timezone(timedelta(hours=7))


def day_window(day):
    start = datetime.combine(date.fromisoformat(day), datetime.min.time(), VIETNAM)
    return start.astimezone(timezone.utc), (start + timedelta(days=1)).astimezone(timezone.utc)


def select_day(rows, day, captured_at):
    start, end = day_window(day)
    captured = instant(captured_at)
    if captured < start:
        raise ValueError('Capture precedes the requested local day')
    return [r for r in rows if start <= instant(r['timestamp_utc']) < min(end, captured)]


def preserve_previous(previous, current):
    canonical = lambda row: json.dumps(row, sort_keys=True, ensure_ascii=False)
    old, new = Counter(map(canonical, previous)), Counter(map(canonical, current))
    if old - new:
        raise ValueError('Current snapshot does not preserve every previous record')
    return len(previous)


def summarize_daily(raw, completed_before=None):
    if not raw:
        return {'records': 0, 'status': 'NO_RECORDS_IN_DAY', 'issues': None, 'city_hour_groups': 0}, [], []
    quality, _ = inspect_rows(raw)
    completed = raw if completed_before is None else [r for r in raw if instant(r['timestamp_utc']) < instant(completed_before)]
    hours = hourly_rows(completed)
    stats = []
    for scope, source in (('raw', raw), ('city_hour', hours)):
        for city in CITIES:
            selected = [r for r in source if r['city'] == city]
            if not selected:
                continue
            for variable, (_, unit) in VARIABLES.items():
                stats.append({'scope': scope, 'city': city, 'variable': variable, 'unit': unit,
                              **descriptive([r[variable] for r in selected])})
    return {'status': 'OBSERVED_DAY_SUBSET', **quality}, hours, stats


def plot_day(folder, day):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharex=True)
    for row, profile in enumerate(PROFILES):
        hourly = read_csv(folder / 'daily' / profile / 'hourly_city.csv')
        for col, (variable, label) in enumerate((('us_aqi', 'US AQI'), ('pm2_5', 'PM2.5 (µg/m³)'))):
            ax = axes[row, col]
            for city, color in zip(CITIES, ('#2563eb', '#db2777', '#059669')):
                selected = [r for r in hourly if r['city'] == city]
                x = [instant(r['timestamp_utc']).astimezone(VIETNAM).hour for r in selected]
                ax.plot(x, [float(r[variable]) for r in selected], marker='o', markersize=3,
                        color=color, label=LABELS[city])
            ax.set(title=PROFILES[profile], ylabel=label, xlabel='Giờ ngày báo cáo (UTC+7)')
            ax.grid(alpha=.2)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=3)
    fig.suptitle(f'Thời tiết và chất lượng không khí ngày {day}\nChuỗi mô hình lấy qua Lambda, trung bình từng đô thị–giờ')
    fig.tight_layout(rect=(0, .05, 1, .93))
    fig.savefig(folder / 'daily_aqi_pm25.png', dpi=180)
    plt.close(fig)


def build(snapshot, collection, release, previous, output, day):
    output.mkdir(parents=True, exist_ok=False)
    shutil.copytree(snapshot, output / 'snapshot')
    shutil.copytree(collection, output / 'collection')
    shutil.copytree(release, output / 'release')
    summary = {'day_local': day, 'timezone': 'UTC+7', 'day_start_utc': day_window(day)[0].isoformat(),
               'day_end_exclusive_utc': day_window(day)[1].isoformat(), 'profiles': {},
               'source_semantics': 'Authenticated Lambda historical-model backfill saved on S3, exported by conditional GET; not recovered scheduled runs',
               'script_sha256_lf': digest(Path(__file__).read_bytes().replace(b'\r\n', b'\n'))}
    for profile in PROFILES:
        base = output / 'snapshot' / profile
        raw = read_csv(base / 'raw_all.csv')
        before = read_csv(previous / profile / 'raw_all.csv')
        snap = json.loads((base / 'snapshot.json').read_text(encoding='utf-8'))
        preserved = preserve_previous(before, raw)
        today = select_day(raw, day, snap['captured_at'])
        analysis_cutoff = instant(snap['captured_at']).replace(minute=0, second=0, microsecond=0)
        quality, hours, stats = summarize_daily(today, analysis_cutoff.isoformat())
        if not today:
            raise ValueError('No real S3 data for the requested day; do not fabricate a daily analysis')
        proof = json.loads((output / 'collection' / f'{profile}.json').read_text(encoding='utf-8'))
        manual_keys = {r['s3_key'] for r in proof['saved_files']}
        provenance = []
        for item in read_csv(base / 'object_inventory.csv'):
            blob = (base / 'objects' / item['key']).read_bytes()
            if digest(blob) != item['sha256']:
                raise ValueError('Original object digest mismatch')
            for row in select_day(ndjson_rows(blob), day, snap['captured_at']):
                provenance.append({'record_id': row['record_id'], 'object_key': item['key'],
                                   'collection_mode': 'manual_model_backfill' if item['key'] in manual_keys else 'other_S3_object'})
        daily = output / 'daily' / profile
        write_csv(daily / 'raw_today.csv', today, list(raw[0]))
        write_csv(daily / 'record_sources.csv', provenance, ['record_id', 'object_key', 'collection_mode'])
        write_csv(daily / 'hourly_city.csv', hours, list(hours[0]))
        write_csv(daily / 'descriptive.csv', stats, list(stats[0]))
        write_json(daily / 'quality.json', quality)
        summary['profiles'][profile] = {'student': PROFILES[profile], 'captured_at_utc': snap['captured_at'],
            'all_records': len(raw), 'previous_snapshot_records_preserved': preserved,
            'new_records_since_previous_export': len(raw) - preserved,
            'day_records': len(today), 'day_city_hour_groups': quality['city_hour_groups'],
            'completed_city_hour_groups': len(hours), 'analysis_completed_before_utc': analysis_cutoff.isoformat(),
            'completed_day_records': sum(instant(r['timestamp_utc']) < analysis_cutoff for r in today),
            'current_hour_records': sum(instant(r['timestamp_utc']) >= analysis_cutoff for r in today),
            'day_first_utc': min(r['timestamp_utc'] for r in today), 'day_last_utc': max(r['timestamp_utc'] for r in today),
            'day_distinct_hours': len({instant(r['timestamp_utc']).replace(minute=0, second=0, microsecond=0) for r in today}),
            'manual_backfill_day_records': sum(r['collection_mode'] == 'manual_model_backfill' for r in provenance),
            'original_objects': len(read_csv(base / 'object_inventory.csv')),
            'quality_issue_counts': quality['issues'], 'lambda_matches_new_release': snap['lambda']['matches_reviewed_release_package']}
    plot_day(output, day)
    write_json(output / 'summary.json', summary)
    write_json(output / 'manifest.json', {'files': [
        {'path': p.relative_to(output).as_posix(), 'sha256': digest(p.read_bytes()), 'bytes': p.stat().st_size}
        for p in sorted(output.rglob('*')) if p.is_file()]})
    print(json.dumps(summary['profiles']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--collection', type=Path, required=True)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--previous', type=Path, default=ROOT / 'tuan_3/results/raw_export_2026_10_18/snapshot')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--date', required=True)
    args = parser.parse_args()
    build(args.snapshot, args.collection, args.release, args.previous, args.output, args.date)
