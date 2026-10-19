"""Build a deterministic collector artifact and check the isolated stack contract."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tuan_3/scripts'))
from release import package
from common import write_json

TEMPLATE = ROOT / 'tuan_4/infrastructure/weather-stack.json'


def validate_contract(template):
    resources = template['Resources']
    required = {'DataBucket', 'BucketPolicy', 'ApiConfig', 'AlertTopic', 'EmailSubscription',
                'Collector', 'CollectorLogs', 'HourlyRule', 'SchedulePermission', 'Database',
                'RawTable', 'QueryWorkgroup', 'ErrorsAlarm', 'Dashboard', 'AlarmTopicPolicy',
                'ResultMetricFilter', 'ErrorMetricFilter'}
    if not required <= resources.keys():
        raise ValueError('Incomplete stack')
    if any(r['Type'].startswith('AWS::IAM::') for r in resources.values()):
        raise ValueError('Shared lab role must not be mutated by this stack')
    bucket = resources['DataBucket']
    if set(bucket['Properties']['PublicAccessBlockConfiguration'].values()) != {True}:
        raise ValueError('All four public access controls must be enabled')
    if bucket.get('DeletionPolicy') != 'Retain' or bucket.get('UpdateReplacePolicy') != 'Retain':
        raise ValueError('Evidence data must survive stack deletion/replacement')
    if resources['HourlyRule']['Properties']['State'] != 'DISABLED':
        raise ValueError('A new stack must start without automatic invocations')
    permission = resources['SchedulePermission']['Properties']
    if not {'SourceArn', 'SourceAccount'} <= permission.keys():
        raise ValueError('Schedule permission must be bound to its rule and account')
    alarm_policy = resources['AlarmTopicPolicy']['Properties']['PolicyDocument']['Statement']
    if (len(alarm_policy) != 1 or alarm_policy[0].get('Principal') != {'Service': 'cloudwatch.amazonaws.com'}
            or alarm_policy[0].get('Action') != 'sns:Publish'
            or 'aws:SourceArn' not in alarm_policy[0].get('Condition', {}).get('ArnEquals', {})
            or 'aws:SourceAccount' not in alarm_policy[0].get('Condition', {}).get('StringEquals', {})):
        raise ValueError('Alarm Publish permission must be limited to the stack alarm and account')
    props = resources['Collector']['Properties']
    if props['Handler'] != 'lambda_function.lambda_handler' or props['Runtime'] != 'python3.12':
        raise ValueError('Collector artifact/runtime mismatch')
    return {'resource_count': len(resources), 'shared_role_changed': False,
            'schedule_initial_state': 'DISABLED', 'data_retained': True}


def build(output):
    template_bytes = TEMPLATE.read_text(encoding='utf-8').encode('utf-8')
    template = json.loads(template_bytes)
    checks = validate_contract(template)
    output.mkdir(parents=True, exist_ok=False)
    source = (ROOT / 'tuan_2/lambda/lambda_function.py').read_text(encoding='utf-8').replace('\r\n', '\n').encode()
    artifact = package(source)
    (output / 'collector.zip').write_bytes(artifact)
    (output / TEMPLATE.name).write_bytes(template_bytes)
    proof = {'status': 'PASS', **checks, 'source_path': 'tuan_2/lambda/lambda_function.py',
             'source_sha256': hashlib.sha256(source).hexdigest(),
             'artifact_sha256': hashlib.sha256(artifact).hexdigest(),
             'template_sha256': hashlib.sha256(template_bytes).hexdigest(),
             'aws_stack_created': False}
    write_json(output / 'build.json', proof)
    return proof


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.output)))
