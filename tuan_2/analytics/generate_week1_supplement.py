"""Add five analytical figures from the submitted Week 1 CSV snapshot.

The six original Athena exports are read-only inputs.  Descriptive statistics
use sample SD (ddof=1) and linearly interpolated quantiles.  Figures and the
manifest share the same unrounded arrays; display labels alone are rounded.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


REPOSITORY = Path(__file__).resolve().parents[2]
DEFAULT_DATA = REPOSITORY / "tuan_1/docs/Bao_cao_tuan_1_CSV_24110054_24110051"
DEFAULT_OUTPUT = REPOSITORY / "tuan_2/results/charts"
CITIES = ("HoChiMinh", "HaNoi", "DaNang")
CITY_LABEL = {"HoChiMinh": "TP. Hồ Chí Minh", "HaNoi": "Hà Nội", "DaNang": "Đà Nẵng"}
SHORT_LABEL = {"HoChiMinh": "TP. HCM", "HaNoi": "Hà Nội", "DaNang": "Đà Nẵng"}
CITY_COLOR = {"HoChiMinh": "#0D9488", "HaNoi": "#7C3AED", "DaNang": "#2563EB"}
VARIABLES = {
    "us_aqi": ("US AQI", "US AQI"),
    "pm2_5": ("PM2.5", "µg/m³"),
    "pm10": ("PM10", "µg/m³"),
    "temperature_2m": ("Nhiệt độ", "°C"),
    "relative_humidity_2m": ("Độ ẩm", "%"),
    "wind_speed_10m": ("Tốc độ gió", "km/h"),
}
SOURCE_FILES = (
    "raw_weather_aqi_records.csv", "avg_aqi_by_city.csv",
    "peak_pollution_hours.csv", "aqi_category_distribution.csv",
    "weather_correlation.csv", "query_metrics.csv",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPOSITORY).as_posix()
    except ValueError:
        return path.name


def displayed_rounding_tolerance(value: str) -> float:
    """Half of the source cell's final decimal unit, plus float tolerance."""
    places = max(0, -Decimal(value).as_tuple().exponent)
    return 0.5 * 10 ** (-places) + 1e-10


def assert_rounded_equal(actual: float, saved: str, label: str) -> None:
    if abs(actual - float(saved)) > displayed_rounding_tolerance(saved):
        raise ValueError(f"Saved aggregate does not match raw data: {label}")


def finite_values(raw: list[dict[str, str]], city: str, variable: str) -> np.ndarray:
    values = np.asarray([float(row[variable]) for row in raw if row["city"] == city])
    if len(values) != 52 or not np.isfinite(values).all():
        raise ValueError(f"Expected 52 finite observations for {city}/{variable}")
    return values


def verify_saved_snapshot(data: dict[str, list[dict[str, str]]]) -> dict:
    """Reconcile the four saved summaries and five query results to raw rows."""
    raw = data["raw_weather_aqi_records.csv"]
    if len(raw) != 156 or Counter(row["city"] for row in raw) != Counter({c: 52 for c in CITIES}):
        raise ValueError("The submitted Week 1 snapshot must contain 156 rows, 52 per city")
    if len({row["record_id"] for row in raw}) != 156:
        raise ValueError("Week 1 raw record_id values must identify 156 source rows")
    by_city = {row["city"]: row for row in data["avg_aqi_by_city.csv"]}
    if set(by_city) != set(CITIES):
        raise ValueError("The saved city summary must cover the three cities")
    for city in CITIES:
        saved = by_city[city]
        if int(saved["total_records"]) != 52:
            raise ValueError(f"Saved sample count differs for {city}")
        for variable, column in (
            ("us_aqi", "avg_aqi"), ("pm2_5", "avg_pm2_5"),
            ("pm10", "avg_pm10"), ("temperature_2m", "avg_temp"),
            ("relative_humidity_2m", "avg_humidity"),
        ):
            assert_rounded_equal(float(np.mean(finite_values(raw, city, variable))),
                                 saved[column], f"{city}/{column}")
        aqi = finite_values(raw, city, "us_aqi")
        if float(saved["min_aqi"]) != float(min(aqi)) or float(saved["max_aqi"]) != float(max(aqi)):
            raise ValueError(f"AQI extrema differ for {city}")

    hourly = data["peak_pollution_hours.csv"]
    if {int(row["hour"]) for row in hourly} != set(range(24)) or len(hourly) != 24:
        raise ValueError("The hourly summary must contain each UTC hour once")
    for saved in hourly:
        selected = [row for row in raw if int(row["hour"]) == int(saved["hour"])]
        if len(selected) != int(saved["sample_count"]):
            raise ValueError("Hourly sample count differs from raw rows")
        for variable, column in (("us_aqi", "avg_aqi"), ("pm2_5", "avg_pm2_5"), ("pm10", "avg_pm10")):
            assert_rounded_equal(statistics.mean(float(row[variable]) for row in selected),
                                 saved[column], f"hour {saved['hour']}/{column}")

    category_counts = Counter((row["city"], row["aqi_category"]) for row in raw)
    categories = data["aqi_category_distribution.csv"]
    if {(row["city"], row["aqi_category"]) for row in categories} != set(category_counts):
        raise ValueError("Saved categories differ from raw categories")
    for saved in categories:
        count = category_counts[saved["city"], saved["aqi_category"]]
        if count != int(saved["occurrence_count"]):
            raise ValueError("Saved category count differs from raw rows")
        assert_rounded_equal(count / 52 * 100, saved["percentage"], "category percentage")

    correlations = {row["city"]: row for row in data["weather_correlation.csv"]}
    if set(correlations) != set(CITIES):
        raise ValueError("Correlation summary must cover the three cities")
    for city in CITIES:
        pm25 = finite_values(raw, city, "pm2_5")
        for variable, column in (("temperature_2m", "corr_temp_pm25"),
                                 ("relative_humidity_2m", "corr_humidity_pm25"),
                                 ("wind_speed_10m", "corr_wind_pm25")):
            result = float(np.corrcoef(finite_values(raw, city, variable), pm25)[0, 1])
            assert_rounded_equal(result, correlations[city][column], f"{city}/{column}")

    metrics = data["query_metrics.csv"]
    expected_queries = {name.removesuffix(".csv") for name in SOURCE_FILES if name != "query_metrics.csv"}
    if len(metrics) != 5 or {row["query_name"] for row in metrics} != expected_queries:
        raise ValueError("Query metrics must describe the five actual saved exports")
    for row in metrics:
        if row["status"] != "SUCCEEDED" or int(row["result_rows"]) != len(data[row["output_csv"]]):
            raise ValueError("Query status or returned row count does not match its saved CSV")
        if int(row["execution_time_ms"]) <= 0 or int(row["bytes_scanned"]) <= 0:
            raise ValueError("Query metrics must retain the positive observed values")
    return {"status": "PASS", "raw_records": 156, "records_per_city": {c: 52 for c in CITIES},
            "city_summary": "PASS", "hourly_summary": "PASS", "category_summary": "PASS",
            "correlation_summary": "PASS", "query_metrics": "PASS"}


def descriptive_statistics(raw: list[dict[str, str]]) -> list[dict]:
    result = []
    for city in CITIES:
        pm25 = finite_values(raw, city, "pm2_5")
        for variable, (_, unit) in VARIABLES.items():
            values = finite_values(raw, city, variable)
            q1, median, q3, p95 = np.quantile(values, [0.25, 0.5, 0.75, 0.95], method="linear")
            result.append({
                "city": city, "city_label": CITY_LABEL[city], "variable": variable,
                "unit": unit, "n": len(values), "mean": float(np.mean(values)),
                "sd": float(np.std(values, ddof=1)), "min": float(np.min(values)),
                "q1": float(q1), "median": float(median), "q3": float(q3),
                "p95": float(p95), "max": float(np.max(values)),
                "pearson_pm25": float(np.corrcoef(values, pm25)[0, 1]),
            })
    return result


def style() -> None:
    plt.rcParams.update({
        "font.family": "Times New Roman", "font.size": 12,
        "axes.titlesize": 13, "axes.labelsize": 12,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.facecolor": "white", "axes.axisbelow": True,
    })


def finish(fig, output: Path, filename: str, title: str, arrays: dict,
           source_files: list[str], manifest: list[dict], note: str = "52 quan trắc mỗi đô thị") -> None:
    fig.suptitle(title, fontsize=15, y=0.985)
    fig.text(0.015, 0.015, f"Nguồn: dữ liệu Athena Tuần 1, {note}.", fontsize=9, color="#444444")
    fig.tight_layout(rect=(0, 0.055, 1, 0.94))
    path = output / filename
    fig.savefig(path, dpi=280, bbox_inches="tight", pad_inches=0.16)
    plt.close(fig)
    manifest.append({"file": filename, "source_image_id": filename.removesuffix(".png"),
                     "title": title, "source_csv": source_files, "plotted_arrays": arrays,
                     "image_sha256": sha256(path), "dpi": 280})


def plot_particulates(raw, output, manifest):
    x = np.arange(len(CITIES))
    fig, ax = plt.subplots(figsize=(8.6, 4.7))
    arrays = {"city_order": list(CITIES), "n": [52] * 3, "unit": "µg/m³"}
    for offset, variable, color in ((-0.18, "pm2_5", "#2563EB"), (0.18, "pm10", "#F59E0B")):
        values = [float(np.mean(finite_values(raw, city, variable))) for city in CITIES]
        bars = ax.bar(x + offset, values, width=0.34, color=color, label=VARIABLES[variable][0])
        ax.bar_label(bars, labels=[f"{v:.2f}".replace(".", ",") for v in values], padding=4, fontsize=11)
        arrays[variable] = values
    ax.set_xticks(x, [CITY_LABEL[city] for city in CITIES])
    ax.set_ylabel("Nồng độ trung bình (µg/m³)")
    ax.set_ylim(0, 45)
    ax.grid(axis="y", alpha=0.18)
    ax.legend(frameon=False, ncol=2, loc="upper right")
    finish(fig, output, "05_particulates_by_city.png", "PM2.5 và PM10 trung bình theo đô thị trong Tuần 1",
           arrays, ["raw_weather_aqi_records.csv", "avg_aqi_by_city.csv"], manifest)


def plot_weather(raw, output, manifest):
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 4.7))
    arrays = {"city_order": list(CITIES), "n": [52] * 3}
    for ax, variable in zip(axes, ("temperature_2m", "relative_humidity_2m", "wind_speed_10m")):
        name, unit = VARIABLES[variable]
        values = [float(np.mean(finite_values(raw, city, variable))) for city in CITIES]
        bars = ax.bar(range(3), values, width=0.60, color=[CITY_COLOR[city] for city in CITIES])
        ax.bar_label(bars, labels=[f"{v:.2f}".replace(".", ",") for v in values], padding=4, fontsize=11)
        ax.set_xticks(range(3), [SHORT_LABEL[city] for city in CITIES], fontsize=10.5)
        ax.set_title(name)
        ax.set_ylabel(unit)
        ax.set_ylim(0, max(values) * 1.22)
        ax.grid(axis="y", alpha=0.18)
        arrays[variable] = {"unit": unit, "mean": values}
    finish(fig, output, "06_weather_by_city.png", "Điều kiện khí tượng trung bình trong Tuần 1",
           arrays, ["raw_weather_aqi_records.csv", "avg_aqi_by_city.csv"], manifest)


def boxplot_arrays(values):
    summary = []
    for sample in values:
        q1, median, q3 = np.quantile(sample, [0.25, 0.5, 0.75], method="linear")
        iqr = q3 - q1
        inside = sample[(sample >= q1 - 1.5 * iqr) & (sample <= q3 + 1.5 * iqr)]
        summary.append({"q1": float(q1), "median": float(median), "q3": float(q3),
                        "whisker_low": float(np.min(inside)), "whisker_high": float(np.max(inside)),
                        "mean": float(np.mean(sample)), "sd": float(np.std(sample, ddof=1)),
                        "outliers": sample[(sample < np.min(inside)) | (sample > np.max(inside))].tolist()})
    return summary


def plot_distributions(raw, output, manifest):
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 5.0))
    arrays = {"city_order": list(CITIES), "n": [52] * 3, "whisker_rule": "1.5 * IQR",
              "quantile_method": "linear", "diamond": "arithmetic mean"}
    for ax, variable in zip(axes, ("us_aqi", "pm2_5")):
        values = [finite_values(raw, city, variable) for city in CITIES]
        boxes = ax.boxplot(values, patch_artist=True, tick_labels=[SHORT_LABEL[city] for city in CITIES],
                           showmeans=True, widths=0.58,
                           meanprops={"marker": "D", "markerfacecolor": "black", "markeredgecolor": "black", "markersize": 5},
                           medianprops={"color": "black", "linewidth": 1.4},
                           flierprops={"marker": "o", "markerfacecolor": "white", "markersize": 4})
        for box, city in zip(boxes["boxes"], CITIES):
            box.set_facecolor(CITY_COLOR[city])
            box.set_alpha(0.55)
        name, unit = VARIABLES[variable]
        ax.set_title(name)
        ax.set_ylabel(unit)
        ax.set_ylim(bottom=0)
        ax.grid(axis="y", alpha=0.18)
        arrays[variable] = {"unit": unit, "observations": [v.tolist() for v in values],
                            "boxplot_statistics": boxplot_arrays(values)}
    finish(fig, output, "07_aqi_pm25_distribution.png", "Phân bố AQI và PM2.5 của mẫu Tuần 1",
           arrays, ["raw_weather_aqi_records.csv"], manifest,
           "52 quan trắc mỗi đô thị; hình thoi biểu thị trung bình")


def plot_temperature_pairs(raw, output, manifest):
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 4.8), sharey=True)
    arrays = {"city_order": list(CITIES), "n": [52] * 3, "x_unit": "°C", "y_unit": "µg/m³"}
    for ax, city in zip(axes, CITIES):
        temperature = finite_values(raw, city, "temperature_2m")
        pm25 = finite_values(raw, city, "pm2_5")
        correlation = float(np.corrcoef(temperature, pm25)[0, 1])
        ax.scatter(temperature, pm25, color=CITY_COLOR[city], alpha=0.72, s=35,
                   edgecolors="white", linewidths=0.45)
        correlation_label = f"{correlation:.4f}".replace(".", ",")
        ax.set_title(f"{CITY_LABEL[city]}\nn = 52, r = {correlation_label}")
        ax.set_xlabel("Nhiệt độ (°C)")
        ax.grid(alpha=0.16)
        ax.set_ylim(bottom=0)
        arrays[city] = {"temperature_2m": temperature.tolist(), "pm2_5": pm25.tolist(),
                        "pearson_r": correlation}
    axes[0].set_ylabel("PM2.5 (µg/m³)")
    finish(fig, output, "08_temperature_pm25_scatter.png", "Các cặp nhiệt độ và PM2.5 quan sát được trong Tuần 1",
           arrays, ["raw_weather_aqi_records.csv", "weather_correlation.csv"], manifest)


def plot_query_metrics(metrics, output, manifest):
    ordered_names = ("avg_aqi_by_city", "peak_pollution_hours", "aqi_category_distribution",
                     "weather_correlation", "raw_weather_aqi_records")
    by_name = {row["query_name"]: row for row in metrics}
    ordered = [by_name[name] for name in ordered_names]
    labels = ["Trung bình đô thị", "Biến thiên theo giờ", "Phân bố cấp AQI", "Tương quan khí tượng", "Dữ liệu chi tiết"]
    duration = [int(row["execution_time_ms"]) for row in ordered]
    scanned = [int(row["bytes_scanned"]) for row in ordered]
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.8), sharey=True)
    y = np.arange(5)
    for ax, values, color, title, unit in zip(axes, (duration, scanned), ("#2563EB", "#0D9488"),
                                            ("Thời gian thực thi", "Dung lượng dữ liệu quét"), ("ms", "byte")):
        bars = ax.barh(y, values, color=color, height=0.6)
        ax.bar_label(bars, labels=[f"{v:,}".replace(",", ".") for v in values], padding=5, fontsize=11)
        ax.set_yticks(y, labels)
        ax.set_xlim(0, max(values) * 1.30)
        ax.set_title(title)
        ax.set_xlabel(unit)
        ax.grid(axis="x", alpha=0.18)
    axes[0].invert_yaxis()
    axes[1].ticklabel_format(axis="x", style="plain", useOffset=False)
    arrays = {"query_order": list(ordered_names), "query_labels": labels,
              "execution_time_ms": duration, "bytes_scanned": scanned,
              "result_rows": [int(row["result_rows"]) for row in ordered],
              "status": [row["status"] for row in ordered]}
    finish(fig, output, "09_query_performance.png", "Kết quả thực thi năm truy vấn Athena của Tuần 1",
           arrays, ["query_metrics.csv"], manifest, "5 truy vấn đã lưu kết quả thành công")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data_dir, output = args.data_dir.resolve(), args.output_dir.resolve()
    source_hashes = {name: sha256(data_dir / name) for name in SOURCE_FILES}
    data = {name: read_rows(data_dir / name) for name in SOURCE_FILES}
    verification = verify_saved_snapshot(data)
    raw = data["raw_weather_aqi_records.csv"]
    descriptive = descriptive_statistics(raw)
    output.mkdir(parents=True, exist_ok=True)
    derived_path = output / "week1_extended_statistics.csv"
    with derived_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(descriptive[0]), quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(descriptive)
    style()
    figures = []
    plot_particulates(raw, output, figures)
    plot_weather(raw, output, figures)
    plot_distributions(raw, output, figures)
    plot_temperature_pairs(raw, output, figures)
    plot_query_metrics(data["query_metrics.csv"], output, figures)
    if {name: sha256(data_dir / name) for name in SOURCE_FILES} != source_hashes:
        raise RuntimeError("Original Week 1 CSV inputs changed during generation")
    manifest = {
        "schema_version": 1, "week": 1,
        "scope": {"total_observations": 156, "observations_per_city": {c: 52 for c in CITIES},
                  "city_labels": CITY_LABEL},
        "statistics": {"sd": "sample standard deviation, ddof=1", "quantiles": "linear interpolation",
                       "boxplot_whiskers": "outermost observations within 1.5 * IQR fences",
                       "correlation": "Pearson r within each city"},
        "sources": {name: {"file": relative_path(data_dir / name), "sha256": source_hashes[name],
                           "rows": len(data[name])} for name in SOURCE_FILES},
        "derived_summary": {"file": derived_path.name, "rows": len(descriptive),
                            "sha256": sha256(derived_path)},
        "verification": verification, "original_csv_preserved": True, "figures": figures,
    }
    (output / "week1_chart_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                                       encoding="utf-8")
    print(json.dumps({"status": "PASS", "raw_records": 156, "statistics_rows": len(descriptive),
                      "figure_count": len(figures), "output_dir": relative_path(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
