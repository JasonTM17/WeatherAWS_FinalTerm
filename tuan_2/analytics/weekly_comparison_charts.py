"""Plot the retained Week 1 submission against each student's Week 2 sample.

Input: six rows from submitted_week1_comparison.csv (two students, three cities).
This module has no cloud access and does not modify source observations.
"""
from __future__ import annotations

import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CITIES = ('HoChiMinh', 'HaNoi', 'DaNang')
CITY_LABELS = ('TP. HCM', 'Hà Nội', 'Đà Nẵng')
STUDENTS = {'default': 'Sinh viên Tiến Sơn', 'quyen': 'Sinh viên Ngọc Quyên'}
COLORS = {'default': '#2563EB', 'quyen': '#F59E0B'}
BASELINE_SCOPE = 'submitted_week1_snapshot_including_backfill'


def comparison_series(rows, metric):
    """Validate source scope and return precisely the values used for each bar."""
    if metric not in ('aqi', 'pm25'):
        raise ValueError('The comparison metric must be aqi or pm25.')
    indexed = {(row['profile'], row['city']): row for row in rows}
    expected = {(student, city) for student in STUDENTS for city in CITIES}
    if len(rows) != len(expected) or set(indexed) != expected:
        raise ValueError('Expected one comparison row per student and city.')
    series = []
    for student, label in STUDENTS.items():
        selected = [indexed[(student, city)] for city in CITIES]
        if any(row.get('baseline_scope') != BASELINE_SCOPE for row in selected):
            raise ValueError('Use the retained Week 1 submission baseline.')
        if any(row.get('week2_scope') != 'observed_week2_samples' for row in selected):
            raise ValueError('Use the observed Week 2 sample scope.')
        first = [float(row[f'week1_avg_{metric}']) for row in selected]
        second = [float(row[f'week2_avg_{metric}']) for row in selected]
        first_n = [int(row['week1_samples']) for row in selected]
        second_n = [int(row['week2_samples']) for row in selected]
        if any(not math.isfinite(value) or value < 0 for value in first + second):
            raise ValueError('Comparison means must be finite and nonnegative.')
        if any(n <= 0 for n in first_n + second_n):
            raise ValueError('Comparison sample counts must be positive.')
        series.append({'profile': student, 'student': label, 'cities': list(CITIES),
                       'week1_values': first, 'week2_values': second,
                       'week1_samples': first_n, 'week2_samples': second_n})
    if (series[0]['week1_values'] != series[1]['week1_values'] or
            series[0]['week1_samples'] != series[1]['week1_samples']):
        raise ValueError('Both student comparisons must use the same submission baseline.')
    return series


def make_comparison_figure(rows, metric):
    """Build two separate panels; report sample sizes, units and a zero baseline."""
    series = comparison_series(rows, metric)
    figure, axes = plt.subplots(1, 2, figsize=(10.2, 4.8), sharey=True)
    maximum = max(max(s['week1_values'] + s['week2_values']) for s in series)
    for axis, item in zip(axes, series):
        for offset, values, color, label in [
            (-.17, item['week1_values'], '#94A3B8', 'Bộ báo cáo Tuần 1'),
            (.17, item['week2_values'], COLORS[item['profile']], 'Mẫu Tuần 2'),
        ]:
            bars = axis.bar([i + offset for i in range(3)], values, .34, color=color, label=label)
            axis.bar_label(bars, labels=[f'{value:.2f}' for value in values], fontsize=9, padding=3)
        axis.set_xticks(range(3), CITY_LABELS)
        first_n = '/'.join(str(n) for n in sorted(set(item['week1_samples'])))
        second_n = '/'.join(str(n) for n in sorted(set(item['week2_samples'])))
        axis.set_title(f'{item["student"]}\nn₁={first_n}, n₂={second_n} mẫu/đô thị', fontsize=12)
        axis.set_ylim(0, maximum * 1.25 if maximum else 1)
        axis.grid(axis='y', alpha=.15)
        axis.set_axisbelow(True)
        axis.legend(frameon=False, fontsize=9, loc='upper left')
    axes[0].set_ylabel('US AQI trung bình' if metric == 'aqi' else 'PM2.5 trung bình (µg/m³)')
    return figure, series
