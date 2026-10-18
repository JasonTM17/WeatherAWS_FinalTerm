"""Forecast target timestamps must be future at actual issuance, not just after training."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from forecast import future_forecast, moving_predictions


class IssuanceTests(unittest.TestCase):
    def rows(self):
        origin = datetime(2026, 10, 18, 4, tzinfo=timezone.utc)
        return [{'timestamp_utc': (origin-timedelta(hours=119-i)).isoformat(), 'us_aqi': i} for i in range(120)]

    def test_all_24_targets_follow_actual_issue_and_bridge_current_hour(self):
        issued = datetime(2026, 10, 18, 5, 32, tzinfo=timezone.utc)
        result = future_forecast(self.rows(), 'us_aqi', issued)
        self.assertEqual(len(result), 24)
        self.assertEqual(result[0]['timestamp_utc'], '2026-10-18T06:00:00+00:00')
        self.assertEqual([r['horizon_hours'] for r in result], list(range(2, 26)))
        self.assertTrue(all(datetime.fromisoformat(r['timestamp_utc']) > issued for r in result))
        self.assertEqual(result[0]['predicted'], moving_predictions(list(range(120)), 25)[1])

    def test_current_hour_and_naive_issue_are_rejected(self):
        with self.assertRaises(ValueError):
            future_forecast(self.rows(), 'us_aqi', datetime(2026, 10, 18, 4, 32, tzinfo=timezone.utc))
        with self.assertRaises(ValueError):
            future_forecast(self.rows(), 'us_aqi', datetime(2026, 10, 18, 5, 32))

    def test_stale_history_is_not_extrapolated_as_live_prediction(self):
        with self.assertRaises(ValueError):
            future_forecast(self.rows(), 'us_aqi', datetime(2026, 10, 20, 5, tzinfo=timezone.utc))


if __name__ == '__main__':
    unittest.main()
