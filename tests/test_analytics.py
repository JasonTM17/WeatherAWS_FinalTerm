"""
Unit Tests for Analytics & Chart Generation
"""

import unittest
import os
import sys
import pandas as pd
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analytics')))

import generate_charts


class TestAnalytics(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.orig_charts_dir = generate_charts.CHARTS_DIR
        generate_charts.CHARTS_DIR = self.test_dir

    def tearDown(self):
        generate_charts.CHARTS_DIR = self.orig_charts_dir
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_plot_city_comparison_runs(self):
        generate_charts.plot_city_comparison()
        expected_file = os.path.join(self.test_dir, '01_aqi_city_comparison.png')
        self.assertTrue(os.path.exists(expected_file))
        self.assertGreater(os.path.getsize(expected_file), 1000)

    def test_plot_hourly_trend_runs(self):
        generate_charts.plot_hourly_trend()
        expected_file = os.path.join(self.test_dir, '02_peak_pollution_hours.png')
        self.assertTrue(os.path.exists(expected_file))
        self.assertGreater(os.path.getsize(expected_file), 1000)

    def test_plot_category_distribution_runs(self):
        generate_charts.plot_category_distribution()
        expected_file = os.path.join(self.test_dir, '03_aqi_category_distribution.png')
        self.assertTrue(os.path.exists(expected_file))
        self.assertGreater(os.path.getsize(expected_file), 1000)

    def test_plot_correlation_runs(self):
        generate_charts.plot_correlation()
        expected_file = os.path.join(self.test_dir, '04_weather_pm25_correlation.png')
        self.assertTrue(os.path.exists(expected_file))
        self.assertGreater(os.path.getsize(expected_file), 1000)


if __name__ == '__main__':
    unittest.main()
