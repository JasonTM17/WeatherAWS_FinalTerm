"""Public readback regressions: a summary or an inaccessible UI is not API proof."""
import copy
import json
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tuan_4/scripts'))
import verify_github_deployments as verifier


class PublicDeploymentEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.source = verifier.REGISTRATION.read_bytes()
        self.registration = json.loads(self.source)
        self.responses = {}
        records = []
        for expected in self.registration['records']:
            identity = expected['deployment_id']
            record = {'id': identity, 'environment': expected['environment'],
                      'sha': expected['evidence_commit'], 'ref': expected['evidence_commit'],
                      'task': 'deploy:cloudformation', 'created_at': expected['github_record_created_at'],
                      'updated_at': expected['github_record_created_at'],
                      'payload': {'registration_only': True, 'fresh_aws_verification': False,
                          'evidence_commit': expected['evidence_commit'],
                          'stack_name': expected['stack_name'], 'evidence_url': expected['evidence_url']}}
            records.append(record)
            self.add(f'{verifier.API}/deployments/{identity}', record)
            self.add(f'{verifier.API}/deployments/{identity}/statuses', [{
                'id': identity + 1, 'created_at': '2026-10-21T02:10:00Z',
                'state': expected['state'], 'environment': expected['environment'],
                'environment_url': expected['environment_url'], 'log_url': expected['evidence_url']}])
            self.add(expected['deployment_url'], None, status=404)
        self.add(f'{verifier.API}/deployments?per_page=100', records)

    def add(self, url, body, status=200):
        self.responses[url] = {'url': url, 'final_url': url, 'http_status': status,
                               'github_request_id': 'test-request-id', 'body': body}

    def snapshot(self):
        return verifier.collect(self.registration, self.source,
                                fetch=lambda url, *args: copy.deepcopy(self.responses[url]))

    def validate(self, snapshot):
        return verifier.validate(snapshot, self.registration, self.source)

    def test_existing_api_records_do_not_make_public_ui_pass(self):
        result = self.validate(self.snapshot())
        self.assertEqual(result['api_records'], 'PASS')
        self.assertEqual(result['public_environment_http'], 'FAIL')
        self.assertEqual(result['status'], 'PARTIAL')

    def test_deleted_or_inaccessible_api_record_fails(self):
        snapshot = self.snapshot()
        snapshot['checks'][0]['deployment']['http_status'] = 404
        with self.assertRaises(ValueError):
            self.validate(snapshot)

    def test_wrong_identity_commit_date_payload_or_status_fails(self):
        for part, key, value in [('fields', 'id', 999), ('fields', 'environment', 'other'),
                                 ('fields', 'sha', '0' * 40), ('fields', 'created_at', '2026-10-22T00:00:00Z'),
                                 ('payload', 'registration_only', False),
                                 ('payload', 'fresh_aws_verification', True)]:
            with self.subTest(part=part, key=key):
                snapshot = self.snapshot()
                snapshot['checks'][0]['deployment'][part][key] = value
                with self.assertRaises(ValueError):
                    self.validate(snapshot)
        for key, value in [('state', 'failure'), ('environment', 'other'), ('log_url', 'https://example.com')]:
            with self.subTest(status_key=key):
                snapshot = self.snapshot()
                snapshot['checks'][0]['statuses']['records'][0][key] = value
                with self.assertRaises(ValueError):
                    self.validate(snapshot)

    def test_empty_statuses_missing_list_membership_or_duplicate_check_fails(self):
        snapshot = self.snapshot()
        snapshot['checks'][0]['statuses']['records'] = []
        with self.assertRaises(ValueError):
            self.validate(snapshot)
        snapshot = self.snapshot()
        snapshot['list_response']['records'] = []
        with self.assertRaises(ValueError):
            self.validate(snapshot)
        snapshot = self.snapshot()
        snapshot['checks'][1] = snapshot['checks'][0]
        with self.assertRaises(ValueError):
            self.validate(snapshot)

    def test_newer_failure_is_not_hidden_by_older_success(self):
        snapshot = self.snapshot()
        later = dict(snapshot['checks'][0]['statuses']['records'][0],
                     id=99999999999, state='failure', created_at='2026-10-22T00:00:00Z')
        snapshot['checks'][0]['statuses']['records'].append(later)
        with self.assertRaises(ValueError):
            self.validate(snapshot)

    def test_redirect_login_or_authentication_cannot_be_public_proof(self):
        snapshot = self.snapshot()
        snapshot['checks'][0]['deployment']['final_url'] = 'https://github.com/login'
        with self.assertRaises(ValueError):
            self.validate(snapshot)
        snapshot = self.snapshot()
        snapshot['access_mode'] = 'authenticated'
        with self.assertRaises(ValueError):
            self.validate(snapshot)

    def test_request_is_get_without_auth_cookie_or_credentials(self):
        class Response:
            status = 200
            url = f'{verifier.API}/deployments'
            headers = {'x-github-request-id': 'test', 'date': 'test-date'}
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return b'[]'
        with patch.object(verifier.urllib.request, 'urlopen', return_value=Response()) as open_url:
            verifier.get_public(Response.url)
        request = open_url.call_args.args[0]
        self.assertEqual(request.get_method(), 'GET')
        self.assertNotIn('authorization', {key.lower() for key, _ in request.header_items()})
        self.assertNotIn('cookie', {key.lower() for key, _ in request.header_items()})

    def test_published_readback_preserves_api_and_ui_outcomes_separately(self):
        snapshot = verifier.load(ROOT / 'tuan_4/results/github_deployment_readback_2026_10_21/public_readback.json')
        result = self.validate(snapshot)
        self.assertEqual(result['api_records'], 'PASS')
        self.assertEqual(result['public_environment_http'], 'FAIL')
        self.assertFalse(result['fresh_aws_verification'])

    def test_current_report_links_do_not_require_deployment_environment_ui(self):
        for relative in ['README.md', 'tuan_4/README.md', 'tuan_4/docs/SUBMISSION.md']:
            with self.subTest(document=relative):
                text = (ROOT / relative).read_text(encoding='utf-8')
                links = re.findall(r'\]\(([^)]+)\)', text)
                self.assertFalse(any(link.startswith(verifier.WEB + '/deployments/week4-') for link in links))
                self.assertIn('/tree/58fdf22da9b048e457aa88e823606cf424ec5caf/tuan_4/results/advanced_live_2026_10_20/stacks/', text)


if __name__ == '__main__':
    unittest.main()
