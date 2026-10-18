"""Bounded, read-only diagnostics; persist allowlisted fields, never raw AWS messages."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import unquote

from botocore.exceptions import BotoCoreError, ClientError

from common import FUNCTION, PROFILES, client, digest, session, write_json
from monitoring_followup import classify_logs

START = datetime(2026, 10, 18, 7, 40, tzinfo=timezone.utc)
END = datetime(2026, 10, 18, 11, 0, tzinfo=timezone.utc)


def attempt(action):
    try:
        return {'status': 'READ_OK', 'data': action()}
    except ClientError as exc:
        return {'status': 'UNAVAILABLE', 'error_code': exc.response['Error']['Code']}
    except BotoCoreError as exc:
        return {'status': 'UNAVAILABLE', 'error_type': type(exc).__name__}


def safe_history(events):
    """Do not retain users, IPs, parameters, resources, account IDs or raw error text."""
    rows = []
    for item in events:
        raw = json.loads(item['CloudTrailEvent'])
        rows.append({'timestamp_utc': item['EventTime'].astimezone(timezone.utc).isoformat(), 'event': item['EventName'],
                     'source': raw.get('eventSource'), 'read_only': raw.get('readOnly'),
                     'error_code': raw.get('errorCode'), 'event_hash': digest(item['EventId'].encode())[:20],
                     'target_function_named': FUNCTION in json.dumps(raw.get('requestParameters') or {}),
                     'management_event': raw.get('managementEvent')})
    return sorted(rows, key=lambda r: (r['timestamp_utc'], r['event_hash']))


def history(ct, source):
    events = []
    for page in ct.get_paginator('lookup_events').paginate(
            LookupAttributes=[{'AttributeKey': 'EventSource', 'AttributeValue': source}],
            StartTime=START, EndTime=END):
        events.extend(page['Events'])
    return safe_history(events)


def metrics(cw):
    rows = []
    for name, stat in (('Errors', 'Sum'), ('Invocations', 'Sum'), ('Throttles', 'Sum'),
                       ('AsyncEventsReceived', 'Sum'), ('AsyncEventsDropped', 'Sum'),
                       ('AsyncEventAge', 'Maximum'), ('Duration', 'SampleCount')):
        points = cw.get_metric_statistics(Namespace='AWS/Lambda', MetricName=name,
            Dimensions=[{'Name': 'FunctionName', 'Value': FUNCTION}],
            StartTime=START, EndTime=END, Period=60, Statistics=[stat])['Datapoints']
        rows.append({'metric': name, 'statistic': stat, 'points': [
            {'timestamp_utc': p['Timestamp'].astimezone(timezone.utc).isoformat(), 'value': p[stat], 'unit': p['Unit']}
            for p in sorted(points, key=lambda p: p['Timestamp'])]})
    return rows


def policy_summary(document):
    if isinstance(document, str):
        document = json.loads(unquote(document))
    statements = document.get('Statement', [])
    if isinstance(statements, dict):
        statements = [statements]
    return {'sha256': digest(json.dumps(document, sort_keys=True).encode()), 'statements': [
        {'effect': s.get('Effect'), 'actions': s.get('Action'), 'not_actions': s.get('NotAction'),
         'all_resources': s.get('Resource') == '*',
         'time_conditions': {op: {key: value for key, value in terms.items() if key == 'aws:CurrentTime'}
                             for op, terms in s.get('Condition', {}).items()
                             if isinstance(terms, dict) and 'aws:CurrentTime' in terms},
         'other_condition_keys': sorted({key for terms in s.get('Condition', {}).values()
                                        if isinstance(terms, dict) for key in terms if key != 'aws:CurrentTime'})}
        for s in statements]}


def iam_timeline(ct, iam, role):
    attached = iam.list_attached_role_policies(RoleName=role)['AttachedPolicies']
    arns = {p['PolicyArn'] for p in attached}
    rows = []
    for page in ct.get_paginator('lookup_events').paginate(
            LookupAttributes=[{'AttributeKey': 'EventSource', 'AttributeValue': 'iam.amazonaws.com'}],
            StartTime=START, EndTime=END):
        for item in page['Events']:
            raw = json.loads(item['CloudTrailEvent'])
            if raw.get('readOnly') is not False:
                continue
            params = raw.get('requestParameters') or {}
            row = {'timestamp_utc': item['EventTime'].astimezone(timezone.utc).isoformat(),
                   'event': item['EventName'], 'error_code': raw.get('errorCode'),
                   'execution_role_named': params.get('roleName') == role,
                   'currently_attached_policy_named': params.get('policyArn') in arns,
                   'set_as_default': params.get('setAsDefault'),
                   'event_hash': digest(item['EventId'].encode())[:20]}
            if params.get('policyDocument'):
                row['policy_document'] = policy_summary(params['policyDocument'])
            rows.append(row)
    current = []
    for item in attached:
        def current_document(item=item):
            meta = iam.get_policy(PolicyArn=item['PolicyArn'])['Policy']
            return {'updated_utc': meta['UpdateDate'].astimezone(timezone.utc).isoformat(),
                    'default_version': meta['DefaultVersionId'],
                    'document': policy_summary(iam.get_policy_version(PolicyArn=item['PolicyArn'],
                        VersionId=meta['DefaultVersionId'])['PolicyVersion']['Document'])}
        current.append(attempt(current_document))
    return {'changes': sorted(rows, key=lambda r: (r['timestamp_utc'], r['event_hash'])),
            'current_attached_policies': current,
            'limitation': 'Timeline and published documents do not prove a specific denied Lambda runtime operation'}


def role_correlations(ct, role_arn):
    rows = []
    for source in ('sts.amazonaws.com', 'lambda.amazonaws.com'):
        for page in ct.get_paginator('lookup_events').paginate(
                LookupAttributes=[{'AttributeKey': 'EventSource', 'AttributeValue': source}],
                StartTime=START, EndTime=END):
            for item in page['Events']:
                raw = json.loads(item['CloudTrailEvent'])
                params = raw.get('requestParameters') or {}
                base = {'timestamp_utc': item['EventTime'].astimezone(timezone.utc).isoformat(),
                        'event': item['EventName'], 'error_code': raw.get('errorCode'),
                        'event_hash': digest(item['EventId'].encode())[:20]}
                if item['EventName'] == 'AssumeRole' and params.get('roleArn') == role_arn:
                    rows.append({**base, 'execution_role_target': True,
                                 'function_session_named': FUNCTION in params.get('roleSessionName', '')})
                if raw.get('errorCode'):
                    issuer = raw.get('userIdentity', {}).get('sessionContext', {}).get('sessionIssuer', {})
                    rows.append({**base, 'caller_is_execution_role': issuer.get('arn') == role_arn})
    return sorted(rows, key=lambda r: (r['timestamp_utc'], r['event_hash']))


def log_evidence(logs, group):
    streams = []
    for page in logs.get_paginator('describe_log_streams').paginate(
            logGroupName=group, logStreamNamePrefix='2026/10/18/'):
        streams.extend(page['logStreams'])
    events, counts = [], []
    for stream in streams:
        token = None
        count = 0
        while True:
            args = dict(logGroupName=group, logStreamName=stream['logStreamName'],
                        startTime=int(START.timestamp()*1000), endTime=int(END.timestamp()*1000),
                        startFromHead=True)
            if token:
                args['nextToken'] = token
            page = logs.get_log_events(**args)
            for event in page['events']:
                count += 1
                events.append({**event, 'eventId': digest((stream['logStreamName'] + str(event)).encode()),
                               'logStreamName': stream['logStreamName']})
            following = page['nextForwardToken']
            if following == token:
                break
            token = following
        counts.append({'stream_hash': digest(stream['logStreamName'].encode())[:20], 'events_in_window': count,
                       'creation_time_utc': datetime.fromtimestamp(stream['creationTime']/1000, timezone.utc).isoformat()})
    typed, summary = classify_logs(events, START, END)
    # Init reports without START are relevant even if the report is not an explicit error.
    summary['all_init_reports'] = sum(e['message'].startswith('INIT_REPORT') for e in events)
    summary['runtime_error_signatures'] = sum(any(s in e['message'] for s in (
        'Runtime.ImportModuleError', 'Runtime.InvalidEntrypoint', 'Task timed out', 'AccessDenied',
        'Sandbox.Timedout', 'Runtime.ExitError')) for e in events)
    return {'stream_counts': counts, 'lifecycle': typed, 'summary': summary,
            'coverage': 'Direct GetLogEvents for streams with date prefix; no raw messages retained'}


def collect(profile):
    sess = session(profile)
    lam, cw, logs, ct, iam, eb = [client(sess, name) for name in
        ('lambda', 'cloudwatch', 'logs', 'cloudtrail', 'iam', 'events')]
    cfg = lam.get_function_configuration(FunctionName=FUNCTION)
    group = cfg.get('LoggingConfig', {}).get('LogGroup', '/aws/lambda/' + FUNCTION)
    role = cfg['Role'].split('/')[-1]
    result = {'student': PROFILES[profile], 'captured_at_utc': datetime.now(timezone.utc).isoformat(),
              'window_start_utc': START.isoformat(), 'window_end_exclusive_utc': END.isoformat(),
              'read_only': True, 'configuration': {k: cfg.get(k) for k in
              ('Runtime', 'Handler', 'Timeout', 'MemorySize', 'LastModified', 'State', 'StateReasonCode',
               'LastUpdateStatus', 'LastUpdateStatusReasonCode', 'CodeSha256', 'Version')},
              'logging': {'LogFormat': cfg.get('LoggingConfig', {}).get('LogFormat'),
                          'default_log_group': group == '/aws/lambda/' + FUNCTION},
              'dead_letter_configured': bool(cfg.get('DeadLetterConfig')),
              'probes': {}}
    p = result['probes']
    p['minute_metrics'] = attempt(lambda: metrics(cw))
    p['direct_stream_logs'] = attempt(lambda: log_evidence(logs, group))
    p['async_configuration'] = attempt(lambda: {k: v for k, v in lam.get_function_event_invoke_config(
        FunctionName=FUNCTION).items() if k in ('MaximumRetryAttempts', 'MaximumEventAgeInSeconds', 'LastModified')})
    p['concurrency'] = attempt(lambda: {k: v for k, v in lam.get_function_concurrency(
        FunctionName=FUNCTION).items() if k == 'ReservedConcurrentExecutions'})
    p['role'] = attempt(lambda: {'created': iam.get_role(RoleName=role)['Role']['CreateDate'].isoformat(),
                               'interpretation': 'Current role exists; not historical permission proof'})
    p['attached_policy_count'] = attempt(lambda: len(iam.list_attached_role_policies(RoleName=role)['AttachedPolicies']))
    p['inline_policy_names'] = attempt(lambda: {'count': len(iam.list_role_policies(RoleName=role)['PolicyNames'])})
    p['iam_policy_timeline'] = attempt(lambda: iam_timeline(ct, iam, role))
    p['role_correlations'] = attempt(lambda: role_correlations(ct, cfg['Role']))
    for source in ('lambda.amazonaws.com', 'events.amazonaws.com', 'iam.amazonaws.com', 'logs.amazonaws.com', 'sts.amazonaws.com'):
        p['history_' + source] = attempt(lambda source=source: history(ct, source))
    p['trail_inventory'] = attempt(lambda: {'trail_count': len(ct.describe_trails(includeShadowTrails=True)['trailList']),
                                          'limitation': 'Inventory alone does not prove data-event coverage'})
    p['event_data_stores'] = attempt(lambda: {'count': len(ct.list_event_data_stores()['EventDataStores'])})
    p['schedule'] = attempt(lambda: {k: v for k, v in eb.describe_rule(Name='WeatherCollectionSchedule').items()
                                    if k in ('State', 'ScheduleExpression')})
    p['target_retry'] = attempt(lambda: [{'targets_function': t.get('Arn', '').endswith(':function:' + FUNCTION),
        'retry_policy': t.get('RetryPolicy'), 'dead_letter_configured': bool(t.get('DeadLetterConfig'))}
        for t in eb.list_targets_by_rule(Rule='WeatherCollectionSchedule')['Targets']])
    return result


def summarize_evidence(probe):
    """Report observed minute values; never infer missing Invocations from Errors or STS."""
    series = {r['metric']: r['points'] for r in probe['probes']['minute_metrics']['data']}
    rows = []
    for minute in (15, 16, 18):
        stamp = datetime(2026, 10, 18, 9, minute, tzinfo=timezone.utc).isoformat()
        values = {name: next((p['value'] for p in points if p['timestamp_utc'] == stamp), None)
                  for name, points in series.items()}
        rows.append({'timestamp_utc': stamp, **values})
    return {'status': 'ROOT_CAUSE_UNRESOLVED', 'observed_minutes': rows,
            'errors_sum_in_0915_five_minute_bucket': sum(r['Errors'] for r in rows if r['Errors'] is not None),
            'interpretation': 'Pattern is consistent with asynchronous failure/retry and a dropped event; individual events are not linked by request ID',
            'missing_invocations_explained': False, 'application_exception_identified': False,
            'lambda_or_iam_modified_by_investigation': False,
            'whole_window_error_rate_percent': None}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=PROFILES, default='default')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    observed = attempt(lambda: collect(args.profile))
    if observed['status'] != 'READ_OK':
        raise SystemExit(json.dumps(observed))
    value = observed['data']
    write_json(args.output, value)
    print(json.dumps({'student': value['student'], 'probe_status': {
        k: v['status'] for k, v in value['probes'].items()}}))
