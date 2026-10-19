"""Unit tests for Week 4 operations, reconciliation, cost analysis, and scripts."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "tuan_4/scripts"
RESULTS_DIR = ROOT / "tuan_4/results"


class TestWeek4Operations(unittest.TestCase):
    def test_reconciliation_csv_and_summary(self):
        reconcile_csv = (
            RESULTS_DIR / "monitoring/log_metric_s3_reconciliation.csv"
        )
        summary_json = RESULTS_DIR / "monitoring/reconciliation_summary.json"
        self.assertTrue(reconcile_csv.exists())
        self.assertTrue(summary_json.exists())

        with reconcile_csv.open("r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            self.assertEqual(len(reader), 14)
            for row in reader:
                self.assertEqual(row["reconciliation_verdict"], "MATCH")
                self.assertEqual(row["log_status"], "complete")
                self.assertEqual(int(row["reported_records"]), 3)
                self.assertEqual(int(row["s3_verified_records"]), 3)
                self.assertEqual(int(row["cities_covered"]), 3)
                self.assertEqual(int(row["native_invocations"]), 1)
                self.assertEqual(int(row["metric_result_lines"]), 1)

        summary = json.loads(summary_json.read_text(encoding="utf-8"))
        self.assertEqual(summary["status"], "PASS")
        self.assertEqual(summary["reconciliation_rate_percent"], 100.0)
        self.assertEqual(summary["orphan_s3_objects_count"], 0)
        self.assertEqual(summary["phantom_invocations_count"], 0)

    def test_cost_reports_integrity(self):
        breakdown_file = RESULTS_DIR / "cost/learner_lab_cost_breakdown.csv"
        scenarios_file = RESULTS_DIR / "cost/projected_cost_scenarios.csv"
        recommendations_file = (
            RESULTS_DIR / "cost/cost_optimization_recommendations.csv"
        )

        for path in (breakdown_file, scenarios_file, recommendations_file):
            self.assertTrue(path.exists(), f"Missing cost report: {path}")
            with path.open("r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
                self.assertGreater(len(rows), 0)

    def test_security_controls_audit_matrix(self):
        matrix_file = RESULTS_DIR / "security/security_controls_audit.csv"
        self.assertTrue(matrix_file.exists())
        with matrix_file.open("r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            self.assertGreaterEqual(len(rows), 10)
            for r in rows:
                self.assertEqual(
                    r["audit_verdict"], "PASS", f"Failed control: {r['control_id']}"
                )

    def test_lifecycle_scripts_exist(self):
        cleanup_ps1 = SCRIPTS_DIR / "cleanup_resources.ps1"
        start_ps1 = SCRIPTS_DIR / "start_resources.ps1"
        self.assertTrue(cleanup_ps1.exists())
        self.assertTrue(start_ps1.exists())
        self.assertIn("session_control.py", cleanup_ps1.read_text(encoding="utf-8"))
        self.assertIn("session_control.py", start_ps1.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
