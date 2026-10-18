"""Numerical and temporal boundaries for supplementary evidence analysis."""
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from reconcile_analysis import correlation, descriptive, partial_comparison, ranks, recursive_mean


class ReconciliationTests(unittest.TestCase):
    def test_tied_ranks_use_mean_positions(self):
        self.assertEqual(ranks([8,2,2,4]),[4,1.5,1.5,3])
        self.assertAlmostEqual(correlation(ranks([1,1,3]),ranks([4,4,9])),1)

    def test_recursive_three_hour_mean_does_not_read_target_values(self):
        values=[1,2,3]
        estimates=recursive_mean(values,3,2)
        self.assertEqual(values,[1,2,3])
        self.assertEqual(estimates[0],2)
        self.assertAlmostEqual(estimates[1],7/3)
        with self.assertRaises(ValueError):
            recursive_mean(values,0)

    def test_statistics_sample_sd_and_linear_percentile(self):
        result=descriptive([1,2,3])
        self.assertEqual(result['sample_std'],1)
        self.assertEqual(result['p25'],1.5)
        self.assertEqual(result['p95'],2.9)

    def test_constant_series_is_undefined_correlation_not_zero(self):
        self.assertIsNone(correlation([1,1,1],[2,3,4]))

    def test_later_model_comparison_excludes_incomplete_hour_and_preissuance(self):
        records=[{'city':'HaNoi','variable':'us_aqi','timestamp_utc':f'2026-10-18T{h:02d}:00:00+00:00',
                  'issued_at_utc':'2026-10-18T06:30:00+00:00','predicted':'12'} for h in (6,7,8)]
        later=[{'city':'HaNoi','timestamp_utc':r['timestamp_utc'],'us_aqi':10} for r in records]
        compared=partial_comparison(records,later,datetime(2026,10,18,8,tzinfo=timezone.utc))
        self.assertEqual(len(compared),1)
        self.assertEqual(compared[0]['timestamp_utc'],'2026-10-18T07:00:00+00:00')
        self.assertEqual(compared[0]['error_vs_later_model'],2)


if __name__=='__main__':
    unittest.main()
