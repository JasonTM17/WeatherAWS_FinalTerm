"""Capture bounded Week 4 operations, security and cost evidence through Boto3."""
from __future__ import annotations

import argparse
import base64
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tuan_3/scripts'))
from common import FUNCTION, PROFILES, client, digest, ndjson_rows, session, write_csv, write_json
from dashboard import reconcile_periods
from monitoring_followup import classify_logs, statistics
from quality import REQUIRED
from snapshot import archive_source
from prepare_stack import TEMPLATE, validate_contract

RULE = 'WeatherCollectionSchedule'
FIELDS = ['timestamp_utc', 'request_hash', 'mode', 'collection_status', 'reported_records',
          'verified_records', 'cities', 'reported_alerts', 'expected_alerts', 'status']


def capture(folder, name, operation):
    try:
        result = operation()
        result = {'status': 'PASS', **result}
    except Exception as error:
        code = getattr(error, 'response', {}).get('Error', {}).get('Code', type(error).__name__)
        # Never serialize exception messages or SDK responses containing account identifiers.
        code = code if re.fullmatch(r'[A-Za-z0-9_.-]{1,70}', code) else 'ServiceError'
        result = {'status': 'BLOCKED_CAPABILITY' if code in (
            'AccessDenied', 'AccessDeniedException', 'UnauthorizedOperation', 'ExpiredToken',
            'ExpiredTokenException', 'UnrecognizedClientException', 'InvalidClientTokenId',
            'DataUnavailableException', 'SubscriptionRequiredException') else 'FAIL', 'error_code': code}
    write_json(folder / f'{name}.json', result)
    return result


def identity(sess):
    account = client(sess, 'sts').get_caller_identity()['Account']
    config = client(sess, 'lambda').get_function_configuration(FunctionName=FUNCTION)
    bucket = config.get('Environment', {}).get('Variables', {}).get('S3_BUCKET_NAME')
    if (config['FunctionArn'] != f'arn:aws:lambda:us-east-1:{account}:function:{FUNCTION}'
            or bucket != f'weather-aqi-{account}'):
        raise ValueError('Unexpected environment identity')
    return account, config, bucket


def source_check(sess, config):
    function = client(sess, 'lambda').get_function(FunctionName=FUNCTION)
    observed = function['Configuration']
    if observed['RevisionId'] != config['RevisionId']:
        raise ValueError('Deployment changed during capture')
    with urllib.request.urlopen(function['Code']['Location'], timeout=30) as handle:
        blob = handle.read()
    if base64.b64encode(bytes.fromhex(digest(blob))).decode() != config['CodeSha256']:
        raise ValueError('Package integrity mismatch')
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        source = archive.read('lambda_function.py')
    local = (ROOT / 'tuan_2/lambda/lambda_function.py').read_text(encoding='utf-8').replace('\r\n', '\n').encode()
    same = source.replace(b'\r\n', b'\n') == local
    return {'status': 'PASS' if same else 'FAIL', 'module_matches_repository': same,
            'module_sha256': digest(source), 'runtime': config['Runtime'],
            'lambda_state': config['State'], 'update_status': config['LastUpdateStatus']}


def rule_check(sess, config):
    events = client(sess, 'events')
    rule = events.describe_rule(Name=RULE)
    targets = [r for p in events.get_paginator('list_targets_by_rule').paginate(Rule=RULE)
               for r in p.get('Targets', [])]
    policy = json.loads(client(sess, 'lambda').get_policy(FunctionName=FUNCTION)['Policy'])
    from check_operations import policy_allows
    bound = len(targets) == 1 and targets[0]['Arn'] == config['FunctionArn']
    allowed = policy_allows(policy, rule['Arn'])
    rules = [r for p in events.get_paginator('list_rule_names_by_target').paginate(TargetArn=config['FunctionArn'])
             for r in p.get('RuleNames', [])]
    enabled = sum(events.describe_rule(Name=name)['State'] == 'ENABLED' for name in rules)
    return {'status': 'PASS' if bound and allowed and enabled == 1 and rule['State'] == 'ENABLED'
            and rule.get('ScheduleExpression') == 'rate(1 hour)' else 'FAIL',
            'canonical_rule': RULE, 'state': rule['State'], 'schedule': rule.get('ScheduleExpression'),
            'one_matching_target': bound, 'source_rule_permission': allowed,
            'enabled_rules_for_collector': enabled}


def minimum_policy_findings(documents):
    statements = [s for doc in documents for s in (doc.get('Statement', [])
        if isinstance(doc.get('Statement', []), list) else [doc['Statement']])]
    broad = 0
    actions = set()
    for statement in statements:
        if statement.get('Effect') != 'Allow':
            continue
        a, r = statement.get('Action', []), statement.get('Resource', [])
        a, r = ([a] if isinstance(a, str) else a), ([r] if isinstance(r, str) else r)
        actions.update(a)
        if ('NotAction' in statement or 'NotResource' in statement or '*' in r
                or any(x == '*' or x.endswith(':*') for x in a)):
            broad += 1
    return {'allow_statements_requiring_scope_review': broad,
            'required_collector_actions': ['s3:PutObject', 'sns:Publish',
                'secretsmanager:GetSecretValue', 'logs:CreateLogStream', 'logs:PutLogEvents'],
            'declared_action_count': len(actions),
            'effective_least_privilege_proven': False,
            'method': 'Static policy scope review; does not evaluate SCPs, boundaries or all IAM conditions'}


def role_check(sess, config):
    iam = client(sess, 'iam')
    role_name = config['Role'].rsplit('/', 1)[-1]
    if role_name != 'LabRole':
        raise ValueError('Unexpected execution role')
    role = iam.get_role(RoleName=role_name)['Role']
    trust = role['AssumeRolePolicyDocument']
    trust_statements = trust.get('Statement', [])
    if isinstance(trust_statements, dict):
        trust_statements = [trust_statements]
    trusts_lambda = any(s.get('Effect') == 'Allow' and isinstance(s.get('Principal'), dict)
        and 'lambda.amazonaws.com' in ([s['Principal'].get('Service')]
             if isinstance(s['Principal'].get('Service'), str) else s['Principal'].get('Service', []))
        for s in trust_statements)
    docs = []
    for page in iam.get_paginator('list_role_policies').paginate(RoleName=role_name):
        docs.extend(iam.get_role_policy(RoleName=role_name, PolicyName=n)['PolicyDocument']
                    for n in page.get('PolicyNames', []))
    for page in iam.get_paginator('list_attached_role_policies').paginate(RoleName=role_name):
        for policy in page.get('AttachedPolicies', []):
            version = iam.get_policy(PolicyArn=policy['PolicyArn'])['Policy']['DefaultVersionId']
            docs.append(iam.get_policy_version(PolicyArn=policy['PolicyArn'], VersionId=version)['PolicyVersion']['Document'])
    return {'execution_role': role_name, 'trusts_lambda_service': trusts_lambda,
            'policy_documents_read': len(docs), 'shared_role_modified': False, **minimum_policy_findings(docs)}


def storage_check(sess, bucket):
    s3 = client(sess, 's3')
    block = s3.get_public_access_block(Bucket=bucket)['PublicAccessBlockConfiguration']
    encryption = s3.get_bucket_encryption(Bucket=bucket)['ServerSideEncryptionConfiguration']['Rules']
    algorithms = [r['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] for r in encryption]
    try:
        public = s3.get_bucket_policy_status(Bucket=bucket)['PolicyStatus']['IsPublic']
        policy_state = 'PRESENT'
    except Exception as error:
        if getattr(error, 'response', {}).get('Error', {}).get('Code') != 'NoSuchBucketPolicy':
            raise
        public, policy_state = False, 'NO_BUCKET_POLICY'
    acl = s3.get_bucket_acl(Bucket=bucket)
    public_acl = any('AllUsers' in grant['Grantee'].get('URI', '') or
        'AuthenticatedUsers' in grant['Grantee'].get('URI', '') for grant in acl['Grants'])
    controls = all(block.get(k) is True for k in ('BlockPublicAcls', 'IgnorePublicAcls', 'BlockPublicPolicy', 'RestrictPublicBuckets'))
    good = controls and not public and not public_acl and bool(algorithms) and all(x in ('AES256', 'aws:kms', 'aws:kms:dsse') for x in algorithms)
    return {'status': 'PASS' if good else 'FAIL', 'all_public_access_blocks': controls,
            'public_policy': public, 'public_acl': public_acl, 'bucket_policy': policy_state,
            'encryption_algorithms': algorithms,
            'versioning': s3.get_bucket_versioning(Bucket=bucket).get('Status', 'NOT_ENABLED')}


def costs(ce, start, end):
    rows, token, seen = [], None, set()
    for _ in range(100):
        request = {'TimePeriod': {'Start': start, 'End': end}, 'Granularity': 'DAILY',
            'Metrics': ['UnblendedCost'], 'GroupBy': [{'Type': 'DIMENSION', 'Key': 'SERVICE'},
                                                    {'Type': 'DIMENSION', 'Key': 'RECORD_TYPE'}]}
        if token:
            request['NextPageToken'] = token
        response = ce.get_cost_and_usage(**request)
        for day in response['ResultsByTime']:
            for group in day['Groups']:
                metric = group['Metrics']['UnblendedCost']
                value = Decimal(metric['Amount'])
                if not value.is_finite() or metric['Unit'] != 'USD':
                    raise ValueError('Invalid billing amount or unit')
                key = (day['TimePeriod']['Start'], *group['Keys'])
                if key in seen:
                    raise ValueError('Repeated billing group')
                seen.add(key)
                rows.append({'date_utc': key[0], 'service': key[1], 'record_type': key[2],
                    'amount_usd': str(value), 'estimated': day['Estimated']})
        token = response.get('NextPageToken')
        if not token:
            return rows
    raise ValueError('Billing pagination limit reached')


def cost_check(sess, folder, start, end):
    rows = costs(client(sess, 'ce'), start, end)
    write_csv(folder / 'cost_by_service.csv', rows, ['date_utc', 'service', 'record_type', 'amount_usd', 'estimated'])
    total = sum((Decimal(r['amount_usd']) for r in rows), Decimal('0'))
    return {'status': 'PASS' if rows else 'NOT_AVAILABLE', 'start_inclusive': start,
            'end_exclusive': end, 'rows': len(rows), 'total_unblended_usd': str(total) if rows else None,
            'negative_rows': sum(Decimal(r['amount_usd']) < 0 for r in rows),
            'scope': 'Account service and record-type totals; not isolated project billing',
            'zero_rows_mean': 'No reported groups, not a measured zero charge'}


def verified_result(result, bucket, s3, folder, archived):
    if result.get('bucket') != bucket:
        raise ValueError('Result references another bucket')
    records = []
    descriptors = result.get('saved_files', [])
    if not isinstance(descriptors, list) or not 1 <= len(descriptors) <= 3:
        raise ValueError('Unexpected result object list')
    from check_operations import saved_object
    for descriptor in descriptors:
        key, count = saved_object(descriptor)
        if key not in archived:
            response = s3.get_object(Bucket=bucket, Key=key)
            blob = response['Body'].read()
            archive_source(folder, key, blob)
            archived[key] = (ndjson_rows(blob), digest(blob))
        data, _ = archived[key]
        if len(data) != count or any(set(r) != REQUIRED for r in data):
            raise ValueError('Raw schema or record count differs')
        records.extend(data)
    cities = {r['city'] for r in records}
    valid = (result.get('records_collected') == len(records) and
             result.get('collection_status') == 'complete' and not result.get('failed_cities') and
             cities == {'HoChiMinh', 'HaNoi', 'DaNang'})
    return records, valid


def operations(sess, config, bucket, folder, start, end):
    logs, s3 = client(sess, 'logs'), client(sess, 's3')
    events = []
    for page in logs.get_paginator('filter_log_events').paginate(logGroupName=f'/aws/lambda/{FUNCTION}',
        startTime=int(start.timestamp() * 1000), endTime=int(end.timestamp() * 1000)):
        events.extend(page.get('events', []))
        if len(events) > 10000:
            raise ValueError('Narrow the log window')
    lifecycle, summary = classify_logs(events, start, end)
    write_csv(folder / 'lifecycle.csv', lifecycle,
        ['timestamp_utc', 'event_hash', 'stream_hash', 'kind', 'request_hash', 'status', 'reported_records', 'alerts_sent'])
    counters = statistics(client(sess, 'cloudwatch'), start, end)
    write_csv(folder / 'native_metrics.csv', counters,
              ['namespace', 'metric', 'statistic', 'timestamp_utc', 'value', 'unit'])
    aligned = reconcile_periods(counters)
    write_json(folder / 'metric_reconciliation.json', aligned)
    # Thread each stream separately: a Lambda execution environment handles one request at a time.
    active, archived, rows, seen = {}, {}, [], set()
    for event in sorted(events, key=lambda e: (e['timestamp'], e.get('ingestionTime', 0))):
        if event['eventId'] in seen:
            continue
        seen.add(event['eventId'])
        msg, stream = event['message'], event['logStreamName']
        match = re.match(r'^START RequestId:\s*([\w-]+)', msg)
        if match:
            active[stream] = {'request': digest(match[1].encode())[:20], 'mode': 'realtime'}
        elif msg.startswith('END RequestId:'):
            active.pop(stream, None)
        elif '[INFO] Backfill mode requested' in msg and stream in active:
            active[stream]['mode'] = 'historical'
        elif '[INFO] Result: ' in msg:
            result = json.loads(msg.split('[INFO] Result: ', 1)[1])
            records, good = verified_result(result, bucket, s3, folder, archived)
            context = active.get(stream, {'request': '', 'mode': 'unresolved'})
            rows.append({'timestamp_utc': datetime.fromtimestamp(event['timestamp']/1000, timezone.utc).isoformat(),
                'request_hash': context['request'], 'mode': context['mode'], 'collection_status': result['collection_status'],
                'reported_records': result['records_collected'], 'verified_records': len(records),
                'cities': len({r['city'] for r in records}), 'reported_alerts': result['alerts_sent'],
                'expected_alerts': 0 if context['mode'] == 'historical' else '',
                'status': 'PASS' if good and context['request'] else 'REVIEW'})
    write_csv(folder / 'collection_s3.csv', rows, FIELDS)
    write_csv(folder / 'objects.csv', [{'key': k, 'records': len(v[0]), 'sha256': v[1]} for k,v in sorted(archived.items())],
              ['key', 'records', 'sha256'])
    lifecycle_by_request = {}
    for item in lifecycle:
        if item['request_hash']:
            lifecycle_by_request.setdefault(item['request_hash'], set()).add(item['kind'])
    matched = sum({'START','END','REPORT'} <= lifecycle_by_request.get(r['request_hash'], set()) for r in rows)
    return {'status': 'PASS' if rows and all(r['status'] == 'PASS' for r in rows) and matched == len(rows) else 'REVIEW',
            'window_start': start.isoformat(), 'window_end': end.isoformat(),
            'results_verified': len(rows), 'matched_request_lifecycles': matched,
            'objects_verified': len(archived), 'distinct_object_records': sum(len(v[0]) for v in archived.values()),
            'metric_alignment_status': aligned['status'], 'lifecycle_summary': summary,
            'semantics': 'Request/log/S3 reconciliation and native metric alignment are separate checks; no inferred email receipt',
            'invoked_by_audit': False}


def template_check(sess):
    template = TEMPLATE.read_text(encoding='utf-8')
    contract = validate_contract(json.loads(template))
    result = client(sess, 'cloudformation').validate_template(TemplateBody=template)
    return {'template_sha256': digest(template.encode()), 'parameters_validated': len(result.get('Parameters', [])),
            **contract, 'stack_created': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--hours', type=int, choices=range(1, 25), default=2)
    parser.add_argument('--cost-start', type=date.fromisoformat, required=True)
    parser.add_argument('--cost-end', type=date.fromisoformat, required=True)
    args = parser.parse_args()
    if not 0 < (args.cost_end - args.cost_start).days <= 31:
        parser.error('Billing interval must contain 1–31 days; end is exclusive')
    args.output.mkdir(parents=True, exist_ok=False)
    end = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    end -= timedelta(minutes=end.minute % 5)
    start = end - timedelta(hours=args.hours)
    report = {'captured_at': datetime.now(timezone.utc).isoformat(), 'source_commit':
        subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'profiles': {}, 'aws_mutations': False}
    for profile in PROFILES:
        folder = args.output / profile
        folder.mkdir()
        sess = session(profile)
        parts = {}
        parts['cost'] = capture(folder, 'cost', lambda: cost_check(sess, folder, str(args.cost_start), str(args.cost_end)))
        parts['template'] = capture(folder, 'template', lambda: template_check(sess))
        try:
            _, config, bucket = identity(sess)
        except Exception:
            parts['environment'] = {'status': 'BLOCKED_CAPABILITY'}
        else:
            parts['source'] = capture(folder, 'source', lambda: source_check(sess, config))
            parts['schedule'] = capture(folder, 'schedule', lambda: rule_check(sess, config))
            parts['storage'] = capture(folder, 'storage', lambda: storage_check(sess, bucket))
            parts['role'] = capture(folder, 'role', lambda: role_check(sess, config))
            parts['operations'] = capture(folder, 'operations', lambda: operations(sess, config, bucket, folder, start, end))
        report['profiles'][profile] = {k: v['status'] for k,v in parts.items()}
        print(json.dumps({'profile': profile, 'checks': report['profiles'][profile]}), flush=True)
    write_json(args.output / 'summary.json', report)
    manifest = {p.relative_to(args.output).as_posix(): digest(p.read_bytes())
        for p in sorted(args.output.rglob('*')) if p.is_file()}
    write_json(args.output / 'manifest.json', manifest)


if __name__ == '__main__':
    main()
