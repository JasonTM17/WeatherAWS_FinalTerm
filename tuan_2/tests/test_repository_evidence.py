"""Regression checks for public evidence without network access."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from botocore.exceptions import ClientError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import collect_repository_evidence as collector
import repository_audit as audit


class EvidenceTests(unittest.TestCase):
    def test_raw_aggregate_disagreement_is_rejected(self):
        raw = [{"city": "HaNoi", "us_aqi": "160", "pm2_5": "70"}]
        with self.assertRaises(ValueError):
            audit.reconcile_city_statistics(
                raw,
                [
                    {
                        "city": "HaNoi",
                        "sample_count": "1",
                        "avg_aqi": "161",
                        "avg_pm2_5": "70",
                    }
                ],
            )

    def test_repeated_city_keys_are_rejected(self):
        raw = [{"city": "HaNoi", "us_aqi": "160", "pm2_5": "70"}]
        row = {
            "city": "HaNoi",
            "sample_count": "1",
            "avg_aqi": "160",
            "avg_pm2_5": "70",
        }
        with self.assertRaises(ValueError):
            audit.reconcile_city_statistics(raw, [row, row])

    def test_nonfinite_aggregate_is_rejected(self):
        raw = [{"city": "HaNoi", "us_aqi": "160", "pm2_5": "70"}]
        with self.assertRaises(ValueError):
            audit.reconcile_city_statistics(
                raw,
                [
                    {
                        "city": "HaNoi",
                        "sample_count": "1",
                        "avg_aqi": "nan",
                        "avg_pm2_5": "70",
                    }
                ],
            )

    def test_raw_mean_and_count_are_reconciled(self):
        raw = [
            {"city": "HaNoi", "us_aqi": "160", "pm2_5": "70"},
            {"city": "HaNoi", "us_aqi": "164", "pm2_5": "74"},
        ]
        result = audit.reconcile_city_statistics(
            raw,
            [
                {
                    "city": "HaNoi",
                    "sample_count": "2",
                    "avg_aqi": "162",
                    "avg_pm2_5": "72",
                }
            ],
        )
        self.assertEqual(result["HaNoi"]["sample_count"], 2)

    def test_malformed_csv_width_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.csv"
            path.write_text("city,aqi\nHaNoi,160,extra\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                audit.csv_rows(path)

    def test_quoted_newline_and_vietnamese_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.csv"
            collector.write_csv(
                path,
                [{"student": "Sinh viên Ngọc Quyên", "note": "a\nb"}],
                ["student", "note"],
            )
            self.assertEqual(
                audit.csv_rows(path)[1],
                [{"student": "Sinh viên Ngọc Quyên", "note": "a\nb"}],
            )

    def test_failed_identity_keeps_sanitized_status(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(collector.boto3, "Session") as session,
        ):
            session.return_value.client.return_value.get_caller_identity.side_effect = (
                ClientError(
                    {
                        "Error": {
                            "Code": "ExpiredToken",
                            "Message": "private-provider-detail",
                        }
                    },
                    "GetCallerIdentity",
                )
            )
            _, checks, queries = collector.collect_profile(
                "default", Path(directory), "us-east-1"
            )
            self.assertEqual(checks[0]["error_code"], "ExpiredToken")
            self.assertEqual(checks[0]["status"], "UNAVAILABLE")
            self.assertEqual(queries, [])
            for file in Path(directory).rglob("*"):
                if file.is_file():
                    self.assertNotIn(
                        "private-provider-detail", file.read_text(encoding="utf-8")
                    )
            self.assertEqual(
                json.loads((Path(directory) / "default/queries.json").read_text()), []
            )

    def test_snapshot_cannot_overwrite_existing_directory(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(collector, "collect_profile") as run,
        ):
            with self.assertRaises(FileExistsError):
                collector.main(["--output", directory])
            run.assert_not_called()

    def test_public_snapshot_reconciles_with_raw(self):
        folder = Path(__file__).resolve().parents[1] / "results/review_2026_10_16"
        result = audit.reconcile_snapshot(folder)
        self.assertEqual(result["default"]["week2_records"], 39)
        self.assertEqual(result["quyen"]["week2_records"], 75)


if __name__ == "__main__":
    unittest.main()
