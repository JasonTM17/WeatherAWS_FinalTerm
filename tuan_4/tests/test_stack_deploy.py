"""Fail closed before touching other resources or accepting mutable artifacts."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tuan_4/scripts'))
import deploy_stack as deploy


class StackDeploymentGuards(unittest.TestCase):
    def setUp(self):
        self.template=json.loads((ROOT/'tuan_4/infrastructure/weather-stack.json').read_text())

    def test_private_journal_cannot_be_written_to_public_results(self):
        with self.assertRaisesRegex(ValueError,'ignored output'):
            deploy.output_path(ROOT/'tuan_4/results/private.json')

    def test_wrong_environment_stack_is_not_adopted(self):
        with self.assertRaises(ValueError):
            deploy.owned_stack({'Tags':[{'Key':'Project','Value':deploy.PROJECT},{'Key':'Environment','Value':'quyen'}]},'son')

    def test_existing_dashboard_blocks_all_later_service_calls(self):
        cw=Mock();cw.get_dashboard.return_value={'DashboardBody':'existing dashboard'}
        with patch.object(deploy,'client',return_value=cw) as clients:
            with self.assertRaisesRegex(ValueError,'dashboard'):
                deploy.ensure_names_absent(Mock(),'123456789012','son',self.template)
        self.assertEqual(clients.call_count,1)
        cw.put_dashboard.assert_not_called()

    def test_dashboard_access_denied_is_not_absence(self):
        cw=Mock();cw.get_dashboard.side_effect=ClientError({'Error':{'Code':'AccessDenied','Message':'denied'}},'GetDashboard')
        with patch.object(deploy,'client',return_value=cw):
            with self.assertRaises(ClientError):
                deploy.ensure_names_absent(Mock(),'123456789012','son',self.template)

    def test_existing_topic_blocks_stack_and_artifact_mutations(self):
        cw=Mock();sns=Mock()
        cw.get_dashboard.side_effect=ClientError({'Error':{'Code':'ResourceNotFound','Message':'absent'}},'GetDashboard')
        sns.get_topic_attributes.return_value={'Attributes':{'TopicArn':'existing'}}
        with patch.object(deploy,'client',side_effect=lambda sess,service: {'cloudwatch':cw,'sns':sns}[service]):
            with self.assertRaisesRegex(ValueError,'topic'):
                deploy.ensure_names_absent(Mock(),'123456789012','son',self.template)
        cw.describe_alarms.assert_not_called()
        sns.create_topic.assert_not_called()

    def test_unowned_artifact_bucket_is_never_modified(self):
        s3=Mock();s3.get_bucket_tagging.return_value={'TagSet':[{'Key':'Project','Value':'different-project'}]}
        with patch.object(deploy,'client',return_value=s3):
            with self.assertRaisesRegex(ValueError,'unrelated'):
                deploy.artifact(Mock(),'123456789012','son',ROOT,{})
        s3.put_bucket_versioning.assert_not_called()
        s3.put_object.assert_not_called()

    def test_multiple_confirmed_recipients_require_exact_selection(self):
        sns=Mock()
        sns.get_paginator.return_value.paginate.return_value=[{'Subscriptions':[
            {'Protocol':'email','SubscriptionArn':'arn:first','Endpoint':'first@example.edu'},
            {'Protocol':'email','SubscriptionArn':'arn:second','Endpoint':'second@example.edu'}]}]
        with patch.object(deploy,'client',return_value=sns):
            with self.assertRaises(ValueError):deploy.confirmed_email(Mock(),'arn:topic')
            selected=deploy.confirmed_email(Mock(),'arn:topic',deploy.digest(b'second@example.edu')[:12])
            self.assertEqual(selected,'second@example.edu')
            with self.assertRaises(ValueError):deploy.confirmed_email(Mock(),'arn:topic','wrong-choice')


if __name__=='__main__':unittest.main()
