"""Read GitHub deployment evidence anonymously; never create or update records."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = 'JasonTM17/WeatherAWS_FinalTerm'
API = f'https://api.github.com/repos/{REPOSITORY}'
WEB = f'https://github.com/{REPOSITORY}'
REGISTRATION = ROOT / 'tuan_4/results/github_deployments_2026_10_21/registration.json'
RECORD_FIELDS = ('id', 'environment', 'sha', 'ref', 'task', 'created_at', 'updated_at')
STATUS_FIELDS = ('id', 'state', 'created_at', 'environment', 'environment_url', 'log_url')


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def selected(value, keys):
    return {key: value.get(key) for key in keys}


def get_public(url, json_response=True):
    """Use GET only, with no token, cookie jar or credential lookup."""
    headers = {'User-Agent': 'WeatherAWS-public-evidence-review',
               'Accept': 'application/vnd.github+json' if json_response else 'text/html'}
    request = urllib.request.Request(url, headers=headers, method='GET')
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            result = {'url': url, 'http_status': response.status, 'final_url': response.url,
                      'github_request_id': response.headers.get('x-github-request-id'),
                      'response_date': response.headers.get('date')}
            if json_response:
                result['body'] = json.loads(response.read())
            return result
    except urllib.error.HTTPError as error:
        return {'url': url, 'http_status': error.code, 'final_url': error.url,
                'github_request_id': error.headers.get('x-github-request-id'),
                'response_date': error.headers.get('date')}


def collect(registration, registration_bytes, fetch=get_public):
    listing = fetch(f'{API}/deployments?per_page=100')
    body = listing.pop('body', None)
    listing['records'] = [selected(item, RECORD_FIELDS) for item in body] if isinstance(body, list) else None
    checks = []
    for expected in registration['records']:
        identity = expected['deployment_id']
        record = fetch(f'{API}/deployments/{identity}')
        body = record.pop('body', None)
        record['fields'] = selected(body, RECORD_FIELDS) if isinstance(body, dict) else None
        if isinstance(body, dict):
            payload = body.get('payload')
            record['payload'] = selected(payload, ('registration_only', 'fresh_aws_verification',
                'evidence_commit', 'stack_name', 'evidence_url')) if isinstance(payload, dict) else None
        statuses = fetch(f'{API}/deployments/{identity}/statuses')
        body = statuses.pop('body', None)
        statuses['records'] = [selected(item, STATUS_FIELDS) for item in body] if isinstance(body, list) else None
        checks.append({'environment': expected['environment'], 'deployment_id': identity,
                       'deployment': record, 'statuses': statuses,
                       'public_environment_page': fetch(expected['deployment_url'], False)})
    return {'schema_version': 1, 'repository': REPOSITORY,
            'checked_at_utc': datetime.now(timezone.utc).isoformat(),
            'access_mode': 'anonymous_without_token_or_cookies',
            'read_only': True, 'aws_calls': False,
            'response_scope': 'Selected public API fields and HTTP metadata; no response body for HTML pages',
            'registration_sha256': hashlib.sha256(registration_bytes).hexdigest(),
            'list_response': listing, 'checks': checks}


def require_response(response, url):
    if (response.get('http_status') != 200 or response.get('url') != url
            or response.get('final_url') != url or not response.get('github_request_id')):
        raise ValueError('Expected public GitHub endpoint did not return HTTP 200 at its exact URL')


def validate(snapshot, registration, registration_bytes):
    """Bind public API identity/status to the earlier summary; keep UI access separate."""
    expected_records = registration['records']
    if ({item['environment'] for item in expected_records} != {'week4-tien-son', 'week4-ngoc-quyen'}
            or len(expected_records) != 2
            or len({item['deployment_id'] for item in expected_records}) != 2
            or any(item.get('state') != 'success' for item in expected_records)):
        raise ValueError('Registration must identify exactly two different Week 4 deployments')
    if (snapshot.get('schema_version') != 1 or snapshot.get('repository') != REPOSITORY
            or snapshot.get('access_mode') != 'anonymous_without_token_or_cookies'
            or snapshot.get('read_only') is not True or snapshot.get('aws_calls') is not False
            or snapshot.get('registration_sha256') != hashlib.sha256(registration_bytes).hexdigest()):
        raise ValueError('Readback provenance differs')
    checked_at = datetime.fromisoformat(snapshot['checked_at_utc'])
    if checked_at.utcoffset() is None:
        raise ValueError('Readback timestamp requires an explicit timezone')
    listing = snapshot['list_response']
    require_response(listing, f'{API}/deployments?per_page=100')
    if not isinstance(listing.get('records'), list):
        raise ValueError('Public deployment list is unavailable')
    checks = snapshot['checks']
    if len(checks) != 2 or len({item['deployment_id'] for item in checks}) != 2:
        raise ValueError('Readback must contain two distinct deployment checks')
    by_id = {item['deployment_id']: item for item in checks}
    page_results = []
    for expected in expected_records:
        identity, environment = expected['deployment_id'], expected['environment']
        check = by_id.get(identity)
        if check is None or check['environment'] != environment:
            raise ValueError('Deployment identity differs')
        record = check['deployment']
        require_response(record, f'{API}/deployments/{identity}')
        fields = record.get('fields')
        if not isinstance(fields, dict) or any(fields.get(key) != value for key, value in {
                'id': identity, 'environment': environment, 'sha': expected['evidence_commit'],
                'created_at': expected['github_record_created_at']}.items()):
            raise ValueError('Deployment ID/environment/commit/creation date differs')
        if not any(item == fields for item in listing['records']):
            raise ValueError('Deployment is absent from the public list')
        payload = record.get('payload')
        if not isinstance(payload, dict) or any(payload.get(key) != value for key, value in {
                'registration_only': True, 'fresh_aws_verification': False,
                'evidence_commit': expected['evidence_commit'], 'stack_name': expected['stack_name'],
                'evidence_url': expected['evidence_url']}.items()):
            raise ValueError('Historical registration payload differs')
        statuses = check['statuses']
        require_response(statuses, f'{API}/deployments/{identity}/statuses')
        values = statuses.get('records')
        if not isinstance(values, list) or not values:
            raise ValueError('Deployment has no public status evidence')
        latest = max(values, key=lambda item: (item['created_at'], item['id']))
        if any(latest.get(key) != value for key, value in {
                'state': expected['state'], 'environment': environment,
                'environment_url': expected['environment_url'], 'log_url': expected['evidence_url']}.items()):
            raise ValueError('Latest deployment status or evidence link differs')
        page = check['public_environment_page']
        if page['url'] != expected['deployment_url']:
            raise ValueError('Public environment page identity differs')
        # HTTP reachability is not browser/rendered-content proof.
        page_results.append(page['http_status'] == 200 and page['final_url'] == page['url'])
    return {'api_records': 'PASS', 'public_environment_http': 'PASS' if all(page_results) else 'FAIL',
            'status': 'PASS' if all(page_results) else 'PARTIAL',
            'verified_records': len(checks), 'fresh_aws_verification': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--output', type=Path, help='New directory for anonymous live GET readback')
    modes.add_argument('--check', type=Path, help='Replay a saved readback JSON without network calls')
    args = parser.parse_args(argv)
    registration_bytes = REGISTRATION.read_bytes()
    registration = json.loads(registration_bytes)
    if args.check:
        snapshot = load(args.check)
    else:
        if args.output.exists():
            parser.error('Output directory already exists; keep previous observations intact')
        snapshot = collect(registration, registration_bytes)
        args.output.mkdir(parents=True)
        (args.output / 'public_readback.json').write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    result = validate(snapshot, registration, registration_bytes)
    print(json.dumps({**result, 'aws_calls': False, 'network_calls': args.check is None}))


if __name__ == '__main__':
    main()
