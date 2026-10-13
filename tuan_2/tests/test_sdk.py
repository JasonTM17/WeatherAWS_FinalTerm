"""Focused SDK regressions without live credentials or cloud resources."""
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from athena_export import AthenaExporter, AthenaQueryError, copy_snapshot
from aws_project import AwsProject, RULE

def error(code):
    return ClientError({'Error': {'Code': code, 'Message': 'Test error'}}, 'Test')

class TestSdk(unittest.TestCase):
    def exporter(self):
        athena, s3 = MagicMock(), MagicMock()
        athena.start_query_execution.return_value = {'QueryExecutionId': 'query-1'}
        return AthenaExporter(athena, s3, 'weather_aqi_db', 's3://bucket/results/', sleep=lambda _: None)

    def test_failed_query_preserves_existing_csv(self):
        exporter = self.exporter()
        exporter.athena.get_query_execution.return_value = {'QueryExecution': {'Status': {'State': 'FAILED'}}}
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'data.csv'
            target.write_bytes(b'original')
            with self.assertRaises(AthenaQueryError): exporter.export('query', 'SELECT 1', target)
            self.assertEqual(target.read_bytes(), b'original')
            exporter.s3.get_object.assert_not_called()

    def test_timeout_cancels_query(self):
        exporter = self.exporter()
        exporter.clock = MagicMock(side_effect=[0, 301])
        exporter.athena.get_query_execution.return_value = {'QueryExecution': {'Status': {'State': 'RUNNING'}}}
        with self.assertRaises(TimeoutError): exporter.execute('SELECT 1')
        exporter.athena.stop_query_execution.assert_called_once_with(QueryExecutionId='query-1')

    def test_pagination_keeps_null_and_header_once(self):
        exporter = self.exporter()
        exporter.s3.get_object.side_effect = error('AccessDenied')
        metadata = {'ColumnInfo': [{'Name': 'city'}, {'Name': 'value'}]}
        exporter.athena.get_query_results.side_effect = [
            {'ResultSet': {'ResultSetMetadata': metadata, 'Rows': [
                {'Data': [{'VarCharValue': 'city'}, {'VarCharValue': 'value'}]},
                {'Data': [{'VarCharValue': 'A'}, {}]}]}, 'NextToken': 'page2'},
            {'ResultSet': {'ResultSetMetadata': metadata, 'Rows': [{'Data': [
                {'VarCharValue': 'B'}, {'VarCharValue': '2'}]}]}},
        ]
        blob = exporter.csv_bytes('query-1', {'ResultConfiguration': {'OutputLocation': 's3://bucket/key.csv'}})
        self.assertEqual(list(csv.reader(io.StringIO(blob.decode()))), [['city', 'value'], ['A', ''], ['B', '2']])
        self.assertEqual(exporter.athena.get_query_results.call_args_list[1].kwargs['NextToken'], 'page2')

    def test_s3_csv_preserved_byte_for_byte(self):
        exporter = self.exporter()
        blob = b'"city","value"\r\n"A","1.00"\r\n'
        exporter.s3.get_object.return_value = {'Body': io.BytesIO(blob)}
        self.assertEqual(exporter.csv_bytes('query-1', {'ResultConfiguration': {'OutputLocation': 's3://bucket/key.csv'}}), blob)

    def test_invalid_credentials_do_not_trigger_fallback(self):
        exporter = self.exporter()
        exporter.s3.get_object.side_effect = error('InvalidAccessKeyId')
        with self.assertRaises(ClientError): exporter.csv_bytes('query-1', {'ResultConfiguration': {'OutputLocation': 's3://bucket/key.csv'}})
        exporter.athena.get_query_results.assert_not_called()

    def test_offline_copy_identifies_saved_source(self):
        with tempfile.TemporaryDirectory() as directory:
            copy_snapshot(directory, ['avg_aqi_by_city'])
            self.assertEqual((Path(directory)/'avg_aqi_by_city.csv').read_bytes(), (ROOT/'results/athena_queries/avg_aqi_by_city.csv').read_bytes())
            self.assertEqual(json.loads((Path(directory)/'export_manifest.json').read_text())['mode'], 'saved-snapshot')

    def test_offline_copy_cannot_overwrite_source(self):
        with self.assertRaises(ValueError): copy_snapshot(ROOT/'results/athena_queries')

    def project(self):
        project = AwsProject(session=MagicMock())
        project._identity = {'Account': '123456789012', 'Arn': 'arn:aws:iam::123456789012:role/LabRole'}
        return project

    def test_s3_access_denied_is_not_missing(self):
        project = self.project()
        s3 = project.client('s3')
        s3.head_bucket.side_effect = error('403')
        with self.assertRaises(ClientError): project.setup_s3()
        s3.create_bucket.assert_not_called()

    def test_cleanup_account_guard_precedes_deletion(self):
        project = self.project()
        with self.assertRaises(ValueError): project.cleanup('999999999999', True)
        project.session.client.assert_not_called()

    def test_cleanup_data_requires_project_tag(self):
        project = self.project()
        project.client('s3').get_bucket_tagging.return_value = {'TagSet': [{'Key':'Project','Value':'OtherProject'}]}
        with self.assertRaises(ValueError): project.cleanup('123456789012', True)
        project.client('s3').delete_objects.assert_not_called()

    def test_schedule_is_single_and_target_errors_raise(self):
        project = self.project()
        project.clients['events'] = events = MagicMock()
        project.clients['lambda'] = lamb = MagicMock()
        events.put_rule.return_value = {'RuleArn': 'arn:aws:events:us-east-1:123456789012:rule/'+RULE}
        events.put_targets.return_value = {'FailedEntryCount': 1}
        with self.assertRaises(RuntimeError): project.setup_eventbridge()
        self.assertEqual(events.put_rule.call_count, 1)
        lamb.add_permission.assert_not_called()

    def test_scripts_use_sdk_entrypoints(self):
        import re
        for script in (ROOT/'scripts').glob('*.ps1'):
            self.assertIsNone(re.search(r'(?im)^\s*(?:&\s*)?aws\s', script.read_text()), str(script))

if __name__ == '__main__': unittest.main()
