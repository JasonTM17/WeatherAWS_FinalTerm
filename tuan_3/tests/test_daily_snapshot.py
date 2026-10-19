from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from daily_snapshot import day_window, preserve_previous, select_day, summarize_daily
from test_week3 import row


class DailySnapshotTests(unittest.TestCase):
    def test_local_day_includes_previous_utc_evening_and_excludes_next_midnight(self):
        start, end = day_window('2026-10-19')
        self.assertEqual(start.isoformat(), '2026-10-18T17:00:00+00:00')
        self.assertEqual(end.isoformat(), '2026-10-19T17:00:00+00:00')
        rows = [{'timestamp_utc': t} for t in ('2026-10-18 16:59:59', '2026-10-18 17:00:00',
                '2026-10-19 16:59:59', '2026-10-19 17:00:00')]
        self.assertEqual(select_day(rows, '2026-10-19', '2026-10-20T00:00:00+00:00'), rows[1:3])

    def test_capture_cutoff_does_not_admit_future_rows(self):
        rows = [{'timestamp_utc': '2026-10-19 07:00:00'}, {'timestamp_utc': '2026-10-19 08:00:00'}]
        self.assertEqual(select_day(rows, '2026-10-19', '2026-10-19T07:30:00+00:00'), rows[:1])
        with self.assertRaises(ValueError):
            select_day(rows, '2026-10-19', '2026-10-18T16:00:00+00:00')

    def test_missing_day_is_unknown_quality_not_a_healthy_zero(self):
        summary, hours, stats = summarize_daily([])
        self.assertEqual(summary['status'], 'NO_RECORDS_IN_DAY')
        self.assertIsNone(summary['issues'])
        self.assertEqual((hours, stats), ([], []))

    def test_previous_record_multiplicity_and_values_are_preserved(self):
        previous = [{'id': 'one', 'value': '1'}, {'id': 'one', 'value': '1'}]
        self.assertEqual(preserve_previous(previous, previous + [{'id': 'two', 'value': '2'}]), 2)
        for changed in (previous[:1], [{'id': 'one', 'value': '9'}] * 2):
            with self.assertRaises(ValueError):
                preserve_previous(previous, changed)

    def test_in_progress_hour_stays_in_raw_but_not_completed_hour_statistics(self):
        earlier, current = row(), row()
        earlier.update({'record_id': 'earlier', 'city': 'HaNoi', 'timestamp_utc': '2026-10-19 06:00:00',
                        'timestamp_vn': '2026-10-19 13:00:00', 'year': '2026', 'month': '10', 'day': '19', 'hour': 6,
                        'collected_at': '2026-10-19T07:20:00+00:00'})
        current.update({**earlier, 'record_id': 'current', 'timestamp_utc': '2026-10-19 07:15:00',
                        'timestamp_vn': '2026-10-19 14:15:00', 'hour': 7})
        quality, hours, stats = summarize_daily([earlier, current], '2026-10-19T07:00:00+00:00')
        self.assertEqual(quality['records'], 2)
        self.assertEqual(len(hours), 1)
        self.assertTrue(all(r['n'] == (2 if r['scope'] == 'raw' else 1) for r in stats))


if __name__ == '__main__':
    unittest.main()
