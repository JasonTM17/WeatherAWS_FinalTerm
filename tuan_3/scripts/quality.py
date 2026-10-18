"""Validate real snapshots without deleting repeated collection observations."""
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import statistics

from common import NUMERIC_FIELDS, finite

REQUIRED = {'record_id', 'city', 'latitude', 'longitude', 'timestamp_utc', 'timestamp_vn',
            'temperature_2m', 'relative_humidity_2m', 'surface_pressure', 'wind_speed_10m',
            'pm2_5', 'pm10', 'carbon_monoxide', 'nitrogen_dioxide', 'sulphur_dioxide',
            'ozone', 'us_aqi', 'aqi_category', 'hour', 'collected_at', 'year', 'month', 'day'}
WEEK3_START = datetime(2026, 10, 18, 17, tzinfo=timezone.utc)
WEEK3_END = datetime(2026, 10, 25, 17, tzinfo=timezone.utc)


def instant(value):
    parsed = datetime.fromisoformat(value)
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def inspect_rows(rows):
    if not rows:
        raise ValueError('Empty snapshot cannot establish quality')
    issues, hours = Counter(), defaultdict(list)
    ids = Counter(r.get('record_id') for r in rows)
    issues['duplicate_record_ids'] = sum(n - 1 for n in ids.values() if n > 1)
    weekly = 0
    for row in rows:
        issues['schema_mismatch_rows'] += set(row) != REQUIRED
        issues['missing_numeric_cells'] += sum(row.get(k) is None or row.get(k) == '' for k in NUMERIC_FIELDS)
        issues['invalid_numeric_cells'] += sum(not finite(row.get(k)) and row.get(k) not in (None, '') for k in NUMERIC_FIELDS)
        try:
            utc = instant(row['timestamp_utc'])
            expected = (utc + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            issues['timezone_mismatch_rows'] += row['timestamp_vn'] != expected
            issues['partition_mismatch_rows'] += (str(row['year']), str(row['month']).zfill(2), str(row['day']).zfill(2), int(row['hour'])) != (utc.strftime('%Y'), utc.strftime('%m'), utc.strftime('%d'), utc.hour)
            acquired = instant(row['collected_at'])
            issues['collection_before_observation_rows'] += acquired < utc
            hours[row['city'], utc.replace(minute=0, second=0, microsecond=0)].append(row)
            weekly += WEEK3_START <= utc < WEEK3_END
        except (ValueError, TypeError, KeyError):
            issues['invalid_time_rows'] += 1
    grouped = []
    for (city, utc), group in sorted(hours.items()):
        grouped.append({'city': city, 'hour_utc': utc.isoformat(), 'sample_count': len(group),
                        'avg_aqi': statistics.mean(float(r['us_aqi']) for r in group if finite(r.get('us_aqi'))) if any(finite(r.get('us_aqi')) for r in group) else '',
                        'avg_pm2_5': statistics.mean(float(r['pm2_5']) for r in group if finite(r.get('pm2_5'))) if any(finite(r.get('pm2_5')) for r in group) else ''})
    summary = {'records': len(rows), 'week3_calendar_records': weekly, 'city_hour_groups': len(hours),
               'multiple_collection_city_hours': sum(len(g) > 1 for g in hours.values()),
               'issues': dict(issues), 'first_utc': min(r['timestamp_utc'] for r in rows),
               'last_utc': max(r['timestamp_utc'] for r in rows)}
    return summary, grouped
