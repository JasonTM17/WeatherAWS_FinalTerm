"""Preview, pause or restore the canonical collection rule with a private state file."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tuan_3/scripts'))
from common import FUNCTION, PROFILES, client, digest, session

RULE = 'WeatherCollectionSchedule'
BACKUPS = ROOT / 'output/week4_session_control'


def publish_state(path, value):
    """Publish a state transition without truncating the recovery record."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
            prefix=path.name + '.', suffix='.tmp', delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(value, handle, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def binding(sess):
    account = client(sess, 'sts').get_caller_identity()['Account']
    config = client(sess, 'lambda').get_function_configuration(FunctionName=FUNCTION)
    expected = f'arn:aws:lambda:us-east-1:{account}:function:{FUNCTION}'
    if config['FunctionArn'] != expected:
        raise ValueError('Unexpected collection environment')
    events = client(sess, 'events')
    rule = events.describe_rule(Name=RULE, EventBusName='default')
    if rule['Arn'] != f'arn:aws:events:us-east-1:{account}:rule/{RULE}':
        raise ValueError('Unexpected rule identity')
    targets = []
    for page in events.get_paginator('list_targets_by_rule').paginate(Rule=RULE, EventBusName='default'):
        targets.extend(page.get('Targets', []))
    if (len(targets) != 1 or targets[0]['Arn'] != expected
            or rule.get('ScheduleExpression') != 'rate(1 hour)'
            or rule.get('State') not in ('ENABLED', 'DISABLED')):
        raise ValueError('Rule binding differs; no schedule change allowed')
    # Include target input, role and retry configuration in the ownership fingerprint.
    signature = digest(json.dumps({'arn': rule['Arn'], 'schedule': rule['ScheduleExpression'],
        'targets': targets}, sort_keys=True).encode())
    return events, {'account_fingerprint': digest(account.encode()), 'binding_fingerprint': signature,
                    'original_state': rule['State']}


def private_path(path):
    path = Path(path).resolve()
    if not path.is_relative_to(BACKUPS.resolve()) or path.suffix != '.json':
        raise ValueError('State file must be beneath ignored output/week4_session_control')
    return path


def control(sess, action, state_file=None, apply=False):
    events, current = binding(sess)
    if action == 'preview':
        return {'status': 'PASS', 'current_state': current['original_state'], 'changed': False}
    if not state_file:
        raise ValueError('A private state file is required')
    state_file = private_path(state_file)
    if action == 'pause':
        saved = dict(current, captured_at=datetime.now(timezone.utc).isoformat(), status='PREPARED')
        desired = 'DISABLED'
    elif action == 'restore':
        saved = json.loads(state_file.read_text(encoding='utf-8'))
        if (saved.get('status') not in ('PREPARED', 'PAUSED') or
            any(saved.get(k) != current[k] for k in ('account_fingerprint', 'binding_fingerprint'))
            or current['original_state'] != 'DISABLED'):
            raise ValueError('State or target changed since pause; restore refused')
        desired = saved['original_state']
        if desired not in ('ENABLED', 'DISABLED'):
            raise ValueError('Invalid original state')
    else:
        raise ValueError('Unknown session action')
    if not apply:
        return {'status': 'PREVIEW', 'action': action, 'desired_state': desired, 'changed': False}
    _, latest = binding(sess)
    if latest != current:
        raise ValueError('Rule changed during preview; no mutation allowed')
    if action == 'pause':
        state_file.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation prevents replacing a previous recovery state.
        with state_file.open('x', encoding='utf-8') as handle:
            json.dump(saved, handle, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
    if desired != current['original_state']:
        operation = events.enable_rule if desired == 'ENABLED' else events.disable_rule
        operation(Name=RULE, EventBusName='default')
    _, after = binding(sess)
    if (after['original_state'] != desired or
            any(after[k] != current[k] for k in ('account_fingerprint', 'binding_fingerprint'))):
        raise ValueError('Schedule readback differs; inspect saved private state')
    saved['status'] = 'PAUSED' if action == 'pause' else 'RESTORED'
    publish_state(state_file, saved)
    return {'status': 'PASS', 'action': action, 'current_state': desired,
            'changed': desired != current['original_state'], 'data_deleted': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('preview', 'pause', 'restore'))
    parser.add_argument('--profile', choices=tuple(PROFILES), required=True)
    parser.add_argument('--state-file', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(control(session(args.profile), args.action, args.state_file, args.apply)))
    except Exception as error:
        print(json.dumps({'status': 'FAIL', 'reason': type(error).__name__, 'details': 'Inspect the selected environment privately'}))
        raise SystemExit(1)
