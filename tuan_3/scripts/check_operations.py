"""Read bounded operation logs and reconcile each result with S3 and alert rules."""
import argparse
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path

from common import FUNCTION, PROFILES, client, digest, ndjson_rows, session, write_csv, write_json
from snapshot import reviewed_release
from quality import REQUIRED


def expected_alerts(records, aqi, pm25):
    if not math.isfinite(aqi) or not math.isfinite(pm25):
        raise ValueError('Nonfinite alert threshold')
    return sum(float(record['us_aqi']) >= aqi or float(record['pm2_5']) >= pm25 for record in records)


def policy_allows(policy, rule_arn):
    for statement in policy.get('Statement', []):
        principal = statement.get('Principal', {})
        condition = statement.get('Condition', {})
        actions = statement.get('Action', [])
        if isinstance(actions, str):
            actions = [actions]
        if (statement.get('Effect') == 'Allow' and isinstance(principal, dict)
                and principal.get('Service') == 'events.amazonaws.com' and 'lambda:InvokeFunction' in actions
                and any(values.get('AWS:SourceArn') == rule_arn for values in condition.values() if isinstance(values, dict))):
            return True
    return False


def saved_object(descriptor):
    if not isinstance(descriptor, dict):
        raise ValueError('Expected Lambda saved_files descriptor')
    key, count = descriptor.get('s3_key'), descriptor.get('count')
    if (not isinstance(key, str) or not key.startswith('raw/year=') or '..' in key
            or not key.endswith('.json') or type(count) is not int or count < 1):
        raise ValueError('Unexpected S3 path/count in saved_files descriptor')
    return key, count


def run(profile, output, start, end, proofs):
    sess = session(profile)
    account = client(sess, 'sts').get_caller_identity()['Account']
    lamb = client(sess, 'lambda')
    config = lamb.get_function_configuration(FunctionName=FUNCTION)
    bucket = config['Environment']['Variables']['S3_BUCKET_NAME']
    if bucket != f'weather-aqi-{account}' or config['FunctionArn'].split(':')[4] != account:
        raise ValueError('Authenticated environment and collection resources differ')
    baseline = reviewed_release(profile, proofs)
    events = client(sess, 'events')
    rule = events.describe_rule(Name='WeatherCollectionSchedule')
    targets = events.list_targets_by_rule(Rule='WeatherCollectionSchedule')['Targets']
    policy = json.loads(lamb.get_policy(FunctionName=FUNCTION)['Policy'])
    binding = {'state': rule['State'], 'schedule': rule.get('ScheduleExpression'),
               'matching_targets': sum(t['Arn'] == config['FunctionArn'] for t in targets),
               'source_rule_permission': policy_allows(policy, rule['Arn'])}
    # Only nonsecret rule thresholds are retained; the complete secret is never written or printed.
    secret = client(sess, 'secretsmanager').get_secret_value(SecretId=config['Environment']['Variables']['SECRET_NAME'])
    settings = json.loads(secret['SecretString'])
    aqi = int(settings.get('aqi_threshold_us_aqi', 100))
    pm25 = float(settings.get('aqi_threshold_pm25', 35.5))
    logs, s3 = client(sess, 'logs'), client(sess, 's3')
    result_rows, objects, raw_objects = [], [], {}
    token = None
    for page in range(5):
        request = {'logGroupName': f'/aws/lambda/{FUNCTION}', 'startTime': int(start.timestamp()*1000),
                   'endTime': int(end.timestamp()*1000), 'filterPattern': '"[INFO] Result:"', 'limit': 100}
        if token:
            request['nextToken'] = token
        response = logs.filter_log_events(**request)
        for entry in response.get('events', []):
            result = json.loads(entry['message'].split('[INFO] Result: ', 1)[1])
            if result.get('bucket') != bucket:
                raise ValueError('Result log bucket differs from selected environment')
            records = []
            keys = result['saved_files']
            if not isinstance(keys, list) or not 1 <= len(keys) <= 3:
                raise ValueError('Unexpected object count in result; inspect privately')
            for descriptor in keys:
                key, expected_count = saved_object(descriptor)
                raw = s3.get_object(Bucket=bucket, Key=key)['Body'].read()
                rows = ndjson_rows(raw)
                if len(rows) != expected_count or any(set(row) != REQUIRED for row in rows):
                    raise ValueError('S3 row count/schema differs from collection contract')
                raw_objects[key] = rows
                records.extend(rows)
                objects.append({'key': key, 'records': len(rows), 'sha256': digest(raw)})
            number = expected_alerts(records, aqi, pm25)
            stamp = datetime.fromtimestamp(entry['timestamp']/1000, timezone.utc)
            result_rows.append({'timestamp_utc': stamp.isoformat(), 'collection_status': result['collection_status'],
                'reported_records': result['records_collected'], 's3_verified_records': len(records),
                'cities': len({r['city'] for r in records}), 'failed_cities': len(result['failed_cities']),
                'expected_alerts': number, 'reported_alerts_sent': result['alerts_sent'],
                'record_count_matches': result['records_collected'] == len(records),
                'alert_count_matches_current_thresholds': result['alerts_sent'] == number,
                'after_current_lambda_update': stamp >= datetime.fromisoformat(config['LastModified'])})
        token = response.get('nextToken')
        if not token:
            break
    else:
        raise RuntimeError('Log window exceeds bounded pagination; narrow the requested window')
    fields = ['timestamp_utc', 'collection_status', 'reported_records', 's3_verified_records', 'cities',
              'failed_cities', 'expected_alerts', 'reported_alerts_sent', 'record_count_matches',
              'alert_count_matches_current_thresholds', 'after_current_lambda_update']
    write_csv(output / profile / 'collection_checks.csv', result_rows, fields)
    raw_rows = [row for key in sorted(raw_objects) for row in raw_objects[key]]
    write_csv(output / profile / 'raw_verified.csv', raw_rows, list(raw_rows[0]) if raw_rows else sorted(REQUIRED))
    write_json(output / profile / 'verification.json', {'student': PROFILES[profile],
        'window_start': start.isoformat(), 'window_end': end.isoformat(), 'rule': binding,
        'lambda_updated_at': config['LastModified'], 'release_baseline_commit': baseline['commit'] if baseline else None,
        'package_matches_reviewed_release': config['CodeSha256'] == baseline['code_sha256'] if baseline else None,
        'thresholds_at_verification': {'aqi': aqi, 'pm2_5': pm25},
        'result_entries': len(result_rows), 'objects': objects, 'invoked_by_this_check': False,
        'limitations': ['Rule configuration and result timing do not provide a per-event trace ID.',
                        'Current secret thresholds are not an archived configuration for every past invocation.',
                        'Zero expected alerts does not exercise a new email delivery.']})
    print(f'{profile}: {len(result_rows)} result entries reconciled', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--hours', type=int, default=2, choices=range(1, 25))
    parser.add_argument('--release-proof', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a new output directory')
    end = datetime.now(timezone.utc)
    for profile in PROFILES:
        run(profile, args.output, end-timedelta(hours=args.hours), end, args.release_proof)


if __name__ == '__main__':
    main()
