"""Execute Athena queries through boto3 and preserve their CSV results."""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
import shutil
import time
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]
QUERY_FILES = {
    'avg_aqi_by_city': 'query_avg_aqi_by_city.sql',
    'peak_pollution_hours': 'query_peak_pollution_hours.sql',
    'aqi_category_distribution': 'query_aqi_category_distribution.sql',
    'weather_correlation': 'query_temperature_humidity_correlation.sql',
    'raw_weather_aqi_records': 'query_raw_weather_aqi_records.sql',
}


class AthenaQueryError(RuntimeError):
    pass


class AthenaExporter:
    def __init__(self, athena, s3, database, output_location, timeout=300,
                 clock=time.monotonic, sleep=time.sleep):
        self.athena, self.s3 = athena, s3
        self.database, self.output_location = database, output_location
        self.timeout, self.clock, self.sleep = timeout, clock, sleep

    def execute(self, sql):
        query_id = self.athena.start_query_execution(
            QueryString=sql,
            QueryExecutionContext={'Database': self.database},
            ResultConfiguration={'OutputLocation': self.output_location},
        )['QueryExecutionId']
        deadline = self.clock() + self.timeout
        while True:
            execution = self.athena.get_query_execution(QueryExecutionId=query_id)['QueryExecution']
            state = execution['Status']['State']
            if state == 'SUCCEEDED':
                return query_id, execution
            if state in ('FAILED', 'CANCELLED'):
                raise AthenaQueryError(f'Athena query {query_id} ended with {state}.')
            if self.clock() >= deadline:
                self.athena.stop_query_execution(QueryExecutionId=query_id)
                raise TimeoutError(f'Athena query {query_id} exceeded {self.timeout} seconds.')
            self.sleep(1)

    def csv_bytes(self, query_id, execution):
        uri = urlparse(execution['ResultConfiguration']['OutputLocation'])
        if uri.scheme != 's3' or not uri.netloc or not uri.path:
            raise AthenaQueryError('Athena did not return a valid S3 result location.')
        try:
            response = self.s3.get_object(Bucket=uri.netloc, Key=uri.path.lstrip('/'))
            body = response['Body']
            try:
                return body.read()
            finally:
                body.close()
        except ClientError as error:
            if error.response['Error']['Code'] not in ('AccessDenied', 'NoSuchKey'):
                raise
        # API fallback keeps column positions and SQL NULL as empty fields.
        rows, header, token = [], None, None
        first_page = True
        while True:
            request = {'QueryExecutionId': query_id, 'MaxResults': 1000}
            if token:
                request['NextToken'] = token
            response = self.athena.get_query_results(**request)
            page = response['ResultSet']
            if header is None:
                header = [column['Name'] for column in page['ResultSetMetadata']['ColumnInfo']]
            page_rows = [[cell.get('VarCharValue', '') for cell in row['Data']]
                         for row in page['Rows']]
            if first_page and page_rows and page_rows[0] == header:
                page_rows = page_rows[1:]
            first_page = False
            rows.extend(row + [''] * (len(header) - len(row)) for row in page_rows)
            token = response.get('NextToken')
            if token is None:
                break
        buffer = io.StringIO(newline='')
        writer = csv.writer(buffer, quoting=csv.QUOTE_ALL, lineterminator='\n')
        writer.writerow(header or [])
        writer.writerows(rows)
        return buffer.getvalue().encode('utf-8')

    def export(self, name, sql, destination):
        query_id, execution = self.execute(sql)
        blob = self.csv_bytes(query_id, execution)
        text = blob.decode('utf-8-sig')
        rows = list(csv.DictReader(io.StringIO(text, newline='')))
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix('.csv.tmp')
        temporary.write_bytes(blob)
        temporary.replace(destination)
        statistics = execution.get('Statistics', {})
        return {'name': name, 'query_id': query_id, 'status': 'SUCCEEDED',
                'execution_time_ms': statistics.get('EngineExecutionTimeInMillis', 0),
                'bytes_scanned': statistics.get('DataScannedInBytes', 0),
                'row_count': len(rows), 'rows': rows}


def copy_snapshot(destination, names=None):
    destination = Path(destination).resolve()
    source = (ROOT / 'results' / 'athena_queries').resolve()
    if destination == source:
        raise ValueError('Choose a separate output directory for an offline copy.')
    names = list(names or QUERY_FILES)
    for name in names:
        if name not in QUERY_FILES:
            raise ValueError(f'Unknown query name: {name}')
        if not (source / f'{name}.csv').is_file():
            raise FileNotFoundError(f'Missing saved CSV: {name}')
    destination.mkdir(parents=True, exist_ok=True)
    for name in names:
        shutil.copyfile(source / f'{name}.csv', destination / f'{name}.csv')
    (destination / 'export_manifest.json').write_text(json.dumps({
        'mode': 'saved-snapshot', 'files': [f'{name}.csv' for name in names],
        'description': 'Copy of saved data. No AWS query was executed for this export.'
    }, ensure_ascii=False, indent=2), encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--region', default='us-east-1')
    parser.add_argument('--database', default='weather_aqi_db')
    parser.add_argument('--bucket')
    parser.add_argument('--output', type=Path, default=ROOT / 'results' / 'data_exports')
    parser.add_argument('--timeout', type=int, default=300)
    parser.add_argument('--only', choices=QUERY_FILES)
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args(argv)
    names = [args.only] if args.only else list(QUERY_FILES)
    if args.offline:
        copy_snapshot(args.output, names)
        print('Copied saved CSV snapshot. No new cloud query was executed.')
        return
    session = boto3.Session(region_name=args.region)
    account = session.client('sts').get_caller_identity()['Account']
    bucket = args.bucket or f'weather-aqi-{account}'
    exporter = AthenaExporter(session.client('athena'), session.client('s3'),
                              args.database, f's3://{bucket}/athena-results/', args.timeout)
    results = [exporter.export(name, (ROOT / 'athena' / QUERY_FILES[name]).read_text(encoding='utf-8'),
                               args.output / f'{name}.csv') for name in names]
    (args.output / 'summary_metrics.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    with (args.output / 'query_metrics.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, quoting=csv.QUOTE_ALL)
        writer.writerow(['query_name', 'query_execution_id', 'status', 'result_rows', 'execution_time_ms', 'bytes_scanned'])
        for item in results:
            writer.writerow([item['name'], item['query_id'], item['status'], item['row_count'], item['execution_time_ms'], item['bytes_scanned']])
    print(f'Exported {len(results)} successful query results.')


if __name__ == '__main__':
    main()
