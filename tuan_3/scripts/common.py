"""Shared bounded I/O for Week 3 evidence; no credentials in output."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from pathlib import Path
import time

import boto3
from botocore.config import Config

ROOT = Path(__file__).resolve().parents[2]
PROFILES = {'default': 'Sinh viên Tiến Sơn', 'quyen': 'Sinh viên Ngọc Quyên'}
FUNCTION = 'WeatherCollectorLambda'
DATABASE = 'weather_aqi_db'
OPTIONS = Config(connect_timeout=10, read_timeout=45, retries={'total_max_attempts': 2})
NUMERIC_FIELDS = ('latitude', 'longitude', 'temperature_2m', 'relative_humidity_2m',
                  'surface_pressure', 'wind_speed_10m', 'pm2_5', 'pm10',
                  'carbon_monoxide', 'nitrogen_dioxide', 'sulphur_dioxide', 'ozone', 'us_aqi', 'hour')


def session(profile):
    return boto3.Session(profile_name=profile, region_name='us-east-1')


def client(sess, service):
    return sess.client(service, config=OPTIONS)


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False, default=str) + '\n', encoding='utf-8')


def write_csv(path, rows, fields):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator='\n', extrasaction='raise')
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle, strict=True)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError('Invalid CSV header')
        rows = list(reader)
        if any(None in r or any(v is None for v in r.values()) for r in rows):
            raise ValueError('CSV width mismatch')
        return rows


def finite(value):
    if value is None or value == '':
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def query(sess, sql, output_uri, name, folder, timeout=180):
    athena = client(sess, 'athena')
    qid = athena.start_query_execution(QueryString=sql,
        QueryExecutionContext={'Database': DATABASE},
        ResultConfiguration={'OutputLocation': output_uri},
        ResultReuseConfiguration={'ResultReuseByAgeConfiguration': {'Enabled': False}})['QueryExecutionId']
    folder = Path(folder)
    write_json(folder / f'{name}.pending.json', {'query_id': qid})
    deadline = time.monotonic() + timeout
    while True:
        execution = athena.get_query_execution(QueryExecutionId=qid)['QueryExecution']
        state = execution['Status']['State']
        if state in ('SUCCEEDED', 'FAILED', 'CANCELLED'):
            break
        if time.monotonic() >= deadline:
            athena.stop_query_execution(QueryExecutionId=qid)
            raise TimeoutError(f'Athena timeout; inspect query ID {qid}')
        time.sleep(1)
    stats = execution.get('Statistics', {})
    result = {'name': name, 'query_id': qid, 'status': state,
              'bytes_scanned': stats.get('DataScannedInBytes', 0),
              'engine_ms': stats.get('EngineExecutionTimeInMillis', 0),
              'total_ms': stats.get('TotalExecutionTimeInMillis', 0),
              'planning_ms': stats.get('QueryPlanningTimeInMillis', 0),
              'result_reused': stats.get('ResultReuseInformation', {}).get('ReusedPreviousResult', False)}
    write_json(folder / f'{name}.json', result)
    if state != 'SUCCEEDED':
        raise RuntimeError(f'Athena {state}; inspect query ID {qid} in AWS')
    data, header = [], None
    for page in athena.get_paginator('get_query_results').paginate(QueryExecutionId=qid):
        result_set = page['ResultSet']
        if header is None:
            header = [c['Name'] for c in result_set['ResultSetMetadata']['ColumnInfo']]
        for row in result_set.get('Rows', []):
            values = [c.get('VarCharValue', '') for c in row['Data']]
            if not data and values == header:
                continue
            data.append(dict(zip(header, values + [''] * (len(header) - len(values)))))
    if header:
        write_csv(folder / f'{name}.csv', data, header)
    (folder / f'{name}.pending.json').unlink()
    return result, data


def ndjson_rows(blob):
    rows = [json.loads(line) for line in blob.decode('utf-8').splitlines() if line.strip()]
    if not rows or any(not isinstance(r, dict) for r in rows):
        raise ValueError('Expected nonempty NDJSON records')
    return rows


def csv_blob(rows, fields):
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode('utf-8')
