"""Read actual Lambda/S3/CloudWatch state into a new isolated snapshot."""
import argparse
from datetime import datetime, timedelta, timezone
import json
import subprocess

from common import ROOT, PROFILES, FUNCTION, client, digest, ndjson_rows, session, write_csv, write_json
from quality import inspect_rows


def collect(profile, folder):
    sess = session(profile)
    account = client(sess, 'sts').get_caller_identity()['Account']
    lamb = client(sess, 'lambda')
    config = lamb.get_function_configuration(FunctionName=FUNCTION)
    bucket = config['Environment']['Variables']['S3_BUCKET_NAME']
    assert bucket == f'weather-aqi-{account}' and config['FunctionArn'].split(':')[4] == account
    s3 = client(sess, 's3')
    files = [obj for page in s3.get_paginator('list_objects_v2').paginate(Bucket=bucket, Prefix='raw/') for obj in page.get('Contents', []) if obj['Key'].endswith('.json')]
    rows, inventory = [], []
    folder.mkdir(parents=True, exist_ok=False)
    for item in sorted(files, key=lambda r: r['Key']):
        response = s3.get_object(Bucket=bucket, Key=item['Key'], IfMatch=item['ETag'])
        blob = response['Body'].read()
        records = ndjson_rows(blob)
        rows.extend(records)
        inventory.append({'key': item['Key'], 'records': len(records), 'bytes': len(blob), 'sha256': digest(blob), 'last_modified': item['LastModified'].isoformat()})
    if not rows:
        raise ValueError('No raw records')
    fields = list(rows[0])
    for row in rows:
        if set(row) != set(fields):
            raise ValueError('Source schema drift; inspect source objects before export')
    write_csv(folder / 'raw_all.csv', rows, fields)
    summary, grouped = inspect_rows(rows)
    write_csv(folder / 'hourly_city.csv', grouped, list(grouped[0]))
    write_csv(folder / 'quality.csv', [{'check': k, 'count': v} for k, v in summary['issues'].items()], ['check', 'count'])
    write_csv(folder / 'object_inventory.csv', inventory, list(inventory[0]))
    before = ROOT / 'output/lambda_release_2026_10_16' / profile / 'update-request.json'
    expected = json.loads(before.read_text())['code_sha256'] if before.exists() else None
    events = client(sess, 'events')
    rules = []
    for name in events.list_rule_names_by_target(TargetArn=config['FunctionArn']).get('RuleNames', []):
        rule = events.describe_rule(Name=name)
        targets = events.list_targets_by_rule(Rule=name)['Targets']
        rules.append({'name': name, 'state': rule['State'], 'schedule': rule.get('ScheduleExpression'), 'matching_targets': sum(t['Arn'] == config['FunctionArn'] for t in targets)})
    start = datetime.now(timezone.utc) - timedelta(hours=24)
    logs = client(sess, 'logs')
    successful = []
    for page in logs.get_paginator('filter_log_events').paginate(logGroupName=f'/aws/lambda/{FUNCTION}', startTime=int(start.timestamp()*1000), filterPattern='"[INFO] Result:"'):
        for entry in page.get('events', []):
            try:
                result = json.loads(entry['message'].split('[INFO] Result: ', 1)[1])
            except (IndexError, ValueError):
                continue
            successful.append({'timestamp_utc': datetime.fromtimestamp(entry['timestamp']/1000, timezone.utc).isoformat(), 'collection_status': result.get('collection_status'), 'records_collected': result.get('records_collected'), 'alerts_sent': result.get('alerts_sent'), 'failed_cities': len(result.get('failed_cities', []))})
    write_csv(folder / 'recent_collections.csv', successful, ['timestamp_utc', 'collection_status', 'records_collected', 'alerts_sent', 'failed_cities'])
    summary.update({'profile': profile, 'student': PROFILES[profile], 'captured_at': datetime.now(timezone.utc).isoformat(),
                    'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                    'lambda': {'state': config['State'], 'update': config['LastUpdateStatus'], 'code_sha256': config['CodeSha256'], 'matches_reviewed_release_package': expected == config['CodeSha256'] if expected else None},
                    'rules': rules, 'recent_success_log_results': len(successful), 'snapshot_semantics': 'All raw objects listed once; conditional GET protects each ETag; not an atomic multi-object AWS snapshot'})
    write_json(folder / 'snapshot.json', summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=__import__('pathlib').Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a new output directory; snapshots are immutable')
    args.output.mkdir(parents=True)
    for profile in PROFILES:
        result = collect(profile, args.output / profile)
        print(json.dumps({'profile': profile, 'records': result['records'], 'week3_calendar_records': result['week3_calendar_records'], 'recent_collections': result['recent_success_log_results'], 'lambda_matches': result['lambda']['matches_reviewed_release_package']}), flush=True)


if __name__ == '__main__':
    main()
