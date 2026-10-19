"""Run one explicit realtime collection, verify its exact S3 records and Athena output."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tuan_3/scripts'))
from botocore.config import Config
from common import FUNCTION, PROFILES, client, digest, query, session, write_csv, write_json
from verify_environment import identity, source_check, verified_result


def comparison(records, result, settings):
    aqi = float(settings.get('aqi_threshold_us_aqi', 100))
    pm = float(settings.get('aqi_threshold_pm25', 35.5))
    from check_operations import expected_alerts
    expected = expected_alerts(records, aqi, pm)
    good = (len(records) == 3 and len({r['record_id'] for r in records}) == 3 and
            result['alerts_sent'] == expected)
    return {'status': 'PASS' if good else 'FAIL', 'records': len(records),
            'expected_alerts': expected, 'reported_sns_acceptances': result['alerts_sent'],
            'threshold_aqi': aqi, 'threshold_pm2_5': pm,
            'email_receipt': 'PENDING_RECIPIENT_CONFIRMATION' if expected else 'NOT_EXERCISED'}


def exact_query(records):
    ids = [r['record_id'] for r in records]
    if not ids or any(not re.fullmatch(r'(?:HoChiMinh|HaNoi|DaNang)_\d{14}_[a-f0-9]{6}', item) for item in ids):
        raise ValueError('Unexpected record identifier')
    dates = {(str(r['year']), str(r['month']), str(r['day'])) for r in records}
    if any(not re.fullmatch(r'\d{4}/\d{2}/\d{2}', '/'.join(d)) for d in dates):
        raise ValueError('Unexpected partition values')
    partitions = ' OR '.join(f"(year='{y}' AND month='{m}' AND day='{d}')" for y,m,d in sorted(dates))
    return "SELECT record_id, city, us_aqi, pm2_5 FROM weather_airquality_records WHERE (" + partitions + ") AND record_id IN (" + ','.join("'"+item+"'" for item in ids) + ') ORDER BY city'


def verify_athena(sess, bucket, records, output):
    sql = exact_query(records)
    (output / 'exact_records.sql').write_text(sql + ';\n', encoding='utf-8')
    metadata, selected = query(sess, sql, f's3://{bucket}/athena-results/week4/', 'athena_exact', output)
    actual = {r['record_id']: r for r in selected}
    expected = {r['record_id']: r for r in records}
    match = len(selected) == 3 and set(actual) == set(expected) and all(
        actual[k]['city'] == expected[k]['city'] and float(actual[k]['us_aqi']) == float(expected[k]['us_aqi'])
        and float(actual[k]['pm2_5']) == float(expected[k]['pm2_5']) for k in expected)
    return 'PASS' if match and not metadata['result_reused'] else 'FAIL'


def run(profile, output):
    sess = session(profile)
    _, config, bucket = identity(sess)
    if source_check(sess, config)['status'] != 'PASS':
        raise ValueError('Deploy the reviewed collector before running this check')
    settings = json.loads(client(sess, 'secretsmanager').get_secret_value(
        SecretId=config['Environment']['Variables']['SECRET_NAME'])['SecretString'])
    # No transport retry: an unacknowledged synchronous request could already have executed.
    lamb = sess.client('lambda', config=Config(connect_timeout=10, read_timeout=90,
        retries={'total_max_attempts': 1}))
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / 'invocation.json', {'status': 'PREPARED', 'student': PROFILES[profile],
        'event': {}, 'captured_at': datetime.now(timezone.utc).isoformat()})
    try:
        response = lamb.invoke(FunctionName=FUNCTION, InvocationType='RequestResponse', Payload=b'{}')
    except Exception:
        write_json(output / 'invocation.json', {'status': 'UNKNOWN_ACKNOWLEDGEMENT', 'retry_automatically': False})
        raise RuntimeError('Inspect the invocation log before trying again') from None
    if response.get('FunctionError') or response['StatusCode'] != 200:
        write_json(output / 'invocation.json', {'status': 'FAIL', 'function_error': bool(response.get('FunctionError'))})
        raise RuntimeError('Collector did not complete')
    result = json.loads(response['Payload'].read())
    archived = {}
    records, good = verified_result(result, bucket, client(sess, 's3'), output, archived)
    verdict = comparison(records, result, settings)
    if not good:
        verdict['status'] = 'FAIL'
    write_csv(output / 'raw_invocation.csv', records, list(records[0]))
    write_json(output / 'invocation.json', {'student': PROFILES[profile],
        'captured_at': datetime.now(timezone.utc).isoformat(), **verdict,
        'request_hash': digest(response['ResponseMetadata']['RequestId'].encode())[:20],
        'module_sha256': source_check(sess, config)['module_sha256'],
        'secret_changed': False, 'schedule_changed': False})
    if verdict['status'] != 'PASS':
        raise ValueError('Realtime collection or alert count did not match')
    # Do not repair/create partitions implicitly. Missing catalog data is a separate failed gate.
    verdict['athena_status'] = verify_athena(sess, bucket, records, output)
    write_json(output / 'e2e.json', verdict)
    if verdict['athena_status'] != 'PASS':
        raise ValueError('Athena output differs from exact invocation records')
    return verdict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True, choices=tuple(PROFILES))
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--invoke', action='store_true', help='Make one realtime invocation; may send real threshold alerts')
    args = parser.parse_args()
    if not args.invoke:
        print(json.dumps({'status': 'PREVIEW', 'invocations': 0, 'writes': False,
            'action_on_invoke': 'One realtime invocation, S3 records, possible SNS alerts, one Athena SELECT'}))
    else:
        try:
            print(json.dumps(run(args.profile, args.output)))
        except Exception as error:
            print(json.dumps({'status': 'FAIL', 'reason': type(error).__name__, 'inspect': 'Selected output directory'}))
            raise SystemExit(1)
