"""
Unit Tests for WeatherCollectorLambda
Testing edge cases, null values, historical series indexing, and SNS alerts.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json

# Add lambda directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lambda')))

import lambda_function


class TestWeatherCollectorLambda(unittest.TestCase):

    def test_safe_float(self):
        self.assertEqual(lambda_function.safe_float(None), 0.0)
        self.assertEqual(lambda_function.safe_float(None, default=10.5), 10.5)
        self.assertEqual(lambda_function.safe_float("23.45"), 23.45)
        self.assertEqual(lambda_function.safe_float(42), 42.0)
        self.assertEqual(lambda_function.safe_float(-5.2), -5.2)
        self.assertEqual(lambda_function.safe_float("invalid"), 0.0)
        self.assertEqual(lambda_function.safe_float("", default=1.0), 1.0)

    def test_safe_int(self):
        self.assertEqual(lambda_function.safe_int(None), 0)
        self.assertEqual(lambda_function.safe_int(None, default=99), 99)
        self.assertEqual(lambda_function.safe_int("75"), 75)
        self.assertEqual(lambda_function.safe_int(75.8), 75)
        self.assertEqual(lambda_function.safe_int("invalid"), 0)

    def test_get_aqi_category_boundaries(self):
        # EPA standard thresholds
        self.assertEqual(lambda_function.get_aqi_category(0), "Good")
        self.assertEqual(lambda_function.get_aqi_category(50), "Good")
        self.assertEqual(lambda_function.get_aqi_category(51), "Moderate")
        self.assertEqual(lambda_function.get_aqi_category(100), "Moderate")
        self.assertEqual(lambda_function.get_aqi_category(101), "Unhealthy for Sensitive Groups")
        self.assertEqual(lambda_function.get_aqi_category(150), "Unhealthy for Sensitive Groups")
        self.assertEqual(lambda_function.get_aqi_category(151), "Unhealthy")
        self.assertEqual(lambda_function.get_aqi_category(200), "Unhealthy")
        self.assertEqual(lambda_function.get_aqi_category(201), "Very Unhealthy")
        self.assertEqual(lambda_function.get_aqi_category(300), "Very Unhealthy")
        self.assertEqual(lambda_function.get_aqi_category(301), "Hazardous")
        self.assertEqual(lambda_function.get_aqi_category(500), "Hazardous")

    def test_get_aqi_category_edge_cases(self):
        self.assertEqual(lambda_function.get_aqi_category(None), "Unknown")
        self.assertEqual(lambda_function.get_aqi_category(-5), "Unknown")
        self.assertEqual(lambda_function.get_aqi_category("bad_value"), "Unknown")
        self.assertEqual(lambda_function.get_aqi_category("75"), "Moderate")

    @patch('lambda_function.secrets_client')
    def test_fetch_secrets_fallback(self, mock_secrets):
        mock_secrets.get_secret_value.side_effect = Exception("AWS Secrets error")
        config = lambda_function.fetch_secrets()
        self.assertIn("locations", config)
        self.assertIn("aqi_threshold_pm25", config)
        self.assertEqual(len(config["locations"]), 3)

    @patch('lambda_function.http_get_json')
    def test_fetch_city_data_success(self, mock_http):
        mock_http.side_effect = [
            # Air quality response
            {
                "current": {
                    "us_aqi": 85,
                    "pm2_5": 28.4,
                    "pm10": 42.1,
                    "carbon_monoxide": 320.0,
                    "nitrogen_dioxide": 18.2,
                    "sulphur_dioxide": 4.1,
                    "ozone": 45.0
                }
            },
            # Weather response
            {
                "current": {
                    "temperature_2m": 31.5,
                    "relative_humidity_2m": 72.0,
                    "surface_pressure": 1008.2,
                    "wind_speed_10m": 12.3
                }
            }
        ]

        loc = {"city": "HoChiMinh", "lat": 10.8231, "lon": 106.6297}
        record = lambda_function.fetch_city_data(loc)

        self.assertEqual(record["city"], "HoChiMinh")
        self.assertEqual(record["us_aqi"], 85)
        self.assertEqual(record["aqi_category"], "Moderate")
        self.assertEqual(record["pm2_5"], 28.4)
        self.assertEqual(record["temperature_2m"], 31.5)
        self.assertIn("year", record)
        self.assertIn("month", record)
        self.assertIn("day", record)

    @patch('lambda_function.http_get_json')
    def test_fetch_city_data_with_null_fields(self, mock_http):
        """Test API returning null values for sensors (should not crash with TypeError)."""
        mock_http.side_effect = [
            {"current": {"us_aqi": None, "pm2_5": None, "pm10": None, "carbon_monoxide": None}},
            {"current": {"temperature_2m": None, "relative_humidity_2m": None, "surface_pressure": None, "wind_speed_10m": None}}
        ]

        loc = {"city": "HaNoi", "lat": 21.0285, "lon": 105.8542}
        record = lambda_function.fetch_city_data(loc)

        self.assertEqual(record["city"], "HaNoi")
        self.assertEqual(record["us_aqi"], 0)
        self.assertEqual(record["aqi_category"], "Unknown")
        self.assertEqual(record["temperature_2m"], 0.0)
        self.assertEqual(record["pm2_5"], 0.0)

    @patch('lambda_function.http_get_json')
    def test_fetch_historical_series_index_alignment(self, mock_http):
        """
        Verify that when len(times) < past_hours:
        1. Records are NOT skipped.
        2. Timestamps and measurement arrays stay aligned.
        """
        times = ["2026-10-06T00:00", "2026-10-06T01:00", "2026-10-06T02:00"]
        mock_http.side_effect = [
            {
                "hourly": {
                    "time": times,
                    "us_aqi": [40, 75, 120],
                    "pm2_5": [10.0, 25.0, 45.0],
                    "pm10": [15.0, 30.0, 50.0],
                    "carbon_monoxide": [100.0, 200.0, 300.0],
                    "nitrogen_dioxide": [10.0, 15.0, 20.0],
                    "sulphur_dioxide": [2.0, 3.0, 4.0],
                    "ozone": [30.0, 40.0, 50.0]
                }
            },
            {
                "hourly": {
                    "time": times,
                    "temperature_2m": [25.0, 26.0, 27.0],
                    "relative_humidity_2m": [80.0, 75.0, 70.0],
                    "surface_pressure": [1010.0, 1009.0, 1008.0],
                    "wind_speed_10m": [5.0, 6.0, 7.0]
                }
            }
        ]

        loc = {"city": "DaNang", "lat": 16.0544, "lon": 108.2022}
        # Request 10 hours even though only 3 are available
        records = lambda_function.fetch_historical_series(loc, past_hours=10)

        self.assertEqual(len(records), 3, "All 3 records must be kept without dropping")
        self.assertEqual(records[0]["us_aqi"], 40)
        self.assertEqual(records[0]["pm2_5"], 10.0)
        self.assertEqual(records[0]["temperature_2m"], 25.0)

        self.assertEqual(records[2]["us_aqi"], 120)
        self.assertEqual(records[2]["pm2_5"], 45.0)
        self.assertEqual(records[2]["temperature_2m"], 27.0)

    @patch('lambda_function.sns_client')
    def test_send_sns_alert(self, mock_sns):
        mock_sns.publish.return_value = {"MessageId": "msg-12345"}
        record = {
            "city": "HoChiMinh",
            "aqi_category": "Unhealthy",
            "us_aqi": 165,
            "latitude": 10.82,
            "longitude": 106.63,
            "timestamp_vn": "2026-10-06 18:00:00",
            "timestamp_utc": "2026-10-06 11:00:00",
            "pm2_5": 45.0,
            "pm10": 60.0,
            "ozone": 30.0,
            "carbon_monoxide": 400.0,
            "nitrogen_dioxide": 25.0,
            "sulphur_dioxide": 5.0,
            "temperature_2m": 30.0,
            "relative_humidity_2m": 85.0,
            "wind_speed_10m": 8.0,
            "surface_pressure": 1009.0,
            "year": "2026",
            "month": "10",
            "day": "06"
        }

        sent = lambda_function.send_sns_alert(record, threshold_pm25=35.5, threshold_aqi=100)
        self.assertTrue(sent)
        self.assertTrue(mock_sns.publish.called)

        # Verify subject is <= 100 characters
        call_kwargs = mock_sns.publish.call_args[1]
        self.assertLessEqual(len(call_kwargs["Subject"]), 100)

    @patch('lambda_function.s3_client')
    def test_save_records_to_s3(self, mock_s3):
        mock_s3.put_object.return_value = {}
        records = [
            {"year": "2026", "month": "10", "day": "06", "city": "HoChiMinh", "us_aqi": 80},
            {"year": "2026", "month": "10", "day": "06", "city": "HaNoi", "us_aqi": 65},
            {"year": "2026", "month": "10", "day": "05", "city": "DaNang", "us_aqi": 50}
        ]

        saved_files = lambda_function.save_records_to_s3(records)
        self.assertEqual(len(saved_files), 2, "Should group into 2 partition files (day 05 and day 06)")
        self.assertEqual(mock_s3.put_object.call_count, 2)

    def test_save_records_to_s3_empty(self):
        saved_files = lambda_function.save_records_to_s3([])
        self.assertEqual(saved_files, [])

    @patch('lambda_function.save_records_to_s3')
    @patch('lambda_function.fetch_city_data')
    @patch('lambda_function.fetch_secrets')
    def test_lambda_handler_realtime(self, mock_secrets, mock_city, mock_save):
        mock_secrets.return_value = {
            "locations": [{"city": "HoChiMinh", "lat": 10.8, "lon": 106.6}],
            "aqi_threshold_pm25": 35.5,
            "aqi_threshold_us_aqi": 100
        }
        mock_city.return_value = {
            "city": "HoChiMinh",
            "pm2_5": 20.0,
            "us_aqi": 60,
            "aqi_category": "Moderate",
            "year": "2026", "month": "10", "day": "06"
        }
        mock_save.return_value = [{"s3_key": "raw/year=2026/...", "count": 1}]

        result = lambda_function.lambda_handler({}, None)
        self.assertEqual(result["statusCode"], 200)
        self.assertEqual(result["records_collected"], 1)
        self.assertEqual(result["alerts_sent"], 0)


if __name__ == '__main__':
    unittest.main()
