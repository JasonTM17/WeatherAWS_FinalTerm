"""
Unit Tests for CSV Exports and Data Integrity
Kiểm tra tính toàn vẹn của các tệp CSV xuất từ AWS Athena & AWS CLI
Môn học: Cloud - Đợt 1 - 2026-2027 | GVHD: Huỳnh Xuân Phụng | SV: 24110054
"""

import unittest
import os
import csv
import json

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CLI_EXPORTS_DIR = os.path.join(REPO_ROOT, 'results', 'aws_cli_exports')
ATHENA_QUERIES_DIR = os.path.join(REPO_ROOT, 'results', 'athena_queries')


class TestCsvExports(unittest.TestCase):

    def test_all_cli_export_files_exist(self):
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
            fpath = os.path.join(CLI_EXPORTS_DIR, fname)
            self.assertTrue(os.path.exists(fpath), f"File {fname} does not exist in {CLI_EXPORTS_DIR}")
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
            cli_path = os.path.join(CLI_EXPORTS_DIR, fname)
            athena_path = os.path.join(ATHENA_QUERIES_DIR, fname)
            self.assertTrue(os.path.exists(athena_path), f"File {fname} not found in {ATHENA_QUERIES_DIR}")
            self.assertEqual(os.path.getsize(cli_path), os.path.getsize(athena_path),
                             f"File sizes differ between CLI exports and Athena queries for {fname}")

    def test_city_comparison_csv_structure_and_counts(self):
        csv_path = os.path.join(CLI_EXPORTS_DIR, 'avg_aqi_by_city.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
        self.assertEqual(len(reader), 3)
        cities = {r['city'] for r in reader}
        self.assertEqual(cities, {'HoChiMinh', 'HaNoi', 'DaNang'})
        total_records = sum(int(r['total_records']) for r in reader)
        self.assertEqual(total_records, 156)

    def test_peak_hours_csv_structure_and_counts(self):
        csv_path = os.path.join(CLI_EXPORTS_DIR, 'peak_pollution_hours.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
        self.assertEqual(len(reader), 24)
        hours = [int(r['hour']) for r in reader]
        self.assertEqual(hours, list(range(24)))
        total_samples = sum(int(r['sample_count']) for r in reader)
        self.assertEqual(total_samples, 156)

    def test_category_distribution_csv_percentages(self):
        csv_path = os.path.join(CLI_EXPORTS_DIR, 'aqi_category_distribution.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
        self.assertEqual(len(reader), 8)
        # Check percentage sum per city is approximately 100%
        city_pcts = {}
        for r in reader:
            city = r['city']
            city_pcts[city] = city_pcts.get(city, 0.0) + float(r['percentage'])
        for city, total_pct in city_pcts.items():
            self.assertAlmostEqual(total_pct, 100.0, delta=1.0)

    def test_weather_correlation_csv_bounds(self):
        csv_path = os.path.join(CLI_EXPORTS_DIR, 'weather_correlation.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
        self.assertEqual(len(reader), 3)
        for r in reader:
            for field in ['corr_temp_pm25', 'corr_humidity_pm25', 'corr_wind_pm25']:
                val = float(r[field])
                self.assertTrue(-1.0 <= val <= 1.0, f"Correlation {field}={val} out of bounds [-1, 1]")

    def test_raw_records_csv_complete_156_records(self):
        csv_path = os.path.join(CLI_EXPORTS_DIR, 'raw_weather_aqi_records.csv')
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
        csv_path = os.path.join(CLI_EXPORTS_DIR, 'query_metrics.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
        self.assertEqual(len(reader), 5)
        for r in reader:
            self.assertEqual(r['status'], 'SUCCEEDED')
            self.assertGreater(int(r['result_rows']), 0)
            self.assertGreater(int(r['execution_time_ms']), 0)
            self.assertGreater(int(r['bytes_scanned']), 0)


if __name__ == '__main__':
    unittest.main()
