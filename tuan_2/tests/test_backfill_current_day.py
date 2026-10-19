"""Fixed-clock regressions for collecting the latest completed UTC hours."""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import unittest
from urllib.parse import parse_qs, urlparse

from test_lambda_function import lambda_function


class BackfillCurrentDayTests(unittest.TestCase):
    def fetch(self, now, count, omit=None):
        origin = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        times = [(origin + timedelta(hours=i)).strftime('%Y-%m-%dT%H:%M') for i in range(48)]
        if omit:
            times.remove(omit)
        air = {'hourly': {'time': times, **{name: [10+i for i in range(len(times))]
                                          for name in lambda_function.AIR_FIELDS}}}
        weather = {'hourly': {'time': times, **{name: [20+i for i in range(len(times))]
                                              for name in lambda_function.WEATHER_FIELDS}}}
        urls = []
        def response(url):
            urls.append(url)
            query = parse_qs(urlparse(url).query)
            if query.get('forecast_days') == ['0']:
                # Simulate documented API behavior: previous day only.
                payload = air if 'air-quality' in url else weather
                return {'hourly': {k: v[:24] for k, v in payload['hourly'].items()}}
            return air if 'air-quality' in url else weather
        with patch.object(lambda_function, 'http_get_json', side_effect=response), \
                patch('lambda_function.datetime.datetime', wraps=datetime) as clock:
            clock.now.return_value = now
            rows = lambda_function.fetch_historical_series({'city': 'HaNoi', 'lat': 21, 'lon': 105}, count)
        return rows, urls

    def test_current_utc_day_excludes_future_and_incomplete_hour(self):
        rows, urls = self.fetch(datetime(2026, 10, 19, 3, 20, tzinfo=timezone.utc), 3)
        self.assertEqual([r['timestamp_utc'] for r in rows],
                         ['2026-10-19 00:00:00', '2026-10-19 01:00:00', '2026-10-19 02:00:00'])
        self.assertTrue(all(parse_qs(urlparse(url).query)['timezone'] == ['UTC'] for url in urls))

    def test_midnight_window_keeps_previous_utc_day_hours(self):
        rows, _ = self.fetch(datetime(2026, 10, 19, 0, 20, tzinfo=timezone.utc), 3)
        self.assertEqual([r['timestamp_utc'] for r in rows],
                         ['2026-10-18 21:00:00', '2026-10-18 22:00:00', '2026-10-18 23:00:00'])

    def test_missing_requested_hour_is_not_replaced_by_an_older_hour(self):
        rows, _ = self.fetch(datetime(2026, 10, 19, 3, 20, tzinfo=timezone.utc), 3, '2026-10-19T01:00')
        self.assertEqual([r['timestamp_utc'] for r in rows], ['2026-10-19 00:00:00', '2026-10-19 02:00:00'])

    def test_incomplete_backfill_preserves_available_rows_as_partial(self):
        with patch.object(lambda_function, 'fetch_secrets', return_value={'locations': [{'city': 'HaNoi'}]}), \
                patch.object(lambda_function, 'fetch_historical_series', return_value=[{'timestamp_utc': '2026-10-19 00:00:00'}]), \
                patch.object(lambda_function, 'save_records_to_s3', return_value=[]):
            result = lambda_function.lambda_handler({'backfill_hours': 3}, None)
        self.assertEqual(result['collection_status'], 'partial')
        self.assertEqual(result['records_collected'], 1)
        self.assertEqual(result['failed_cities'], ['HaNoi'])

    def test_backfill_never_publishes_historical_alerts(self):
        with patch.object(lambda_function, 'fetch_secrets', return_value={'locations': [{'city': 'HaNoi'}]}), \
                patch.object(lambda_function, 'fetch_historical_series', return_value=[
                    {'us_aqi': 300, 'pm2_5': 200, 'timestamp_utc': f'2026-10-19 0{i}:00:00'} for i in range(3)]), \
                patch.object(lambda_function, 'save_records_to_s3', return_value=[]), \
                patch.object(lambda_function, 'send_sns_alert') as alert:
            result = lambda_function.lambda_handler({'backfill_hours': 3}, None)
        alert.assert_not_called()
        self.assertEqual(result['alerts_sent'], 0)


if __name__ == '__main__':
    unittest.main()
