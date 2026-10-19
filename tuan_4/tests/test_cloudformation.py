"""Regression checks for the single deployable infrastructure definition."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tuan_4/scripts'))
from prepare_stack import TEMPLATE, validate_contract


class TestCloudFormationTemplate(unittest.TestCase):
    def setUp(self):
        self.template = json.loads(TEMPLATE.read_text(encoding='utf-8'))

    def test_no_placeholder_collector_can_claim_three_records(self):
        code = self.template['Resources']['Collector']['Properties']['Code']
        self.assertEqual(set(code), {'S3Bucket','S3Key','S3ObjectVersion'})
        self.assertNotIn('Default', self.template['Parameters']['ArtifactBucket'])
        self.assertNotIn('Default', self.template['Parameters']['ArtifactVersion'])

    def test_log_metrics_are_environment_scoped_and_do_not_fabricate_zeroes(self):
        for name in ('ResultMetricFilter','ErrorMetricFilter'):
            props = self.template['Resources'][name]['Properties']
            self.assertEqual(props['LogGroupName'], {'Ref':'CollectorLogs'})
            metric = props['MetricTransformations'][0]
            self.assertIn('${EnvironmentName}',metric['MetricNamespace']['Fn::Sub'])
            self.assertNotIn('DefaultValue',metric)

    def test_partition_placeholders_are_not_cloudformation_variables(self):
        location = self.template['Resources']['RawTable']['Properties']['TableInput']['Parameters']['storage.location.template']
        self.assertIn('Fn::Join',location)
        self.assertIn('${year}',location['Fn::Join'][1][-1])
        self.assertEqual(validate_contract(self.template)['resource_count'],17)


if __name__ == '__main__':
    unittest.main()
