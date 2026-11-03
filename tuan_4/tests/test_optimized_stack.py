"""Unit test to validate the optimized CloudFormation template."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OPTIMIZED_TEMPLATE = ROOT / 'tuan_4/infrastructure/weather-stack-optimized.json'


class TestOptimizedStack(unittest.TestCase):
    def setUp(self):
        self.assertTrue(OPTIMIZED_TEMPLATE.exists(), 'Optimized template must exist')
        with open(OPTIMIZED_TEMPLATE, 'r', encoding='utf-8') as f:
            self.template = json.load(f)

    def test_optimized_resources_present(self):
        resources = self.template.get('Resources', {})
        self.assertIn('CollectorDeadLetterQueue', resources, 'DLQ SQS must be present')
        self.assertIn('ConfigParameter', resources, 'SSM Parameter must be present')
        self.assertIn('DataBucket', resources, 'DataBucket must be present')

    def test_s3_lifecycle_rule_configured(self):
        bucket_props = self.template['Resources']['DataBucket']['Properties']
        lifecycle = bucket_props.get('LifecycleConfiguration', {})
        rules = lifecycle.get('Rules', [])
        self.assertTrue(any(r['Id'] == 'ExpireAthenaQueryResults' and r['ExpirationInDays'] == 7 for r in rules),
                        'Athena query results must expire in 7 days')

    def test_lambda_memory_tuning_and_dlq(self):
        collector_props = self.template['Resources']['Collector']['Properties']
        self.assertEqual(collector_props.get('MemorySize'), 128, 'Memory must be tuned to 128MB')
        dlq_config = collector_props.get('DeadLetterConfig', {})
        self.assertIn('TargetArn', dlq_config, 'Lambda must have DeadLetterConfig pointing to SQS')


if __name__ == '__main__':
    unittest.main()
