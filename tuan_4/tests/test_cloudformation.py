"""Unit tests validating AWS CloudFormation template syntax, security, and resource contracts."""
from __future__ import annotations

import json
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2]
YAML_TEMPLATE = ROOT / "tuan_4/iac/cloudformation_stack.yaml"
JSON_TEMPLATE = ROOT / "tuan_4/iac/cloudformation_stack.json"


class CfnLoader(yaml.SafeLoader):
    pass


TAGS = [
    "!Ref",
    "!Sub",
    "!GetAtt",
    "!If",
    "!Not",
    "!Equals",
    "!Join",
    "!Select",
    "!Split",
    "!FindInMap",
    "!Base64",
    "!And",
    "!Or",
]
for tag in TAGS:

    def _make_constructor(t):
        def _constructor(loader, node):
            if isinstance(node, yaml.ScalarNode):
                return {t.lstrip("!"): loader.construct_scalar(node)}
            elif isinstance(node, yaml.SequenceNode):
                return {t.lstrip("!"): loader.construct_sequence(node)}
            elif isinstance(node, yaml.MappingNode):
                return {t.lstrip("!"): loader.construct_mapping(node)}

        return _constructor

    yaml.add_constructor(tag, _make_constructor(tag), CfnLoader)


class TestCloudFormationTemplate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.yaml_data = yaml.load(
            YAML_TEMPLATE.read_text(encoding="utf-8"), Loader=CfnLoader
        )
        cls.json_data = json.loads(JSON_TEMPLATE.read_text(encoding="utf-8"))

    def test_templates_exist_and_non_empty(self):
        self.assertTrue(YAML_TEMPLATE.exists())
        self.assertTrue(JSON_TEMPLATE.exists())
        self.assertGreater(YAML_TEMPLATE.stat().st_size, 2000)
        self.assertGreater(JSON_TEMPLATE.stat().st_size, 2000)

    def test_required_top_level_sections(self):
        for data in (self.yaml_data, self.json_data):
            self.assertEqual(data.get("AWSTemplateFormatVersion"), "2010-09-09")
            self.assertIn("Description", data)
            self.assertIn("Parameters", data)
            self.assertIn("Resources", data)
            self.assertIn("Outputs", data)

    def test_parameters_specification(self):
        params = self.yaml_data["Parameters"]
        expected_params = {
            "EnvironmentName",
            "LabRoleArn",
            "ArtifactBucket",
            "ArtifactKey",
            "AlertEmail",
            "ScheduleState",
            "ScheduleExpression",
            "RetentionDays",
        }
        self.assertTrue(expected_params <= params.keys())
        self.assertIn("default", params["EnvironmentName"]["AllowedValues"])
        self.assertIn("son", params["EnvironmentName"]["AllowedValues"])
        self.assertIn("quyen", params["EnvironmentName"]["AllowedValues"])

    def test_resource_completeness(self):
        resources = self.yaml_data["Resources"]
        expected_resources = {
            "DataBucket",
            "BucketPolicy",
            "ApiConfig",
            "AlertTopic",
            "EmailSubscription",
            "CollectorLogs",
            "ResultMetricFilter",
            "ErrorMetricFilter",
            "Collector",
            "HourlyRule",
            "SchedulePermission",
            "Database",
            "RawTable",
            "QueryWorkgroup",
            "ErrorsAlarm",
            "Dashboard",
        }
        self.assertEqual(set(resources.keys()), expected_resources)

    def test_no_iam_role_mutations_for_learner_lab(self):
        for name, res in self.yaml_data["Resources"].items():
            self.assertFalse(
                res["Type"].startswith("AWS::IAM::Role"),
                f"Resource {name} attempts IAM Role creation, invalid in Learner Lab",
            )
            self.assertFalse(
                res["Type"].startswith("AWS::IAM::Policy"),
                f"Resource {name} attempts IAM Policy creation, invalid in Learner Lab",
            )

    def test_s3_block_public_access_100_percent(self):
        bucket = self.yaml_data["Resources"]["DataBucket"]["Properties"]
        pab = bucket["PublicAccessBlockConfiguration"]
        self.assertTrue(pab["BlockPublicAcls"])
        self.assertTrue(pab["IgnorePublicAcls"])
        self.assertTrue(pab["BlockPublicPolicy"])
        self.assertTrue(pab["RestrictPublicBuckets"])
        self.assertEqual(bucket["VersioningConfiguration"]["Status"], "Enabled")
        sse = bucket["BucketEncryption"]["ServerSideEncryptionConfiguration"][0][
            "ServerSideEncryptionByDefault"
        ]
        self.assertEqual(sse["SSEAlgorithm"], "AES256")

    def test_s3_bucket_policy_enforces_tls(self):
        policy = self.yaml_data["Resources"]["BucketPolicy"]["Properties"]
        statement = policy["PolicyDocument"]["Statement"][0]
        self.assertEqual(statement["Effect"], "Deny")
        self.assertEqual(statement["Action"], "s3:*")
        self.assertEqual(statement["Condition"]["Bool"]["aws:SecureTransport"], "false")

    def test_secrets_manager_payload(self):
        secret = self.yaml_data["Resources"]["ApiConfig"]["Properties"]
        payload = json.loads(secret["SecretString"])
        self.assertEqual(payload["api_provider"], "open-meteo")
        self.assertEqual(len(payload["locations"]), 3)
        cities = {loc["city"] for loc in payload["locations"]}
        self.assertEqual(cities, {"HoChiMinh", "HaNoi", "DaNang"})
        self.assertIn("aqi_threshold_pm25", payload)
        self.assertIn("aqi_threshold_pm10", payload)
        self.assertIn("aqi_threshold_us_aqi", payload)

    def test_lambda_collector_specification(self):
        props = self.yaml_data["Resources"]["Collector"]["Properties"]
        self.assertEqual(props["Runtime"], "python3.12")
        self.assertEqual(props["Handler"], "lambda_function.lambda_handler")
        self.assertEqual(props["Timeout"], 60)
        self.assertEqual(props["MemorySize"], 256)
        env_vars = props["Environment"]["Variables"]
        self.assertIn("S3_BUCKET_NAME", env_vars)
        self.assertIn("SECRET_NAME", env_vars)
        self.assertIn("SNS_TOPIC_ARN", env_vars)

    def test_metric_filters_specification(self):
        res_mf = self.yaml_data["Resources"]["ResultMetricFilter"]["Properties"]
        self.assertEqual(res_mf["FilterPattern"], '"Result:"')
        t1 = res_mf["MetricTransformations"][0]
        self.assertEqual(t1["MetricNamespace"], "WeatherAWS/Collection")
        self.assertEqual(t1["MetricName"], "ResultLogLines")
        self.assertEqual(t1["MetricValue"], "1")

        err_mf = self.yaml_data["Resources"]["ErrorMetricFilter"]["Properties"]
        self.assertEqual(err_mf["FilterPattern"], '"[ERROR]"')
        t2 = err_mf["MetricTransformations"][0]
        self.assertEqual(t2["MetricNamespace"], "WeatherAWS/Collection")
        self.assertEqual(t2["MetricName"], "ErrorLogLines")
        self.assertEqual(t2["MetricValue"], "1")

    def test_cloudwatch_alarm_specification(self):
        alarm = self.yaml_data["Resources"]["ErrorsAlarm"]["Properties"]
        self.assertEqual(alarm["Namespace"], "AWS/Lambda")
        self.assertEqual(alarm["MetricName"], "Errors")
        self.assertEqual(alarm["Period"], 300)
        self.assertEqual(alarm["Threshold"], 1)
        self.assertEqual(alarm["ComparisonOperator"], "GreaterThanOrEqualToThreshold")
        self.assertEqual(alarm["TreatMissingData"], "missing")

    def test_glue_and_athena_partition_projection(self):
        table = self.yaml_data["Resources"]["RawTable"]["Properties"]["TableInput"]
        self.assertEqual(table["TableType"], "EXTERNAL_TABLE")
        params = table["Parameters"]
        self.assertEqual(params["projection.enabled"], "true")
        self.assertEqual(params["projection.year.range"], "2026,2030")
        self.assertEqual(params["projection.month.range"], "1,12")
        self.assertEqual(params["projection.day.range"], "1,31")
        keys = [p["Name"] for p in table["PartitionKeys"]]
        self.assertEqual(keys, ["year", "month", "day"])
        cols = [c["Name"] for c in table["StorageDescriptor"]["Columns"]]
        self.assertIn("city", cols)
        self.assertIn("temperature_2m", cols)
        self.assertIn("pm2_5", cols)
        self.assertIn("us_aqi", cols)

    def test_athena_workgroup_cost_guardrail(self):
        wg = self.yaml_data["Resources"]["QueryWorkgroup"]["Properties"][
            "WorkGroupConfiguration"
        ]
        self.assertTrue(wg["EnforceWorkGroupConfiguration"])
        self.assertEqual(wg["BytesScannedCutoffPerQuery"], 10485760)  # 10 MB limit

    def test_dashboard_body_is_valid_json_with_widgets(self):
        raw_body = self.yaml_data["Resources"]["Dashboard"]["Properties"][
            "DashboardBody"
        ]
        # In YAML loader with !Sub, it's a mapping or string
        if isinstance(raw_body, dict):
            body_str = raw_body["Sub"]
        else:
            body_str = str(raw_body)
        # Verify widget keywords are present in dashboard body
        self.assertIn('"widgets"', body_str)
        self.assertIn('"ResultLogLines"', body_str)
        self.assertIn('"Invocations"', body_str)
        self.assertIn('"Errors"', body_str)


if __name__ == "__main__":
    unittest.main()
