"""Render Vietnamese, print-sized charts from the saved Athena CSV snapshot."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = str(ROOT / "results" / "athena_queries")
CHARTS_DIR = str(ROOT / "results" / "charts")


def rows(name):
    with (Path(DATA_DIR) / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
})

CITY = {"HoChiMinh": "TP. Hồ Chí Minh", "DaNang": "Đà Nẵng", "HaNoi": "Hà Nội"}


def finish(fig, name):
    fig.text(0.01, 0.01, "Nguồn dữ liệu: Open-Meteo; kết quả Athena đã lưu",
             color="#444444", fontsize=8)
    Path(CHARTS_DIR).mkdir(parents=True, exist_ok=True)
    fig.savefig(Path(CHARTS_DIR) / name, dpi=260, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)



def plot_city_comparison():
    # Figure 4.1: three comparable AQI measures for each city.
    city = rows("avg_aqi_by_city.csv")
    names = [CITY[r["city"]] for r in city]
    x = np.arange(len(city))
    w = 0.23
    fig, ax = plt.subplots(figsize=(8.2, 4.35))
    for offset, key, label, color in [
        (-w, "min_aqi", "Thấp nhất", "#7A9BB7"),
        (0, "avg_aqi", "Trung bình", "#355C7D"),
        (w, "max_aqi", "Cao nhất", "#B85C5C"),
    ]:
        vals = [float(r[key]) for r in city]
        bars = ax.bar(x + offset, vals, width=w, label=label, color=color)
        for bar, val in zip(bars, vals):
            ax.annotate(f"{val:.1f}", (bar.get_x() + bar.get_width() / 2, val),
                        xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
    ax.set_xticks(x, names)
    ax.set_ylim(0, 205)
    ax.set_ylabel("Chỉ số US AQI")
    ax.set_title("So sánh US AQI theo ba đô thị")
    ax.grid(axis="y", alpha=0.18)
    ax.legend(ncol=3, frameon=False, loc="upper right", fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    finish(fig, "01_aqi_city_comparison.png")



def plot_hourly_trend():
    # Figure 4.2: hourly aggregate and unequal sample size.
    hours = sorted(rows("peak_pollution_hours.csv"), key=lambda r: int(r["hour"]))
    hh = [int(r["hour"]) for r in hours]
    pm25 = [float(r["avg_pm2_5"]) for r in hours]
    pm10 = [float(r["avg_pm10"]) for r in hours]
    aqi = [float(r["avg_aqi"]) for r in hours]
    fig, ax = plt.subplots(figsize=(8.2, 4.25))
    ax2 = ax.twinx()
    l1 = ax.plot(hh, pm25, color="#B54343", marker="o", markersize=3, linewidth=2, label="PM2.5")
    l2 = ax.plot(hh, pm10, color="#C17B35", marker="s", markersize=3, linewidth=1.8, label="PM10")
    l3 = ax2.plot(hh, aqi, color="#365E86", marker="^", markersize=3, linewidth=1.8, label="US AQI")
    ax.set_xticks(range(0, 24, 2))
    ax.set_xlim(0, 23)
    ax.set_xlabel("Giờ UTC")
    ax.set_ylabel("Nồng độ bụi (µg/m³)")
    ax2.set_ylabel("Chỉ số US AQI")
    ax.set_title("Biến thiên trung bình theo 24 khung giờ UTC")
    ax.grid(alpha=0.18)
    ax.legend(l1 + l2 + l3, [line.get_label() for line in l1 + l2 + l3],
              ncol=3, frameon=False, loc="upper left", fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    finish(fig, "02_peak_pollution_hours.png")



def plot_category_distribution():
    # Figure 4.3: category percentages; raw counts remain in the report table.
    category = rows("aqi_category_distribution.csv")
    cats = [
        ("Good", "Tốt", "#5A9B78"),
        ("Moderate", "Trung bình", "#E0B84F"),
        ("Unhealthy for Sensitive Groups", "Nhóm nhạy cảm", "#D88744"),
        ("Unhealthy", "Kém", "#B95555"),
    ]
    lookup = {(r["city"], r["aqi_category"]): float(r["percentage"]) for r in category}
    city_order = ["HoChiMinh", "DaNang", "HaNoi"]
    fig, ax = plt.subplots(figsize=(8.2, 4.3))
    bottom = np.zeros(3)
    for key, label, color in cats:
        vals = np.array([lookup.get((city_name, key), 0) for city_name in city_order])
        ax.bar(range(3), vals, bottom=bottom, width=0.62, color=color, label=label)
        for j, val in enumerate(vals):
            if val >= 6:
                ax.text(j, bottom[j] + val / 2, f"{val:.1f}%".replace(".", ","),
                        ha="center", va="center", fontsize=9, color="black")
        bottom += vals
    ax.set_xticks(range(3), [CITY[name] for name in city_order])
    ax.set_ylim(0, 115)
    ax.set_ylabel("Tỷ lệ mẫu (%)")
    ax.set_title("Phân bố cấp US AQI theo đô thị (52 mẫu/thành phố)")
    ax.legend(ncol=4, frameon=False, loc="upper center", fontsize=8.2)
    ax.grid(axis="y", alpha=0.15)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    finish(fig, "03_aqi_category_distribution.png")



def plot_correlation():
    w = 0.23
    city_order = ["HoChiMinh", "DaNang", "HaNoi"]
    # Figure 4.4: signed correlation coefficients; no causal interpretation.
    corr = rows("weather_correlation.csv")
    by_city = {r["city"]: r for r in corr}
    fig, ax = plt.subplots(figsize=(8.2, 4.3))
    for offset, key, label, color in [
        (-w, "corr_temp_pm25", "Nhiệt độ", "#C58B34"),
        (0, "corr_humidity_pm25", "Độ ẩm", "#4477B1"),
        (w, "corr_wind_pm25", "Tốc độ gió", "#4E9C7D"),
    ]:
        vals = [float(by_city[name][key]) for name in city_order]
        bars = ax.bar(np.arange(3) + offset, vals, width=w, label=label, color=color)
        for bar, val in zip(bars, vals):
            ax.annotate(f"{val:+.2f}", (bar.get_x() + bar.get_width() / 2, val),
                        xytext=(0, 3 if val >= 0 else -12), textcoords="offset points",
                        ha="center", fontsize=8.5)
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_xticks(range(3), [CITY[name] for name in city_order])
    ax.set_ylim(-0.9, 0.9)
    ax.set_ylabel("Hệ số tương quan Pearson r")
    ax.set_title("Tương quan với PM2.5 theo đô thị")
    ax.legend(ncol=3, frameon=False, fontsize=9, loc="upper right")
    ax.grid(axis="y", alpha=0.16)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    finish(fig, "04_weather_pm25_correlation.png")

if __name__ == "__main__":
    plot_city_comparison()
    plot_hourly_trend()
    plot_category_distribution()
    plot_correlation()
