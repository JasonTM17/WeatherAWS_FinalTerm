"""Reject accidental verification of the canonical app or a different account."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tuan_4/scripts'))
from verify_stack import validate_outputs


class StackOutputBoundary(unittest.TestCase):
    def setUp(self):
        self.account = '123456789012'
        self.outputs = {
            'DataBucket': f'weather-w4-son-{self.account}-us-east-1',
            'FunctionName': 'weather-w4-son-collector',
            'RuleName': 'weather-w4-son-hourly',
            'DatabaseName': 'weather_w4_son',
            'Workgroup': 'weather-w4-son',
            'TopicArn': f'arn:aws:sns:us-east-1:{self.account}:weather-w4-son-alerts',
            'DashboardName': 'WeatherAirQuality-Week4-son',
            'SecretArn': f'arn:aws:secretsmanager:us-east-1:{self.account}:secret:test-abcdef',
        }

    def test_canonical_resources_cannot_substitute_for_new_stack(self):
        for key, value in [('FunctionName', 'WeatherCollectorLambda'),
                           ('DatabaseName', 'weather_aqi_db'),
                           ('Workgroup', 'primary')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_outputs({**self.outputs, key: value}, self.account, 'son')

    def test_other_student_or_account_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_outputs(self.outputs, self.account, 'quyen')
        with self.assertRaises(ValueError):
            validate_outputs(self.outputs, '999999999999', 'son')
        with self.assertRaises(ValueError):
            validate_outputs({**self.outputs, 'SecretArn': self.outputs['SecretArn'].replace(
                self.account, '999999999999')}, self.account, 'son')

    def test_exact_isolated_bindings_are_accepted(self):
        result = validate_outputs(self.outputs, self.account, 'son')
        self.assertEqual(result['DatabaseName'], 'weather_w4_son')


if __name__ == '__main__':
    unittest.main()
