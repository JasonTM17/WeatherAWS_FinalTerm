"""Contract and failure-boundary regressions for final-week verification."""
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import zipfile

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import prepare_stack as stack
import session_control as control
import verify_environment as verify
import run_demo_check as demo
from common import digest
from dashboard import reconcile_periods


class TemplateTests(unittest.TestCase):
    def setUp(self):
        self.template = json.loads(stack.TEMPLATE.read_text(encoding='utf-8'))

    def test_complete_stack_has_no_iam_mutation(self):
        self.assertEqual(stack.validate_contract(self.template)['resource_count'], 15)

    def test_alarm_topic_policy_must_bind_source_alarm(self):
        statement = self.template['Resources']['AlarmTopicPolicy']['Properties']['PolicyDocument']['Statement'][0]
        del statement['Condition']['ArnEquals']['aws:SourceArn']
        with self.assertRaises(ValueError):
            stack.validate_contract(self.template)

    def test_public_storage_change_is_rejected(self):
        self.template['Resources']['DataBucket']['Properties']['PublicAccessBlockConfiguration']['BlockPublicPolicy'] = False
        with self.assertRaises(ValueError):
            stack.validate_contract(self.template)

    def test_starting_an_automatic_schedule_is_rejected(self):
        self.template['Resources']['HourlyRule']['Properties']['State'] = 'ENABLED'
        with self.assertRaises(ValueError):
            stack.validate_contract(self.template)

    def test_bucket_replacement_must_preserve_evidence(self):
        del self.template['Resources']['DataBucket']['UpdateReplacePolicy']
        with self.assertRaises(ValueError):
            stack.validate_contract(self.template)

    def test_catalog_schema_equals_collector_contract(self):
        table = self.template['Resources']['RawTable']['Properties']['TableInput']
        names = {x['Name'] for x in table['StorageDescriptor']['Columns'] + table['PartitionKeys']}
        self.assertEqual(names, verify.REQUIRED)
        projection = table['Parameters']['storage.location.template']['Fn::Join'][1][-1]
        self.assertIn('year=${year}/month=${month}/day=${day}', projection)

    def test_artifact_contains_canonical_source_and_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp)/'a', Path(tmp)/'b'
            stack.build(a)
            stack.build(b)
            self.assertEqual((a/'collector.zip').read_bytes(), (b/'collector.zip').read_bytes())
            with zipfile.ZipFile(a/'collector.zip') as archive:
                self.assertEqual(archive.namelist(), ['lambda_function.py'])
                source = (stack.ROOT/'tuan_2/lambda/lambda_function.py').read_text(encoding='utf-8').replace('\r\n', '\n').encode()
                self.assertEqual(archive.read('lambda_function.py'), source)


class CostTests(unittest.TestCase):
    class CE:
        def __init__(self, repeat=False):
            self.calls = []
            self.repeat = repeat

        def get_cost_and_usage(self, **kwargs):
            self.calls.append(kwargs)
            second = len(self.calls) > 1
            day = '2026-10-19' if not second or self.repeat else '2026-10-20'
            result = {'ResultsByTime': [{'TimePeriod': {'Start': day}, 'Estimated': True,
                'Groups': [{'Keys': ['CloudWatch', 'Usage'],
                    'Metrics': {'UnblendedCost': {'Amount': '-0.0000000764', 'Unit': 'USD'}}}]}]}
            if not second:
                result['NextPageToken'] = 'next'
            return result

    def test_billing_paginates_and_preserves_negative_precision(self):
        service = self.CE()
        rows = verify.costs(service, '2026-10-19', '2026-10-21')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['amount_usd'], '-7.64E-8')
        self.assertEqual(service.calls[1]['NextPageToken'], 'next')
        self.assertEqual(service.calls[0]['GroupBy'][1]['Key'], 'RECORD_TYPE')

    def test_duplicate_billing_group_is_rejected(self):
        with self.assertRaises(ValueError):
            verify.costs(self.CE(repeat=True), '2026-10-19', '2026-10-21')

    def test_empty_billing_groups_are_not_zero_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(verify, 'client'), patch.object(verify, 'costs', return_value=[]):
                result = verify.cost_check(None, Path(tmp), '2026-10-19', '2026-10-20')
        self.assertIsNone(result['total_unblended_usd'])
        self.assertEqual(result['status'], 'NOT_AVAILABLE')


class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.state = {'account_fingerprint': 'account', 'binding_fingerprint': 'binding', 'original_state': 'ENABLED'}
        self.events = self.Events(self.state)

    class Events:
        def __init__(self, state):
            self.state = state
            self.calls = []
        def enable_rule(self, **kwargs):
            self.calls.append('enable')
            self.state['original_state'] = 'ENABLED'
        def disable_rule(self, **kwargs):
            self.calls.append('disable')
            self.state['original_state'] = 'DISABLED'

    def get_binding(self, _):
        return self.events, dict(self.state)

    def test_preview_never_changes_schedule(self):
        with patch.object(control, 'binding', side_effect=self.get_binding):
            control.control(None, 'pause', control.BACKUPS/'test.json', apply=False)
        self.assertEqual(self.events.calls, [])

    def test_pause_restore_preserve_original_state(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(control, 'binding', side_effect=self.get_binding):
            with patch.object(control, 'BACKUPS', Path(tmp)):
                file = Path(tmp)/'state.json'
                control.control(None, 'pause', file, apply=True)
                self.assertEqual(self.state['original_state'], 'DISABLED')
                control.control(None, 'restore', file, apply=True)
                self.assertEqual(self.events.calls, ['disable','enable'])

    def test_restore_does_not_enable_a_previously_disabled_rule(self):
        self.state['original_state'] = 'DISABLED'
        with tempfile.TemporaryDirectory() as tmp, patch.object(control, 'binding', side_effect=self.get_binding):
            with patch.object(control, 'BACKUPS', Path(tmp)):
                file = Path(tmp)/'state.json'
                control.control(None, 'pause', file, apply=True)
                control.control(None, 'restore', file, apply=True)
        self.assertEqual(self.events.calls, [])

    def test_changed_binding_blocks_restore(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(control, 'binding', side_effect=self.get_binding):
            with patch.object(control, 'BACKUPS', Path(tmp)):
                file = Path(tmp)/'state.json'
                control.control(None, 'pause', file, apply=True)
                self.state['binding_fingerprint'] = 'other-target'
                with self.assertRaises(ValueError):
                    control.control(None, 'restore', file, apply=True)
        self.assertEqual(self.events.calls, ['disable'])

    def test_recovery_after_unacknowledged_disable_keeps_backup(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(control, 'binding', side_effect=self.get_binding):
            with patch.object(control, 'BACKUPS', Path(tmp)):
                file = Path(tmp)/'state.json'
                file.write_text(json.dumps(dict(self.state, status='PREPARED')), encoding='utf-8')
                self.state['original_state'] = 'DISABLED'
                control.control(None, 'restore', file, apply=True)
        self.assertEqual(self.events.calls, ['enable'])

    def test_state_cannot_be_written_to_public_source(self):
        with self.assertRaises(ValueError):
            control.private_path(control.ROOT/'tuan_4/state.json')

    def test_failed_status_publish_preserves_recovery_record(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(control, 'binding', side_effect=self.get_binding):
            with patch.object(control, 'BACKUPS', Path(tmp)):
                file = Path(tmp)/'state.json'
                with patch.object(control.os, 'replace', side_effect=OSError('disk unavailable')):
                    with self.assertRaises(OSError):
                        control.control(None, 'pause', file, apply=True)
                self.assertEqual(json.loads(file.read_text())['status'], 'PREPARED')
                self.assertEqual(self.state['original_state'], 'DISABLED')
                control.control(None, 'restore', file, apply=True)
                self.assertEqual(self.state['original_state'], 'ENABLED')


class EvidenceTests(unittest.TestCase):
    def test_schedule_with_wrong_frequency_is_not_accepted(self):
        events, lamb = MagicMock(), MagicMock()
        config = {'FunctionArn': 'selected-function'}
        events.describe_rule.return_value = {'Arn':'selected-rule', 'State':'ENABLED', 'ScheduleExpression':'rate(1 minute)'}
        targets, names = MagicMock(), MagicMock()
        targets.paginate.return_value = [{'Targets':[{'Arn':'selected-function'}]}]
        names.paginate.return_value = [{'RuleNames':['WeatherCollectionSchedule']}]
        events.get_paginator.side_effect = lambda name: targets if name == 'list_targets_by_rule' else names
        lamb.get_policy.return_value = {'Policy':'{}'}
        with patch.object(verify, 'client', side_effect=lambda _, service: events if service == 'events' else lamb):
            with patch('check_operations.policy_allows', return_value=True):
                self.assertEqual(verify.rule_check(None, config)['status'], 'FAIL')
                events.describe_rule.return_value['ScheduleExpression'] = 'rate(1 hour)'
                self.assertEqual(verify.rule_check(None, config)['status'], 'PASS')

    def test_absent_invocations_remain_missing_even_with_errors(self):
        result = reconcile_periods([{'namespace': 'AWS/Lambda', 'metric': 'Errors', 'statistic': 'Sum',
            'timestamp_utc': '2026-10-19T10:00:00+00:00', 'value': 3}])
        self.assertIsNone(result['overall_error_rate_percent'])
        self.assertEqual(result['periods'][0]['status'], 'MISSING_INVOCATIONS')

    def test_exception_message_is_not_exported(self):
        with tempfile.TemporaryDirectory() as tmp:
            def fail():
                raise ValueError('sensitive provider detail')
            verify.capture(Path(tmp), 'check', fail)
            self.assertNotIn('sensitive', (Path(tmp)/'check.json').read_text())

    def test_wildcard_role_is_not_called_least_privilege(self):
        result = verify.minimum_policy_findings([{'Statement': [{'Effect':'Allow','Action':'*','Resource':'*'}]}])
        self.assertEqual(result['allow_statements_requiring_scope_review'], 1)
        self.assertFalse(result['effective_least_privilege_proven'])

    def test_alert_comparison_does_not_claim_email_receipt(self):
        rows = [{'record_id': str(i), 'pm2_5': 36 if i == 0 else 1, 'us_aqi': 50} for i in range(3)]
        result = demo.comparison(rows, {'alerts_sent': 1}, {})
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['email_receipt'], 'PENDING_RECIPIENT_CONFIRMATION')

    def test_alert_boundaries_include_equality_and_use_or(self):
        rows = [{'record_id': str(i), 'pm2_5': pm, 'us_aqi': aqi}
                for i,(pm,aqi) in enumerate([(35.5,99),(1,100),(35.4,99)])]
        self.assertEqual(demo.comparison(rows, {'alerts_sent':2}, {})['status'], 'PASS')

    def test_sql_uses_only_exact_new_record_ids_and_date_partitions(self):
        # Actual canonical collector ID format, observed in the controlled AWS invocation.
        rows = [{'record_id':'HoChiMinh_20261019123807_56113a', 'year':2026,'month':'10','day':'19'}]
        self.assertIn("record_id IN ('HoChiMinh_20261019123807_56113a')", demo.exact_query(rows))
        rows[0]['record_id'] = "' OR 1=1"
        with self.assertRaises(ValueError):
            demo.exact_query(rows)


if __name__ == '__main__':
    unittest.main()
