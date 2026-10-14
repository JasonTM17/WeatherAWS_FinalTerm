"""
Unit Tests for CSV Exports and Data Integrity
Kiểm tra tính toàn vẹn của các tệp CSV xuất từ AWS Athena & Python SDK
Môn học: Cloud - Đợt 1 - 2026-2027 | GVHD: Huỳnh Xuân Phụng | SV: 24110054
"""

import unittest
import os
import csv
import json
import subprocess
import tempfile
import shutil
import sys
import re

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_EXPORTS_DIR = os.path.join(REPO_ROOT, 'results', 'data_exports')
ATHENA_QUERIES_DIR = os.path.join(REPO_ROOT, 'results', 'athena_queries')


class TestCsvExports(unittest.TestCase):

    def test_all_saved_export_files_exist(self):
        expected_files = [
            'avg_aqi_by_city.csv',
            'peak_pollution_hours.csv',
            'aqi_category_distribution.csv',
            'weather_correlation.csv',
            'raw_weather_aqi_records.csv',
            'query_metrics.csv',
            'summary_metrics.json',
            'README.md'
        ]
        for fname in expected_files:
            fpath = os.path.join(DATA_EXPORTS_DIR, fname)
            self.assertTrue(os.path.exists(fpath), f"File {fname} does not exist in {DATA_EXPORTS_DIR}")
            self.assertGreater(os.path.getsize(fpath), 0, f"File {fname} is empty")

    def test_athena_queries_synchronized(self):
        expected_csvs = [
            'avg_aqi_by_city.csv',
            'peak_pollution_hours.csv',
            'aqi_category_distribution.csv',
            'weather_correlation.csv',
            'raw_weather_aqi_records.csv',
            'query_metrics.csv'
        ]
        for fname in expected_csvs:
            saved_path = os.path.join(DATA_EXPORTS_DIR, fname)
            athena_path = os.path.join(ATHENA_QUERIES_DIR, fname)
            self.assertTrue(os.path.exists(athena_path), f"File {fname} not found in {ATHENA_QUERIES_DIR}")
            with open(saved_path, 'rb') as left, open(athena_path, 'rb') as right:
                self.assertEqual(left.read(), right.read(), f"Saved export differs from Athena CSV: {fname}")

    def test_city_comparison_csv_structure_and_counts(self):
        csv_path = os.path.join(DATA_EXPORTS_DIR, 'avg_aqi_by_city.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
        self.assertEqual(len(reader), 3)
        cities = {r['city'] for r in reader}
        self.assertEqual(cities, {'HoChiMinh', 'HaNoi', 'DaNang'})
        total_records = sum(int(r['total_records']) for r in reader)
        self.assertEqual(total_records, 156)

    def test_peak_hours_csv_structure_and_counts(self):
        csv_path = os.path.join(DATA_EXPORTS_DIR, 'peak_pollution_hours.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
        self.assertEqual(len(reader), 24)
        hours = [int(r['hour']) for r in reader]
        self.assertEqual(hours, list(range(24)))
        total_samples = sum(int(r['sample_count']) for r in reader)
        self.assertEqual(total_samples, 156)

    def test_category_distribution_csv_percentages(self):
        csv_path = os.path.join(DATA_EXPORTS_DIR, 'aqi_category_distribution.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
        self.assertEqual(len(reader), 8)
        city_pcts = {}
        for r in reader:
            city = r['city']
            city_pcts[city] = city_pcts.get(city, 0.0) + float(r['percentage'])
        for city, total_pct in city_pcts.items():
            self.assertAlmostEqual(total_pct, 100.0, delta=1.0)

    def test_weather_correlation_csv_bounds(self):
        csv_path = os.path.join(DATA_EXPORTS_DIR, 'weather_correlation.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
        self.assertEqual(len(reader), 3)
        for r in reader:
            for field in ['corr_temp_pm25', 'corr_humidity_pm25', 'corr_wind_pm25']:
                val = float(r[field])
                self.assertTrue(-1.0 <= val <= 1.0, f"Correlation {field}={val} out of bounds [-1, 1]")

    def test_raw_records_csv_complete_156_records(self):
        csv_path = os.path.join(DATA_EXPORTS_DIR, 'raw_weather_aqi_records.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
        self.assertEqual(len(reader), 156)
        expected_columns = {
            'record_id', 'city', 'latitude', 'longitude',
            'timestamp_utc', 'timestamp_vn', 'temperature_2m',
            'relative_humidity_2m', 'surface_pressure', 'wind_speed_10m',
            'pm2_5', 'pm10', 'carbon_monoxide', 'nitrogen_dioxide',
            'sulphur_dioxide', 'ozone', 'us_aqi', 'aqi_category',
            'hour', 'collected_at', 'year', 'month', 'day'
        }
        self.assertTrue(expected_columns.issubset(set(reader[0].keys())))

    def test_query_metrics_csv_contents(self):
        csv_path = os.path.join(DATA_EXPORTS_DIR, 'query_metrics.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
        self.assertEqual(len(reader), 5)
        for r in reader:
            self.assertEqual(r['status'], 'SUCCEEDED')
            self.assertGreater(int(r['result_rows']), 0)
            self.assertGreater(int(r['execution_time_ms']), 0)
            self.assertGreater(int(r['bytes_scanned']), 0)

    def test_csv_data_cleanliness_and_no_nans(self):
        """Verify no CSV contains corrupt 'NaN' strings or empty required values."""
        for fname in ['avg_aqi_by_city.csv', 'peak_pollution_hours.csv', 'raw_weather_aqi_records.csv']:
            fpath = os.path.join(DATA_EXPORTS_DIR, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row_idx, row in enumerate(reader):
                    for k, v in row.items():
                        self.assertIsNotNone(v, f"Null field {k} in {fname} row {row_idx}")
                        self.assertNotEqual(v.lower(), 'nan', f"NaN in {fname} field {k} row {row_idx}")

    def test_canonical_table_and_view_have_distinct_names(self):
        """Only the base table is external; the public alias must remain a view."""
        tbl_path = os.path.join(REPO_ROOT, 'athena', 'create_table.sql')
        view_path = os.path.join(REPO_ROOT, 'athena', 'create_view_vietnam_weather_aqi.sql')
        self.assertTrue(os.path.exists(tbl_path), "create_table.sql missing")
        self.assertTrue(os.path.exists(view_path), "create_view_vietnam_weather_aqi.sql missing")
        with open(tbl_path, 'r', encoding='utf-8') as f:
            table_sql = f.read()
        with open(view_path, 'r', encoding='utf-8') as f:
            view_sql = f.read()
        self.assertRegex(table_sql, r'(?i)CREATE\s+EXTERNAL\s+TABLE\s+IF\s+NOT\s+EXISTS\s+weather_aqi_db\.weather_airquality_records')
        self.assertRegex(view_sql, r'(?i)CREATE\s+OR\s+REPLACE\s+VIEW\s+weather_aqi_db\.vietnam_weather_aqi')
        self.assertRegex(view_sql, r'(?i)FROM\s+weather_aqi_db\.weather_airquality_records')
        for name in os.listdir(os.path.join(REPO_ROOT, 'athena')):
            if name.endswith('.sql'):
                with open(os.path.join(REPO_ROOT, 'athena', name), encoding='utf-8') as f:
                    sql = f.read()
                self.assertIsNone(re.search(
                    r'(?i)CREATE\s+(?:EXTERNAL\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?weather_aqi_db\.vietnam_weather_aqi\b', sql),
                    f'{name} creates a table with the view name')

    def test_export_raw_records_offline_resilience(self):
        """Test export_raw_records.py --offline flag generates 156 records to custom destination."""
        temp_dir = tempfile.mkdtemp()
        try:
            target_file = os.path.join(temp_dir, 'offline_raw_test.csv')
            script = os.path.join(REPO_ROOT, 'scripts', 'export_raw_records.py')
            res = subprocess.run([sys.executable, script, '--offline', '--output', target_file],
                                 capture_output=True, text=True, check=True)
            self.assertTrue(os.path.exists(target_file))
            with open(target_file, 'r', encoding='utf-8') as f:
                records = list(csv.DictReader(f))
            self.assertEqual(len(records), 156)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_offline_export_with_custom_output_dir(self):
        """An offline export copies saved bytes and labels their provenance."""
        temp_dir = tempfile.mkdtemp()
        try:
            script = os.path.join(REPO_ROOT, 'scripts', 'athena_export.py')
            cmd = [sys.executable, script, '--output', temp_dir, '--offline']
            test_env = os.environ.copy()
            test_env['AWS_ACCESS_KEY_ID'] = 'OFFLINE_MOCK'
            test_env['AWS_SECRET_ACCESS_KEY'] = 'OFFLINE_MOCK'
            test_env['AWS_SESSION_TOKEN'] = 'OFFLINE_MOCK'
            res = subprocess.run(cmd, capture_output=True, text=True, env=test_env)
            self.assertEqual(res.returncode, 0, f"Script failed: {res.stderr}\n{res.stdout}")

            expected_csvs = [
                'avg_aqi_by_city.csv',
                'peak_pollution_hours.csv',
                'aqi_category_distribution.csv',
                'weather_correlation.csv',
                'raw_weather_aqi_records.csv'
            ]
            for c in expected_csvs:
                p = os.path.join(temp_dir, c)
                self.assertTrue(os.path.exists(p), f"{c} was not created in custom output dir")
                self.assertGreater(os.path.getsize(p), 0, f"{c} is empty in custom output dir")

            with open(os.path.join(temp_dir, 'export_manifest.json'), encoding='utf-8') as f:
                self.assertEqual(json.load(f)['mode'], 'saved-snapshot')
            self.assertFalse(os.path.exists(os.path.join(temp_dir, 'query_metrics.csv')))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
