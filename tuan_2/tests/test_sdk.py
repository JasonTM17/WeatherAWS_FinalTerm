"""Focused SDK regressions without live credentials or cloud resources."""

import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from athena_export import (
    QUERY_FILES,
    AthenaExporter,
    AthenaQueryError,
    copy_snapshot,
    main,
)
from aws_project import RULE, AwsProject


def error(code):
    return ClientError({"Error": {"Code": code, "Message": "Test error"}}, "Test")


class TestSdk(unittest.TestCase):
    def exporter(self):
        athena, s3 = MagicMock(), MagicMock()
        athena.start_query_execution.return_value = {"QueryExecutionId": "query-1"}
        return AthenaExporter(
            athena, s3, "weather_aqi_db", "s3://bucket/results/", sleep=lambda _: None
        )

    def test_failed_query_preserves_existing_csv(self):
        exporter = self.exporter()
        exporter.athena.get_query_execution.return_value = {
            "QueryExecution": {"Status": {"State": "FAILED"}}
        }
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "data.csv"
            target.write_bytes(b"original")
            with self.assertRaises(AthenaQueryError):
                exporter.export("query", "SELECT 1", target)
            self.assertEqual(target.read_bytes(), b"original")
            exporter.s3.get_object.assert_not_called()

    def test_timeout_cancels_query(self):
        exporter = self.exporter()
        exporter.clock = MagicMock(side_effect=[0, 301])
        exporter.athena.get_query_execution.return_value = {
            "QueryExecution": {"Status": {"State": "RUNNING"}}
        }
        with self.assertRaises(TimeoutError):
            exporter.execute("SELECT 1")
        exporter.athena.stop_query_execution.assert_called_once_with(
            QueryExecutionId="query-1"
        )

    def test_pagination_keeps_null_and_header_once(self):
        exporter = self.exporter()
        exporter.s3.get_object.side_effect = error("AccessDenied")
        metadata = {"ColumnInfo": [{"Name": "city"}, {"Name": "value"}]}
        exporter.athena.get_query_results.side_effect = [
            {
                "ResultSet": {
                    "ResultSetMetadata": metadata,
                    "Rows": [
                        {"Data": [{"VarCharValue": "city"}, {"VarCharValue": "value"}]},
                        {"Data": [{"VarCharValue": "A"}, {}]},
                    ],
                },
                "NextToken": "page2",
            },
            {
                "ResultSet": {
                    "ResultSetMetadata": metadata,
                    "Rows": [{"Data": [{"VarCharValue": "B"}, {"VarCharValue": "2"}]}],
                }
            },
        ]
        blob = exporter.csv_bytes(
            "query-1",
            {"ResultConfiguration": {"OutputLocation": "s3://bucket/key.csv"}},
        )
        self.assertEqual(
            list(csv.reader(io.StringIO(blob.decode()))),
            [["city", "value"], ["A", ""], ["B", "2"]],
        )
        self.assertEqual(
            exporter.athena.get_query_results.call_args_list[1].kwargs["NextToken"],
            "page2",
        )

    def test_s3_csv_preserved_byte_for_byte(self):
        exporter = self.exporter()
        blob = b'"city","value"\r\n"A","1.00"\r\n'
        exporter.s3.get_object.return_value = {"Body": io.BytesIO(blob)}
        self.assertEqual(
            exporter.csv_bytes(
                "query-1",
                {"ResultConfiguration": {"OutputLocation": "s3://bucket/key.csv"}},
            ),
            blob,
        )

    def test_invalid_csv_preserves_existing_export(self):
        invalid_results = [
            b"",
            b"city,city\nA,B\n",
            b"city,\nA,B\n",
            b"city,value\nA\n",
            b"city,value\nA,1,extra\n",
            b'city,value\n"A,1\n',
            b"city,value\nA,\xff\n",
        ]
        for blob in invalid_results:
            with self.subTest(blob=blob), tempfile.TemporaryDirectory() as directory:
                exporter = self.exporter()
                exporter.athena.get_query_execution.return_value = {
                    "QueryExecution": {
                        "Status": {"State": "SUCCEEDED"},
                        "ResultConfiguration": {
                            "OutputLocation": "s3://bucket/key.csv"
                        },
                    }
                }
                exporter.s3.get_object.return_value = {"Body": io.BytesIO(blob)}
                target = Path(directory) / "data.csv"
                target.write_bytes(b"original")
                with self.assertRaises(AthenaQueryError):
                    exporter.export("query", "SELECT city, value", target)
                self.assertEqual(target.read_bytes(), b"original")

    def test_header_only_and_quoted_newlines_are_valid_csv(self):
        for blob, expected in [
            (b'"city","value"\r\n', []),
            (b'"city","value"\n"A\nB","1"\n', [{"city": "A\nB", "value": "1"}]),
        ]:
            with self.subTest(blob=blob), tempfile.TemporaryDirectory() as directory:
                exporter = self.exporter()
                exporter.athena.get_query_execution.return_value = {
                    "QueryExecution": {
                        "Status": {"State": "SUCCEEDED"},
                        "ResultConfiguration": {
                            "OutputLocation": "s3://bucket/key.csv"
                        },
                    }
                }
                exporter.s3.get_object.return_value = {"Body": io.BytesIO(blob)}
                target = Path(directory) / "data.csv"
                result = exporter.export("query", "SELECT city, value", target)
                self.assertEqual(target.read_bytes(), blob)
                self.assertEqual(result["rows"], expected)
                self.assertEqual(result["row_count"], len(expected))

    def test_header_only_first_page_keeps_equal_data_row(self):
        exporter = self.exporter()
        exporter.s3.get_object.side_effect = error("AccessDenied")
        metadata = {"ColumnInfo": [{"Name": "city"}, {"Name": "value"}]}
        row = {"Data": [{"VarCharValue": "city"}, {"VarCharValue": "value"}]}
        exporter.athena.get_query_results.side_effect = [
            {
                "ResultSet": {"ResultSetMetadata": metadata, "Rows": [row]},
                "NextToken": "page2",
            },
            {"ResultSet": {"ResultSetMetadata": metadata, "Rows": [row]}},
        ]
        blob = exporter.csv_bytes(
            "query-1",
            {"ResultConfiguration": {"OutputLocation": "s3://bucket/key.csv"}},
        )
        self.assertEqual(
            list(csv.reader(io.StringIO(blob.decode()))),
            [["city", "value"], ["city", "value"]],
        )

    def test_invalid_credentials_do_not_trigger_fallback(self):
        exporter = self.exporter()
        exporter.s3.get_object.side_effect = error("InvalidAccessKeyId")
        with self.assertRaises(ClientError):
            exporter.csv_bytes(
                "query-1",
                {"ResultConfiguration": {"OutputLocation": "s3://bucket/key.csv"}},
            )
        exporter.athena.get_query_results.assert_not_called()

    def test_offline_copy_identifies_saved_source(self):
        with tempfile.TemporaryDirectory() as directory:
            copy_snapshot(directory, ["avg_aqi_by_city"])
            self.assertEqual(
                (Path(directory) / "avg_aqi_by_city.csv").read_bytes(),
                (ROOT / "results/athena_queries/avg_aqi_by_city.csv").read_bytes(),
            )
            self.assertEqual(
                json.loads((Path(directory) / "export_manifest.json").read_text())[
                    "mode"
                ],
                "saved-snapshot",
            )

    def test_offline_copy_cannot_overwrite_source(self):
        with self.assertRaises(ValueError):
            copy_snapshot(ROOT / "results/athena_queries")

    def test_export_uses_selected_database_in_every_query(self):
        for database in ("weather_aqi_db", "weekly_data", 'weekly"data'):
            with (
                self.subTest(database=database),
                tempfile.TemporaryDirectory() as directory,
            ):
                with (
                    patch("athena_export.boto3.Session") as session_type,
                    patch("athena_export.AthenaExporter") as exporter_type,
                ):
                    session_type.return_value.client.return_value.get_caller_identity.return_value = {
                        "Account": "123456789012"
                    }
                    exporter_type.return_value.export.return_value = {
                        "name": "query",
                        "query_id": "query-1",
                        "status": "SUCCEEDED",
                        "row_count": 0,
                        "execution_time_ms": 0,
                        "bytes_scanned": 0,
                    }
                    main(["--database", database, "--output", directory])
                    self.assertEqual(exporter_type.call_args.args[2], database)
                    calls = exporter_type.return_value.export.call_args_list
                    self.assertEqual(len(calls), len(QUERY_FILES))
                    for call, (name, filename) in zip(calls, QUERY_FILES.items()):
                        original = (ROOT / "athena" / filename).read_text(
                            encoding="utf-8"
                        )
                        qualifier = '"' + database.replace('"', '""') + '"'
                        expected = (
                            original
                            if database == "weather_aqi_db"
                            else original.replace("weather_aqi_db.", qualifier + ".")
                        )
                        self.assertEqual(
                            call.args, (name, expected, Path(directory) / f"{name}.csv")
                        )
        for database in ("", " ", "weekly\x00data"):
            with (
                self.subTest(database=database),
                patch("athena_export.boto3.Session") as session_type,
            ):
                with self.assertRaises(ValueError):
                    main(["--database", database])
                session_type.assert_not_called()

    def project(self):
        project = AwsProject(session=MagicMock())
        project._identity = {
            "Account": "123456789012",
            "Arn": "arn:aws:iam::123456789012:role/LabRole",
        }
        return project

    def test_s3_access_denied_is_not_missing(self):
        project = self.project()
        s3 = project.client("s3")
        s3.head_bucket.side_effect = error("403")
        with self.assertRaises(ClientError):
            project.setup_s3()
        s3.create_bucket.assert_not_called()

    def test_existing_lambda_update_restores_declared_runtime_and_handler(self):
        project = self.project()
        client = project.client("lambda")
        client.get_function_configuration.return_value = {
            "Runtime": "python3.11",
            "Handler": "old_module.handler",
            "Environment": {"Variables": {"CUSTOM_SETTING": "keep"}},
        }
        project.deploy_lambda()
        update = client.update_function_configuration.call_args.kwargs
        self.assertEqual(update["Runtime"], "python3.12")
        self.assertEqual(update["Handler"], "lambda_function.lambda_handler")
        self.assertEqual(update["MemorySize"], 256)
        self.assertEqual(update["Timeout"], 60)
        self.assertEqual(update["Environment"]["Variables"]["CUSTOM_SETTING"], "keep")
        client.create_function.assert_not_called()

    def test_cleanup_account_guard_precedes_deletion(self):
        project = self.project()
        with self.assertRaises(ValueError):
            project.cleanup("999999999999", True)
        project.session.client.assert_not_called()

    def test_cleanup_data_requires_project_tag(self):
        project = self.project()
        project.client("s3").get_bucket_tagging.return_value = {
            "TagSet": [{"Key": "Project", "Value": "OtherProject"}]
        }
        with self.assertRaises(ValueError):
            project.cleanup("123456789012", True)
        project.client("s3").delete_objects.assert_not_called()

    def test_schedule_is_single_and_target_errors_raise(self):
        project = self.project()
        project.clients["events"] = events = MagicMock()
        project.clients["lambda"] = lamb = MagicMock()
        events.put_rule.return_value = {
            "RuleArn": "arn:aws:events:us-east-1:123456789012:rule/" + RULE
        }
        events.put_targets.return_value = {"FailedEntryCount": 1}
        with self.assertRaises(RuntimeError):
            project.setup_eventbridge()
        self.assertEqual(events.put_rule.call_count, 1)
        lamb.add_permission.assert_not_called()

    def test_scripts_use_sdk_entrypoints(self):
        import re

        for script in (ROOT / "scripts").glob("*.ps1"):
            self.assertIsNone(
                re.search(r"(?im)^\s*(?:&\s*)?aws\s", script.read_text()), str(script)
            )


if __name__ == "__main__":
    unittest.main()
