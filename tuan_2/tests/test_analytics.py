"""
Unit Tests for Analytics & Chart Generation
"""

import importlib
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "analytics"))
)

import generate_charts


class TestAnalytics(unittest.TestCase):
    def test_importing_week2_chart_module_does_not_write_report_assets(self):
        import report_chart_extensions

        sys.modules.pop("generate_week2_charts", None)
        with (
            patch.object(report_chart_extensions, "generate_extensions") as extensions,
            patch("pathlib.Path.mkdir") as mkdir,
            patch(
                "pathlib.Path.open",
                side_effect=AssertionError("Import read source data"),
            ),
            patch(
                "matplotlib.pyplot.subplots",
                side_effect=AssertionError("Import generated figures"),
            ),
        ):
            module = importlib.import_module("generate_week2_charts")
            self.assertTrue(callable(module.main))
            mkdir.assert_not_called()
            extensions.assert_not_called()

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.orig_charts_dir = generate_charts.CHARTS_DIR
        generate_charts.CHARTS_DIR = self.test_dir

    def tearDown(self):
        generate_charts.CHARTS_DIR = self.orig_charts_dir
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_plot_city_comparison_runs(self):
        generate_charts.plot_city_comparison()
        expected_file = os.path.join(self.test_dir, "01_aqi_city_comparison.png")
        self.assertTrue(os.path.exists(expected_file))
        self.assertGreater(os.path.getsize(expected_file), 1000)

    def test_plot_hourly_trend_runs(self):
        generate_charts.plot_hourly_trend()
        expected_file = os.path.join(self.test_dir, "02_peak_pollution_hours.png")
        self.assertTrue(os.path.exists(expected_file))
        self.assertGreater(os.path.getsize(expected_file), 1000)

    def test_plot_category_distribution_runs(self):
        generate_charts.plot_category_distribution()
        expected_file = os.path.join(self.test_dir, "03_aqi_category_distribution.png")
        self.assertTrue(os.path.exists(expected_file))
        self.assertGreater(os.path.getsize(expected_file), 1000)

    def test_plot_correlation_runs(self):
        generate_charts.plot_correlation()
        expected_file = os.path.join(self.test_dir, "04_weather_pm25_correlation.png")
        self.assertTrue(os.path.exists(expected_file))
        self.assertGreater(os.path.getsize(expected_file), 1000)


if __name__ == "__main__":
    unittest.main()
