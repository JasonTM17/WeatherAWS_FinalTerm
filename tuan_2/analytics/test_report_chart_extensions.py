"""Regressions for matched-hour scope and complete original-week comparisons."""
from decimal import Decimal
import unittest

from report_chart_extensions import (DATA, WEEK1, CITIES, read_csv, matched_summary,
    matched_figure, reference_comparison, cent_value)


class ReportChartExtensionTests(unittest.TestCase):
    def test_matched_chart_shows_observed_levels_when_differences_are_zero(self):
        import matplotlib.pyplot as plt
        summary=matched_summary(read_csv(DATA/'matched_account_hours.csv'))
        self.assertEqual([r['common_hours'] for r in summary],[7,7,7])
        self.assertTrue(all(r['delta_us_aqi']==r['delta_pm2_5']==0 for r in summary))
        self.assertTrue(any(r['delta_relative_humidity_2m']!=0 for r in summary))
        figure=matched_figure(summary)
        try:
            for axis,metric in zip(figure.axes,['us_aqi','pm2_5']):
                expected=[r[p+'_'+metric] for p in ('son','quyen') for r in summary]
                self.assertEqual([bar.get_height() for bar in axis.patches],expected)
                self.assertTrue(all(v>0 for v in expected))
        finally:plt.close(figure)

    def test_equal_hour_weights_do_not_weight_by_more_records(self):
        rows=[]
        for index,value in enumerate([10.,30.]):
            row={'city':'HoChiMinh','timestamp_utc':str(index),'son_samples':1,'quyen_samples':index+1}
            for metric in ('us_aqi','pm2_5','pm10','temperature_2m','relative_humidity_2m'):
                row.update({'son_'+metric:value,'quyen_'+metric:value,'delta_'+metric:0.})
            rows.append(row)
        result=matched_summary(rows,['HoChiMinh'])[0]
        self.assertEqual(result['quyen_us_aqi'],20.)
        self.assertEqual(result['quyen_records_in_common_hours'],3)
        with self.assertRaises(ValueError):matched_summary(rows+[rows[0]],['HoChiMinh'])
        with self.assertRaises(ValueError):matched_summary(rows,['HaNoi'])

    def test_reference_category_denominators_and_correlations_use_correct_scope(self):
        data=reference_comparison(read_csv(WEEK1/'raw_weather_aqi_records.csv'),read_csv(DATA/'raw_week2_both_accounts.csv'))
        self.assertEqual(len(data),63)
        for city in CITIES:
            for profile,n in [('week1',52),('default',9),('quyen',19)]:
                group=[r for r in data if r['city']==city and r['series']==profile]
                self.assertTrue(all(r['n']==n for r in group))
                categories=[r for r in group if r['kind']=='aqi_category']
                self.assertEqual(sum(r['count'] for r in categories),n)
                self.assertAlmostEqual(sum(r['value'] for r in categories),100.)
                self.assertTrue(all(-1<=r['value']<=1 for r in group if r['kind']=='pearson_pm25'))

    def test_cent_rounding_preserves_real_negative_cost_and_normalizes_signed_zero(self):
        self.assertEqual(str(cent_value('-0.0000000764')),'0.00')
        self.assertEqual(cent_value('0.0267146366'),Decimal('0.03'))
        self.assertEqual(cent_value('-1.236'),Decimal('-1.24'))
        self.assertEqual(cent_value('0.005'),Decimal('0.01'))


if __name__=='__main__':unittest.main()
