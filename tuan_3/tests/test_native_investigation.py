"""Regressions for safe diagnostic evidence and partial AWS access."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock

from botocore.exceptions import ClientError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from investigate_native_errors import iam_timeline, policy_summary, safe_history, summarize_evidence


class NativeInvestigationTests(unittest.TestCase):
    def test_error_retry_pattern_does_not_invent_missing_invocations_or_causality(self):
        probe = {'probes': {'minute_metrics': {'data': [
            {'metric': 'Errors', 'points': [{'timestamp_utc': f'2026-10-18T09:{minute}:00+00:00', 'value': 1}
                                           for minute in ('15', '16', '18')]},
            {'metric': 'Invocations', 'points': []}]}}}
        result = summarize_evidence(probe)
        self.assertEqual(result['errors_sum_in_0915_five_minute_bucket'], 3)
        self.assertTrue(all(r['Invocations'] is None for r in result['observed_minutes']))
        self.assertIsNone(result['whole_window_error_rate_percent'])
        self.assertFalse(result['missing_invocations_explained'])

    def test_history_retains_utc_and_code_without_provider_message_or_identity(self):
        raw = {'eventSource': 'lambda.amazonaws.com', 'readOnly': True, 'managementEvent': True,
               'errorCode': 'AccessDenied', 'errorMessage': 'private provider identity',
               'userIdentity': {'arn': 'private-arn'}, 'requestParameters': {'secret': 'private-value'}}
        result = safe_history([{'CloudTrailEvent': json.dumps(raw), 'EventId': 'private-id',
            'EventTime': datetime(2026, 10, 18, 16, 15, tzinfo=timezone(timedelta(hours=7))),
            'EventName': 'GetFunctionConfiguration'}])
        self.assertEqual(result[0]['timestamp_utc'], '2026-10-18T09:15:00+00:00')
        self.assertEqual(result[0]['error_code'], 'AccessDenied')
        self.assertNotIn('private', json.dumps(result))

    def test_policy_summary_excludes_principal_resource_and_non_time_values(self):
        document = {'Statement': [{'Effect': 'Deny', 'Action': '*', 'Resource': 'private-resource',
            'Principal': 'private-principal', 'Condition': {
                'ArnEquals': {'aws:PrincipalArn': 'private-arn'},
                'DateGreaterThan': {'aws:CurrentTime': '2026-10-18T09:06:03Z'}}}]}
        result = policy_summary(document)
        self.assertNotIn('private', json.dumps(result))
        self.assertEqual(result['statements'][0]['time_conditions'],
                         {'DateGreaterThan': {'aws:CurrentTime': '2026-10-18T09:06:03Z'}})
        self.assertFalse(result['statements'][0]['all_resources'])

    def test_denied_current_policy_read_does_not_erase_available_history(self):
        ct, iam = MagicMock(), MagicMock()
        iam.list_attached_role_policies.return_value = {'AttachedPolicies': [{'PolicyArn': 'private-arn'}]}
        iam.get_policy.side_effect = ClientError({'Error': {'Code': 'AccessDenied', 'Message': 'private'}}, 'GetPolicy')
        raw = {'readOnly': False, 'requestParameters': {'roleName': 'execution-role'}}
        ct.get_paginator.return_value.paginate.return_value = [{'Events': [{
            'CloudTrailEvent': json.dumps(raw), 'EventTime': datetime(2026, 10, 18, 9, tzinfo=timezone.utc),
            'EventName': 'AttachRolePolicy', 'EventId': 'private-id'}]}]
        result = iam_timeline(ct, iam, 'execution-role')
        self.assertTrue(result['changes'][0]['execution_role_named'])
        self.assertEqual(result['current_attached_policies'], [{'status': 'UNAVAILABLE', 'error_code': 'AccessDenied'}])
        self.assertNotIn('private', json.dumps(result))


if __name__ == '__main__':
    unittest.main()
