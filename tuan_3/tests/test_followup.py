"""Regression checks for paired counters and unchanged issued-forecast comparisons."""
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from dashboard import metric_consistency, reconcile_periods
from forecast_followup import summarize
from monitoring_followup import classify_logs
from reconcile_analysis import partial_comparison


def point(name,value,stamp='2026-10-18T08:15:00+00:00'):
    return {'namespace':'AWS/Lambda','metric':name,'statistic':'Sum','value':value,'timestamp_utc':stamp}


class FollowupTests(unittest.TestCase):
    def test_equal_window_totals_do_not_pair_different_periods(self):
        rows=[point('Invocations',10),point('Errors',2,'2026-10-18T09:15:00+00:00')]
        result=metric_consistency(rows)
        self.assertEqual(result['error_rate_status'],'UNPAIRED_PERIODS')
        self.assertIsNone(result['error_rate_percent'])

    def test_valid_totals_cannot_hide_an_impossible_individual_period(self):
        rows=[point('Invocations',10),point('Errors',0),point('Invocations',1,'2026-10-18T09:15:00+00:00'),point('Errors',2,'2026-10-18T09:15:00+00:00')]
        self.assertEqual(metric_consistency(rows)['error_rate_status'],'INCONSISTENT_COUNTS')
        self.assertIsNone(metric_consistency(rows)['error_rate_percent'])

    def test_orphan_error_is_retained_and_paired_rate_is_not_overall_rate(self):
        rows=[point('Invocations',1),point('Errors',0),point('Errors',3,'2026-10-18T09:15:00+00:00')]
        result=reconcile_periods(rows)
        self.assertEqual(result['paired_error_rate_percent'],0)
        self.assertIsNone(result['overall_error_rate_percent'])
        self.assertEqual(result['unpaired_periods'],1)
        self.assertIsNone(result['periods'][1]['invocations'])
        self.assertEqual(result['periods'][1]['errors'],3)

    def test_timezone_offsets_join_the_same_native_period(self):
        result=reconcile_periods([point('Invocations',2),point('Errors',1,'2026-10-18T15:15:00+07:00')])
        self.assertEqual(result['overall_error_rate_percent'],50)
        self.assertEqual(len(result['periods']),1)

    def test_missing_error_is_unknown_and_no_invocations_is_not_zero_error_rate(self):
        self.assertIsNone(reconcile_periods([point('Invocations',1)])['paired_error_rate_percent'])
        result=reconcile_periods([point('Invocations',0),point('Errors',0)])
        self.assertEqual(result['periods'][0]['status'],'NO_INVOCATIONS')
        self.assertIsNone(result['overall_error_rate_percent'])

    def test_duplicate_negative_and_nonfinite_points_are_rejected(self):
        for rows in ([point('Invocations',1),point('Invocations',1)], [point('Errors',-1)], [point('Errors',float('nan'))]):
            with self.subTest(rows=rows),self.assertRaises(ValueError):
                reconcile_periods(rows)

    def test_logs_are_deduplicated_and_raw_messages_are_never_exported(self):
        start=datetime(2026,10,18,8,tzinfo=timezone.utc);end=datetime(2026,10,18,9,tzinfo=timezone.utc)
        def event(i,message):
            return {'eventId':str(i),'logStreamName':'private-stream','timestamp':int(start.timestamp()*1000),'message':message}
        first=event(1,'START RequestId: private-request Version: $LATEST')
        entries=[first,first,event(2,'END RequestId: private-request'),event(3,'REPORT RequestId: private-request Duration: 1 ms'),
                 event(4,'[INFO] Result: {"collection_status":"complete","records_collected":3,"alerts_sent":0,"private":"secret-placeholder"}')]
        rows,summary=classify_logs(entries,start,end)
        self.assertEqual(summary['matched_start_end_report'],1)
        self.assertEqual(summary['complete_results'],1)
        self.assertEqual(len(rows),4)
        self.assertNotIn('private-request',str(rows));self.assertNotIn('secret-placeholder',str(rows))
        self.assertNotIn('private-stream',str(rows))

    def test_comparison_excludes_uncompleted_hour_and_keeps_issued_values(self):
        issued=[{'city':'HaNoi','variable':'us_aqi','timestamp_utc':f'2026-10-18T0{h}:00:00+00:00','issued_at_utc':'2026-10-18T06:24:00+00:00','predicted':'10'} for h in (7,8,9)]
        later=[{'city':'HaNoi','timestamp_utc':r['timestamp_utc'],'us_aqi':12} for r in issued]
        before=[dict(r) for r in issued]
        compared=partial_comparison(issued,later,datetime(2026,10,18,9,tzinfo=timezone.utc))
        self.assertEqual(len(compared),2);self.assertEqual(issued,before)
        scores=summarize(issued,compared)
        self.assertEqual(scores[0]['matched_hours'],2);self.assertEqual(scores[0]['issued_hours'],3)
        self.assertEqual(scores[0]['mae'],2);self.assertEqual(scores[0]['bias'],-2)


if __name__=='__main__':
    unittest.main()
