"""Compare registered JSON, projected JSON and projected Parquet on frozen rows."""
from __future__ import annotations

import argparse
from collections import defaultdict
import copy
import io
import json
import math
from pathlib import Path
import re
import statistics

import pyarrow as pa
import pyarrow.parquet as pq

from botocore.exceptions import ClientError
from common import DATABASE, PROFILES, client, digest, query, read_csv, session, write_csv, write_json

DATA_COLUMNS = [('record_id', 'string'), ('city', 'string'), ('latitude', 'double'), ('longitude', 'double'),
    ('timestamp_utc', 'string'), ('timestamp_vn', 'string'), ('temperature_2m', 'double'),
    ('relative_humidity_2m', 'double'), ('surface_pressure', 'double'), ('wind_speed_10m', 'double'),
    ('pm2_5', 'double'), ('pm10', 'double'), ('carbon_monoxide', 'double'), ('nitrogen_dioxide', 'double'),
    ('sulphur_dioxide', 'double'), ('ozone', 'double'), ('us_aqi', 'int'), ('aqi_category', 'string'),
    ('hour', 'int'), ('collected_at', 'string')]


def typed_rows(rows):
    result = []
    for row in rows:
        item = {}
        for name, kind in DATA_COLUMNS:
            value = row[name]
            if value == '':
                item[name] = None
            elif kind == 'double':
                item[name] = float(value)
                if not math.isfinite(item[name]):
                    raise ValueError('Nonfinite source input')
            elif kind == 'int':
                number = float(value)
                if not math.isfinite(number) or not number.is_integer():
                    raise ValueError('Integer input must be finite and integral')
                item[name] = int(number)
            else:
                item[name] = value
        result.append(item)
    return result


def projection(root, years):
    return {'projection.enabled': 'true', 'projection.year.type': 'integer',
            'projection.year.range': f'{min(years)},{max(years)}', 'projection.year.digits': '4',
            'projection.month.type': 'integer', 'projection.month.range': '1,12', 'projection.month.digits': '2',
            'projection.day.type': 'integer', 'projection.day.range': '1,31', 'projection.day.digits': '2',
            'storage.location.template': root + 'year=${year}/month=${month}/day=${day}/'}


def storage(location, parquet):
    return {'Columns': [{'Name': n, 'Type': t} for n, t in DATA_COLUMNS], 'Location': location,
            'InputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat' if parquet else 'org.apache.hadoop.mapred.TextInputFormat',
            'OutputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat' if parquet else 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
            'SerdeInfo': {'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe' if parquet else 'org.openx.data.jsonserde.JsonSerDe'}}


def assert_equal_groups(expected, observed):
    if len(expected) != len(observed):
        raise ValueError('Aggregate row count mismatch')
    for a, b in zip(expected, observed):
        if set(a) != set(b):
            raise ValueError('Aggregate fields mismatch')
        for key in a:
            if key == 'city':
                if a[key] != b[key]:
                    raise ValueError('Aggregate city mismatch')
            elif not math.isclose(float(a[key]), float(b[key]), rel_tol=1e-11, abs_tol=1e-9):
                raise ValueError(f'Aggregate differs: {key}')


def put_immutable(s3, bucket, key, blob):
    try:
        old = s3.get_object(Bucket=bucket, Key=key)['Body'].read()
    except ClientError as error:
        if error.response['Error']['Code'] not in ('NoSuchKey', '404'):
            raise
        s3.put_object(Bucket=bucket, Key=key, Body=blob, ServerSideEncryption='AES256')
    else:
        if digest(old) != digest(blob):
            raise ValueError('Experiment object already exists with different data; choose a new run ID')


def run(profile, snapshot, output, run_id):
    folder = output / profile
    folder.mkdir(parents=True, exist_ok=True)
    rows = read_csv(snapshot / profile / 'raw_all.csv')
    if not rows:
        raise ValueError('Empty benchmark input')
    by_day = defaultdict(list)
    for row in rows:
        by_day[row['year'], row['month'], row['day']].append(row)
    sess = session(profile)
    account = client(sess, 'sts').get_caller_identity()['Account']
    bucket = f'weather-aqi-{account}'
    s3, glue = client(sess, 's3'), client(sess, 'glue')
    prefix = f'week3/experiments/{run_id}/'
    inventory = []
    arrow_types = {'double': pa.float64(), 'int': pa.int32(), 'string': pa.string()}
    schema = pa.schema([(n, arrow_types[t]) for n, t in DATA_COLUMNS])
    for (year, month, day), group in sorted(by_day.items()):
        records = typed_rows(group)
        raw_blob = ('\n'.join(json.dumps(r, ensure_ascii=False, allow_nan=False) for r in records) + '\n').encode('utf-8')
        buffer = io.BytesIO()
        pq.write_table(pa.Table.from_pylist(records, schema=schema), buffer, compression='snappy')
        for format_name, blob, suffix in [('ndjson', raw_blob, 'json'), ('parquet', buffer.getvalue(), 'parquet')]:
            key = f'{prefix}{format_name}/year={year}/month={month}/day={day}/data.{suffix}'
            put_immutable(s3, bucket, key, blob)
            inventory.append({'format': format_name, 'year': year, 'month': month, 'day': day,
                              'records': len(group), 'bytes': len(blob), 'sha256': digest(blob)})
    write_csv(folder / 'storage_inventory.csv', inventory, list(inventory[0]))
    definitions = {}
    years = [int(key[0]) for key in by_day]
    for format_name, parquet, projected in [('registered_json', False, False), ('projected_json', False, True), ('projected_parquet', True, True)]:
        name = f'w3_{run_id}_{format_name}'
        location = f's3://{bucket}/{prefix}{"parquet" if parquet else "ndjson"}/'
        parameters = {'classification': 'parquet' if parquet else 'json', 'week3.run_id': run_id,
                      'week3.input_sha256': digest((snapshot / profile / 'raw_all.csv').read_bytes())}
        if projected:
            parameters.update(projection(location, years))
        definition = {'Name': name, 'TableType': 'EXTERNAL_TABLE', 'StorageDescriptor': storage(location, parquet),
                      'PartitionKeys': [{'Name': k, 'Type': 'string'} for k in ('year', 'month', 'day')], 'Parameters': parameters}
        try:
            old = glue.get_table(DatabaseName=DATABASE, Name=name)['Table']
        except ClientError as error:
            if error.response['Error']['Code'] != 'EntityNotFoundException':
                raise
            glue.create_table(DatabaseName=DATABASE, TableInput=definition)
        else:
            for key in ('TableType', 'StorageDescriptor', 'PartitionKeys', 'Parameters'):
                if key == 'StorageDescriptor':
                    if any(old[key].get(k) != definition[key][k] for k in ('Columns', 'Location', 'InputFormat', 'SerdeInfo')):
                        raise ValueError('Existing experiment table differs')
                elif old.get(key) != definition[key]:
                    raise ValueError('Existing experiment table differs')
        if not projected:
            existing = {tuple(p['Values']) for page in glue.get_paginator('get_partitions').paginate(DatabaseName=DATABASE, TableName=name) for p in page['Partitions']}
            additions = []
            for values in sorted(set(by_day) - existing):
                descriptor = copy.deepcopy(definition['StorageDescriptor'])
                descriptor['Location'] += f'year={values[0]}/month={values[1]}/day={values[2]}/'
                additions.append({'Values': list(values), 'StorageDescriptor': descriptor})
            if additions:
                response = glue.batch_create_partition(DatabaseName=DATABASE, TableName=name, PartitionInputList=additions)
                if response.get('Errors'):
                    raise RuntimeError('Experiment partition registration failed')
        partition_count = sum(len(page['Partitions']) for page in glue.get_paginator('get_partitions').paginate(DatabaseName=DATABASE, TableName=name))
        if projected and partition_count:
            raise ValueError('Projection experiment must not use registered partitions')
        definitions[format_name] = {'name': name, 'projected': projected, 'registered_partitions': partition_count,
                                    'parameters': {k: v.replace(bucket, 'PROJECT_BUCKET') for k, v in parameters.items()}}
    write_json(folder / 'tables.json', definitions)
    selected_day = max(by_day)
    clause = f"year='{selected_day[0]}' AND month='{selected_day[1]}' AND day='{selected_day[2]}'"
    template = 'SELECT city, COUNT(*) AS samples, AVG(us_aqi) AS avg_aqi, AVG(pm2_5) AS avg_pm2_5 FROM {table} WHERE ' + clause + ' GROUP BY city ORDER BY city'
    expected = []
    for city in sorted({r['city'] for r in by_day[selected_day]}):
        group = [r for r in by_day[selected_day] if r['city'] == city]
        expected.append({'city': city, 'samples': len(group), 'avg_aqi': statistics.mean(float(r['us_aqi']) for r in group), 'avg_pm2_5': statistics.mean(float(r['pm2_5']) for r in group)})
    measured = []
    for repeat in range(3):
        # Rotate execution order to reduce one fixed-order warm-cache advantage.
        formats = list(definitions)
        formats = formats[repeat:] + formats[:repeat]
        for format_name in formats:
            sql = template.format(table=definitions[format_name]['name'])
            local_sql = sql.replace(f'w3_{run_id}_', 'w3_RUN_ID_')
            (folder / f'{format_name}.sql').write_text(local_sql + '\n', encoding='utf-8')
            result, observed = query(sess, sql, f's3://{bucket}/athena-results/week3/{run_id}/', f'{format_name}_{repeat+1}', folder / 'queries')
            assert_equal_groups(expected, observed)
            if result['result_reused']:
                raise ValueError('Reused result cannot be a benchmark trial')
            measured.append({'format': format_name, 'trial': repeat + 1, 'selected_date': '-'.join(selected_day),
                             'input_rows': sum(int(r['samples']) for r in expected),
                             **{k: result[k] for k in ('query_id', 'bytes_scanned', 'engine_ms', 'total_ms', 'planning_ms', 'result_reused')}})
    write_csv(folder / 'benchmark.csv', measured, list(measured[0]))
    summary = {kind: {metric: statistics.median(r[metric] for r in measured if r['format'] == kind)
                     for metric in ('bytes_scanned', 'engine_ms', 'total_ms', 'planning_ms')} for kind in definitions}
    write_json(folder / 'summary.json', {'profile': profile, 'input_records': len(rows), 'selected_date': '-'.join(selected_day),
                'selected_records': sum(int(r['samples']) for r in expected), 'result_parity': 'PASS',
                'trial_count': 9, 'medians': summary, 'format_scope': 'Same frozen rows and aggregation, same daily grouping, one object per day; not a production cost forecast',
                'source_sha256': digest((snapshot / profile / 'raw_all.csv').read_bytes()),
                'parquet_scan_change_percent': (summary['projected_parquet']['bytes_scanned'] / summary['projected_json']['bytes_scanned'] - 1) * 100 if summary['projected_json']['bytes_scanned'] else None})
    print(json.dumps({'profile': profile, 'records': len(rows), 'summary': summary, 'parity': 'PASS'}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9_]{1,24}', args.run_id):
        raise ValueError('Use a short lowercase alphanumeric run ID')
    for profile in PROFILES:
        run(profile, args.snapshot, args.output, args.run_id)


if __name__ == '__main__':
    main()
