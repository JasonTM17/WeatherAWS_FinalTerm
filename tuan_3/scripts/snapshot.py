"""Read actual Lambda/S3/CloudWatch state into a new isolated snapshot."""
import argparse
import base64
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess

from common import ROOT, PROFILES, FUNCTION, client, digest, ndjson_rows, session, write_csv, write_json
from quality import inspect_rows


def reviewed_release(profile, folder):
    target = {'default': 'tien-son', 'quyen': 'ngoc-quyen'}[profile]
    path = Path(folder) / f'{target}.json'
    if not path.exists():
        return None
    proof = json.loads(path.read_text(encoding='utf-8'))
    if proof.get('status') != 'PASS' or proof.get('target') != target or proof.get('final_aws_readback') != 'PASS':
        raise ValueError('Release baseline must contain a verified proof for the selected environment')
    digest_bytes = bytes.fromhex(proof['deployed_package_sha256'])
    if len(digest_bytes) != 32:
        raise ValueError('Invalid release package SHA-256')
    return {'commit': proof['commit'], 'code_sha256': base64.b64encode(digest_bytes).decode()}


def result_counts(entries):
    return {'recent_result_log_entries': len(entries),
            'recent_success_log_results': sum(r['collection_status'] == 'complete' and r['failed_cities'] == 0 for r in entries),
            'recent_partial_log_results': sum(r['collection_status'] == 'partial' for r in entries)}


def archive_source(folder, key, blob):
    """Keep exact S3 bytes beneath the selected snapshot, without unsafe keys."""
    parts = key.split('/')
    if (not key.startswith('raw/') or not key.endswith('.json')
            or any(part in ('', '.', '..') or '\\' in part or ':' in part for part in parts)):
        raise ValueError('Unsafe raw object path')
    target = folder / 'objects' / key
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as handle:
        handle.write(blob)


def collect(profile, folder, proof_folder=ROOT / 'tuan_3/results/cd_2026_10_18', archive_objects=False):
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
        if archive_objects:
            archive_source(folder, item['Key'], blob)
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
    baseline = reviewed_release(profile, proof_folder)
    expected = baseline['code_sha256'] if baseline else None
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
                    'lambda': {'state': config['State'], 'update': config['LastUpdateStatus'], 'code_sha256': config['CodeSha256'], 'reviewed_release_commit': baseline['commit'] if baseline else None, 'matches_reviewed_release_package': expected == config['CodeSha256'] if expected else None},
                    'rules': rules, **result_counts(successful), 'snapshot_semantics': 'All raw objects listed once; conditional GET protects each ETag; not an atomic multi-object AWS snapshot'})
    write_json(folder / 'snapshot.json', summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--release-proof', type=Path, default=ROOT / 'tuan_3/results/cd_2026_10_18')
    parser.add_argument('--archive-source', action='store_true', help='Retain each original NDJSON object byte for byte alongside the CSV')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a new output directory; snapshots are immutable')
    args.output.mkdir(parents=True)
    for profile in PROFILES:
        result = collect(profile, args.output / profile, args.release_proof, args.archive_source)
        print(json.dumps({'profile': profile, 'records': result['records'], 'week3_calendar_records': result['week3_calendar_records'], 'recent_collections': result['recent_success_log_results'], 'lambda_matches': result['lambda']['matches_reviewed_release_package']}), flush=True)


if __name__ == '__main__':
    main()
