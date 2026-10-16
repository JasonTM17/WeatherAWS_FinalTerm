"""Validate repository links, weekly worklogs, CSV inventory and AWS snapshots."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import statistics
import subprocess
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
CATALOG = "docs/csv_catalog.csv"
FIELDS = ["path", "data_rows", "columns", "bytes", "sha256", "scope"]


def csv_rows(path):
    blob = Path(path).read_bytes()
    reader = csv.DictReader(
        io.StringIO(blob.decode("utf-8-sig"), newline=""), strict=True
    )
    header = reader.fieldnames
    if (
        not header
        or any(not h.strip() for h in header)
        or len(header) != len(set(header))
    ):
        raise ValueError(f"Invalid CSV header: {path}")
    rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f"CSV row width differs from header: {path}")
    return header, rows


def raw_city_statistics(raw):
    cities = defaultdict(list)
    for row in raw:
        cities[row["city"]].append(row)
    return {
        city: {
            "sample_count": len(rows),
            "avg_aqi": statistics.mean(float(r["us_aqi"]) for r in rows),
            "avg_pm2_5": statistics.mean(float(r["pm2_5"]) for r in rows),
        }
        for city, rows in cities.items()
    }


def reconcile_city_statistics(raw, aggregate):
    calculated = raw_city_statistics(raw)
    observed = {r["city"]: r for r in aggregate}
    if len(observed) != len(aggregate) or calculated.keys() != observed.keys():
        raise ValueError("City aggregate keys do not match raw data")
    for city, values in calculated.items():
        for key, expected in values.items():
            actual = float(observed[city][key])
            if not math.isfinite(actual) or not math.isclose(
                actual, expected, rel_tol=1e-11, abs_tol=1e-9
            ):
                raise ValueError(f"City aggregate mismatch: {city}/{key}")
    return calculated


def reconcile_snapshot(folder):
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        path = (folder / item["path"]).resolve()
        if not path.is_relative_to(folder.resolve()):
            raise ValueError("Snapshot manifest escapes its directory")
        if (
            hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]
            or path.stat().st_size != item["bytes"]
        ):
            raise ValueError(f"Snapshot hash mismatch: {item['path']}")
    results = {}
    for profile in ("default", "quyen"):
        base = folder / profile
        _, raw = csv_rows(base / "raw_week2.csv")
        _, all_raw = csv_rows(base / "raw_all.csv")
        _, aggregate = csv_rows(base / "city_week2.csv")
        calculated = reconcile_city_statistics(raw, aggregate)
        source = {r["record_id"]: r for r in all_raw}
        if len(source) != len(all_raw) or any(
            source.get(r["record_id"]) != r for r in raw
        ):
            raise ValueError("Weekly raw is not an exact subset of all raw")
        start, end = "2026-10-11 17:00:00", "2026-10-18 17:00:00"
        if [r for r in all_raw if start <= r["timestamp_utc"] < end] != raw:
            raise ValueError("Weekly filter differs from raw query")
        _, category = csv_rows(base / "category_week2.csv")
        counts = Counter((r["city"], r["aqi_category"]) for r in raw)
        if {
            (r["city"], r["aqi_category"]): int(r["sample_count"]) for r in category
        } != counts:
            raise ValueError("AQI category counts differ from raw")
        queries = json.loads((base / "queries.json").read_text(encoding="utf-8"))
        expected_queries = {
            "raw_all",
            "raw_week2",
            "city_week2",
            "category_week2",
            "hour_city_week2",
            "partition_all",
            "quality_all",
        }
        if (
            len(queries) != len(expected_queries)
            or {q["name"] for q in queries} != expected_queries
        ):
            raise ValueError(
                "Snapshot must contain each of the seven declared SELECT results"
            )
        if len({q["query_id"] for q in queries}) != len(queries):
            raise ValueError("Query execution IDs must be distinct")
        for q in queries:
            if q["status"] != "SUCCEEDED":
                raise ValueError("Snapshot contains unavailable query results")
            path = base / (q["name"] + ".csv")
            if (
                hashlib.sha256(path.read_bytes()).hexdigest() != q["csv_sha256"]
                or len(csv_rows(path)[1]) != q["row_count"]
            ):
                raise ValueError("Query metadata differs from CSV")
        results[profile] = {
            "all_records": len(all_raw),
            "week2_records": len(raw),
            "cities": calculated,
            "query_count": len(queries),
            "first_utc": min(r["timestamp_utc"] for r in raw),
            "last_utc": max(r["timestamp_utc"] for r in raw),
            "observed_days": len({r["timestamp_utc"][:10] for r in raw}),
            "city_hour_groups": len(
                {(r["city"], r["timestamp_utc"][:13]) for r in raw}
            ),
        }
    return results


def repository_paths():
    return sorted(
        set(
            subprocess.check_output(
                ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
            ).splitlines()
        )
    )


def catalog_rows(paths):
    rows = []
    for relative in paths:
        if not relative.endswith(".csv") or relative == CATALOG:
            continue
        path = ROOT / relative
        header, data = csv_rows(path)
        scope = (
            "weekly-worklog"
            if path.name == "worklog.csv"
            else "saved-report-input-or-analysis"
        )
        if "/review_" in relative:
            scope = "aws-review-2026-10-16"
        rows.append(
            {
                "path": relative,
                "data_rows": str(len(data)),
                "columns": str(len(header)),
                "bytes": str(path.stat().st_size),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "scope": scope,
            }
        )
    return rows


def validate_worklogs():
    _, rows = csv_rows(ROOT / "worklog.csv")
    expected = {
        ("Tuần 1", "24110054"): Decimal("9.5"),
        ("Tuần 1", "24110051"): Decimal("9.0"),
        ("Tuần 2", "24110054"): Decimal("10.0"),
        ("Tuần 2", "24110051"): Decimal("9.5"),
    }
    actual = {(r["week"], r["student_id"]): Decimal(r["duration_hours"]) for r in rows}
    if len(rows) != 4 or actual != expected:
        raise ValueError("Weekly hours differ from confirmed student totals")
    for row in rows:
        for relative in row["evidence_paths"].split("; "):
            path = (ROOT / relative).resolve()
            if not path.is_relative_to(ROOT) or not path.exists():
                raise ValueError(f"Missing worklog evidence: {relative}")
    for week in (1, 2):
        if csv_rows(ROOT / f"tuan_{week}/worklog.csv")[1] != [
            r for r in rows if r["week"] == f"Tuần {week}"
        ]:
            raise ValueError("Weekly CSV differs from root worklog")
    return str(sum(actual.values()))


def validate_links(paths):
    count = 0
    tracked = set(paths)
    for relative in paths:
        path = ROOT / relative
        if path.suffix != ".md":
            continue
        for target in re.findall(
            r"!?\[[^\]\n]*\]\(([^\)\n]+)\)", path.read_text(encoding="utf-8-sig")
        ):
            url = urlsplit(target.strip().strip("<>"))
            if url.scheme or url.netloc:
                continue
            dest = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not dest.is_relative_to(ROOT) or not dest.exists():
                raise ValueError(f"Broken Markdown link: {relative} -> {target}")
            name = dest.relative_to(ROOT).as_posix()
            if dest.is_file() and name not in tracked:
                raise ValueError(
                    f"Markdown links to an unpublished file: {relative} -> {target}"
                )
            count += 1
    return count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Update the CSV catalog")
    mode.add_argument(
        "--check", action="store_true", help="Validate the checked-in catalog"
    )
    args = parser.parse_args(argv)
    paths = repository_paths()
    rows = catalog_rows(paths)
    if args.write:
        with (ROOT / CATALOG).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=FIELDS, quoting=csv.QUOTE_ALL, lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(rows)
    elif csv_rows(ROOT / CATALOG)[1] != rows:
        raise ValueError("CSV catalog is stale; run repository_audit.py --write")
    hours = validate_worklogs()
    links = validate_links(repository_paths())
    snapshots = {
        p.name: reconcile_snapshot(p)
        for p in (ROOT / "tuan_2/results").glob("review_*")
        if p.is_dir()
    }
    print(
        json.dumps(
            {
                "status": "PASS",
                "catalog_csv_files": len(rows),
                "worklog_hours": hours,
                "markdown_links": links,
                "snapshots": snapshots,
            },
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
