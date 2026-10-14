"""Focused regression checks for time boundaries and two-account analysis."""
import unittest
from datetime import datetime,timezone
from pathlib import Path
import csv,statistics,math,importlib.util
target=Path(__file__).with_name('analyze_week2_accounts.py')
spec=importlib.util.spec_from_file_location('week2_analyzer',target);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
DATA=target.parents[1]/'results/week2_analysis'
class Week2AnalysisTests(unittest.TestCase):
    def test_timezone_normalization_avoids_lexical_filter_error(self):
        self.assertLess(module.instant('2026-10-12 00:00:00+07:00'),module.instant('2026-10-11 18:00:00+00:00'))
        self.assertEqual(module.instant('2026-10-12T00:00:00+07:00'),module.START)
        self.assertLess(module.instant('2026-10-11T23:59:59+07:00'),module.START)
    def test_spearman_average_ties(self):
        self.assertEqual(module.ranks([4,2,2,9]),[3,1.5,1.5,4])
        self.assertAlmostEqual(module.correlation(module.ranks([1,2,3]),module.ranks([3,2,1])),-1)
    def test_correlations_do_not_invent_value_for_constant_input(self):
        self.assertIsNone(module.correlation([1,1,1],[1,2,3]))
        self.assertIsNone(module.correlation([1,2],[1,2]))
    def test_city_aggregates_match_raw_independently(self):
        raw=module.read_csv(DATA/'raw_week2_both_accounts.csv');stats=module.read_csv(DATA/'city_statistics.csv')
        self.assertEqual(len(raw),84)
        for row in stats:
            data=[r for r in raw if r['profile']==row['profile'] and r['city']==row['city']]
            self.assertEqual(len(data),int(row['sample_count']))
            self.assertAlmostEqual(statistics.mean(float(r['us_aqi']) for r in data),float(row['avg_aqi']),places=10)
            self.assertEqual(sum(float(r['us_aqi'])>=100 or float(r['pm2_5'])>=35.5 for r in data),int(row['combined_alert_count']))
    def test_account_pairing_uses_hour_means_without_pooling(self):
        hourly=module.read_csv(DATA/'hourly_city.csv');paired=module.read_csv(DATA/'matched_account_hours.csv')
        self.assertEqual(len(paired),21)
        for row in paired:
            values={p:next(r for r in hourly if r['profile']==p and r['city']==row['city'] and r['timestamp_utc']==row['timestamp_utc']) for p in ['default','quyen']}
            self.assertAlmostEqual(float(row['delta_us_aqi']),float(values['quyen']['avg_aqi'])-float(values['default']['avg_aqi']),places=10)
    def test_invalid_error_ratio_is_missing_not_zero_or_over_100_percent(self):
        for row in module.read_csv(DATA/'operational_summary.csv'):
            self.assertGreater(float(row['Errors']),float(row['Invocations']))
            self.assertEqual(row['error_rate'],'')
            self.assertEqual(row['error_rate_valid'],'False')
    def test_partition_comparison_has_same_count_and_actual_scan_reduction(self):
        raw=module.read_csv(DATA/'raw_week2_both_accounts.csv')
        for row in module.read_csv(DATA/'partition_scan_comparison.csv'):
            count=sum(r['profile']==row['profile'] for r in raw)
            self.assertEqual(count,int(row['matched_records']))
            expected=1-float(row['partition_filtered_bytes'])/float(row['time_only_bytes'])
            self.assertAlmostEqual(expected,float(row['scan_reduction_fraction']),places=12)
if __name__=='__main__':unittest.main()
