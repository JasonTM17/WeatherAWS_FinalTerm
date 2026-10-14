"""Regressions for the direct submitted-week comparison and its plotted values."""
import csv
from pathlib import Path
import unittest
import matplotlib.pyplot as plt
from weekly_comparison_charts import comparison_series, make_comparison_figure

DATA=Path(__file__).resolve().parents[1]/'results/week2_analysis/submitted_week1_comparison.csv'

class WeeklyComparisonChartTests(unittest.TestCase):
    def rows(self):
        with DATA.open(encoding='utf-8-sig',newline='') as handle:return list(csv.DictReader(handle))

    def test_bars_use_exact_retained_baseline_and_separate_week2_values(self):
        for metric in ('aqi','pm25'):
            figure,series=make_comparison_figure(self.rows(),metric)
            try:
                self.assertEqual([item['week1_samples'] for item in series],[[52]*3,[52]*3])
                self.assertEqual([item['week2_samples'] for item in series],[[9]*3,[19]*3])
                for axis,item in zip(figure.axes,series):
                    self.assertEqual([bar.get_height() for bar in axis.patches],item['week1_values']+item['week2_values'])
                    self.assertEqual(axis.get_ylim()[0],0)
                    self.assertIn(item['student'],axis.get_title())
                self.assertEqual(series[0]['week1_values'],series[1]['week1_values'])
                self.assertIn('µg/m³' if metric=='pm25' else 'US AQI',figure.axes[0].get_ylabel())
            finally:plt.close(figure)

    def test_missing_or_repeated_city_row_is_rejected(self):
        rows=self.rows()
        with self.assertRaises(ValueError):comparison_series(rows[:-1],'aqi')
        with self.assertRaises(ValueError):comparison_series(rows[:-1]+[rows[0]],'aqi')

    def test_wrong_scope_or_baseline_is_rejected(self):
        rows=self.rows();rows[0]['baseline_scope']='later_week_filtered'
        with self.assertRaisesRegex(ValueError,'retained'):comparison_series(rows,'aqi')
        rows=self.rows();rows[0]['week1_avg_aqi']='1'
        with self.assertRaisesRegex(ValueError,'same submission'):comparison_series(rows,'aqi')
        rows=self.rows();rows[0]['week2_avg_aqi']='nan'
        with self.assertRaisesRegex(ValueError,'finite'):comparison_series(rows,'aqi')

if __name__=='__main__':unittest.main()
