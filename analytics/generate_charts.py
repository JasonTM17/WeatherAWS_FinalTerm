"""
Generate Trend and Analytical Visual Charts from Athena Query Results
Môn học: Cloud - Đợt 1 - 2026-2027
GVHD: Huỳnh Xuân Phụng
Sinh viên: 24110054
Account: 873674852386 | Region: us-east-1
"""

import os
import sys
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI']
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

CHARTS_DIR = os.path.abspath('results/charts')
DATA_DIR = os.path.abspath('results/athena_queries')
os.makedirs(CHARTS_DIR, exist_ok=True)

# 1. Chart 1: AQI City Comparison
def plot_city_comparison():
    csv_file = os.path.join(DATA_DIR, 'avg_aqi_by_city.csv')
    df = pd.read_csv(csv_file)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    x = np.arange(len(df))
    width = 0.25

    rects1 = ax.bar(x - width, df['avg_aqi'], width, label='Average AQI', color='#2563eb', alpha=0.9)
    rects2 = ax.bar(x, df['min_aqi'], width, label='Minimum AQI', color='#10b981', alpha=0.9)
    rects3 = ax.bar(x + width, df['max_aqi'], width, label='Maximum AQI', color='#ef4444', alpha=0.9)

    # Reference lines for EPA categories
    ax.axhline(50, color='#10b981', linestyle='--', linewidth=1, alpha=0.7, label='Good limit (50)')
    ax.axhline(100, color='#f59e0b', linestyle='--', linewidth=1, alpha=0.7, label='Moderate limit (100)')
    ax.axhline(150, color='#ef4444', linestyle='--', linewidth=1, alpha=0.7, label='Unhealthy limit (150)')

    ax.set_ylabel('US Air Quality Index (AQI)', fontsize=12, fontweight='bold')
    ax.set_title('Air Quality Index (AQI) Comparison by City in Vietnam\nAWS Learner Lab - Athena Analytics (Account: 873674852386)', fontsize=14, pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(df['city'], fontsize=11, fontweight='bold')
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    ax.set_ylim(0, 200)

    # Add data labels
    for rects in [rects1, rects2, rects3]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    out_path = os.path.join(CHARTS_DIR, '01_aqi_city_comparison.png')
    plt.savefig(out_path)
    plt.close()
    print(f"[OK] Generated: {out_path}")

# 2. Chart 2: Hourly Diurnal Pollution Pattern
def plot_hourly_trend():
    csv_file = os.path.join(DATA_DIR, 'peak_pollution_hours.csv')
    df = pd.read_csv(csv_file).sort_values('hour')

    fig, ax1 = plt.subplots(figsize=(11, 6), dpi=300)

    color_pm25 = '#dc2626'
    color_pm10 = '#d97706'
    color_aqi = '#2563eb'

    ax1.plot(df['hour'], df['avg_pm2_5'], marker='o', color=color_pm25, linewidth=2.5, label='PM2.5 (ug/m3)')
    ax1.plot(df['hour'], df['avg_pm10'], marker='s', color=color_pm10, linewidth=2, linestyle='--', label='PM10 (ug/m3)')
    ax1.set_xlabel('Hour of Day (UTC)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Particulate Matter (ug/m3)', color=color_pm25, fontsize=12, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color_pm25)
    ax1.set_xticks(range(0, 24, 2))

    ax2 = ax1.twinx()
    ax2.plot(df['hour'], df['avg_aqi'], marker='^', color=color_aqi, linewidth=2, linestyle=':', label='US AQI')
    ax2.set_ylabel('US AQI Index', color=color_aqi, fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color_aqi)

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', frameon=True, facecolor='white')

    plt.title('Diurnal Air Pollution Trend (Hourly PM2.5, PM10 & AQI)\nAWS Athena Serverless Query Results', fontsize=14, pad=15)
    plt.tight_layout()
    out_path = os.path.join(CHARTS_DIR, '02_peak_pollution_hours.png')
    plt.savefig(out_path)
    plt.close()
    print(f"[OK] Generated: {out_path}")

# 3. Chart 3: AQI Category Distribution
def plot_category_distribution():
    csv_file = os.path.join(DATA_DIR, 'aqi_category_distribution.csv')
    df = pd.read_csv(csv_file)

    pivot_df = df.pivot(index='city', columns='aqi_category', values='percentage').fillna(0)
    # Ensure standard order
    desired_cols = ['Good', 'Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy', 'Very Unhealthy', 'Hazardous']
    cols = [c for c in desired_cols if c in pivot_df.columns]
    pivot_df = pivot_df[cols]

    colors = {
        'Good': '#10b981',
        'Moderate': '#fbbf24',
        'Unhealthy for Sensitive Groups': '#f97316',
        'Unhealthy': '#ef4444',
        'Very Unhealthy': '#8b5cf6',
        'Hazardous': '#7f1d1d'
    }
    plot_colors = [colors[c] for c in cols]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    pivot_df.plot(kind='bar', stacked=True, color=plot_colors, ax=ax, edgecolor='white')
    plt.title('Air Quality Category Distribution by City (%)\nAWS Athena Aggregation', fontsize=14, pad=15)
    plt.xlabel('City', fontsize=12, fontweight='bold')
    plt.ylabel('Percentage (%)', fontsize=12, fontweight='bold')
    plt.legend(title='AQI Category', bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True)
    plt.xticks(rotation=0, fontsize=11, fontweight='bold')
    plt.ylim(0, 100)

    # Annotate percentage numbers
    for n, c in enumerate(cols):
        for i, val in enumerate(pivot_df[c]):
            if val > 5:
                # Calculate cumulative bottom
                bottom = sum(pivot_df[cols[j]].iloc[i] for j in range(n))
                ax.text(i, bottom + val / 2, f'{val:.0f}%', ha='center', va='center',
                        color='white' if c in ['Unhealthy', 'Very Unhealthy', 'Hazardous', 'Good'] else 'black',
                        fontweight='bold', fontsize=10)

    plt.tight_layout()
    out_path = os.path.join(CHARTS_DIR, '03_aqi_category_distribution.png')
    plt.savefig(out_path)
    plt.close()
    print(f"[OK] Generated: {out_path}")

# 4. Chart 4: Correlation Matrix
def plot_correlation():
    csv_file = os.path.join(DATA_DIR, 'weather_correlation.csv')
    df = pd.read_csv(csv_file)

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    x = np.arange(len(df))
    width = 0.25

    rects1 = ax.bar(x - width, df['corr_temp_pm25'], width, label='Corr(Temp, PM2.5)', color='#f59e0b')
    rects2 = ax.bar(x, df['corr_humidity_pm25'], width, label='Corr(Humidity, PM2.5)', color='#3b82f6')
    rects3 = ax.bar(x + width, df['corr_wind_pm25'], width, label='Corr(WindSpeed, PM2.5)', color='#10b981')

    ax.axhline(0, color='#666666', linestyle='-', linewidth=0.8)
    ax.set_ylabel('Pearson Correlation Coefficient (r)', fontsize=12, fontweight='bold')
    ax.set_title('Correlation Between Weather Factors and PM2.5 Concentration\nAWS Athena Analytics (Ho Chi Minh, Da Nang, Ha Noi)', fontsize=14, pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(df['city'], fontsize=11, fontweight='bold')
    ax.set_ylim(-1.0, 1.0)
    ax.legend(frameon=True, facecolor='white')

    for rects in [rects1, rects2, rects3]:
        for rect in rects:
            height = rect.get_height()
            y_pos = height + 0.04 if height >= 0 else height - 0.08
            ax.annotate(f'{height:.2f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3 if height >= 0 else -10),
                        textcoords="offset points",
                        ha='center', va='bottom' if height >= 0 else 'top',
                        fontsize=9, fontweight='bold')

    plt.tight_layout()
    out_path = os.path.join(CHARTS_DIR, '04_weather_pm25_correlation.png')
    plt.savefig(out_path)
    plt.close()
    print(f"[OK] Generated: {out_path}")

if __name__ == '__main__':
    plot_city_comparison()
    plot_hourly_trend()
    plot_category_distribution()
    plot_correlation()
    print("\n[ALL CHARTS GENERATED SUCCESSFULLY!]")
