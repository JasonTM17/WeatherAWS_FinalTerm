"""Chronological 24-hour holdout and baseline forecasts on real API model data."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import statistics
import urllib.parse
import urllib.request

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from common import finite, write_csv, write_json

CITIES = {'HoChiMinh': (10.8231, 106.6297), 'HaNoi': (21.0285, 105.8542), 'DaNang': (16.0544, 108.2022)}
LABELS = {'HoChiMinh': 'TP. Hồ Chí Minh', 'HaNoi': 'Hà Nội', 'DaNang': 'Đà Nẵng'}
MODELS = ('persistence', 'seasonal_naive_24h', 'moving_average_24h')


def moving_predictions(train, steps):
    history = [float(x) for x in train]
    predictions = []
    for _ in range(steps):
        prediction = statistics.mean(history[-24:])
        predictions.append(prediction)
        history.append(prediction)
    return predictions


def predict(train, horizon=24, model='moving_average_24h'):
    if len(train) < 24 or horizon != 24 or any(not math.isfinite(float(x)) for x in train):
        raise ValueError('Need 24 finite training observations and a 24h horizon')
    if model == 'persistence':
        return [float(train[-1])] * horizon
    if model == 'seasonal_naive_24h':
        return [float(x) for x in train[-24:]]
    if model == 'moving_average_24h':
        # Fixed-origin recursive prediction; no actual holdout values fed back.
        return moving_predictions(train, horizon)
    raise ValueError('Unknown forecasting model')


def score(actual, predicted):
    if not actual or len(actual) != len(predicted):
        raise ValueError('Metrics require equal nonempty vectors')
    errors = [float(p) - float(a) for a, p in zip(actual, predicted)]
    if not all(math.isfinite(e) for e in errors):
        raise ValueError('Nonfinite forecast error')
    return {'mae': statistics.mean(abs(e) for e in errors), 'rmse': math.sqrt(statistics.mean(e*e for e in errors)), 'bias': statistics.mean(errors)}


def consecutive_tail(records, variable):
    ordered = sorted(records, key=lambda r: r['timestamp_utc'])
    if len({r['timestamp_utc'] for r in ordered}) != len(ordered):
        raise ValueError('Hourly input has repeated timestamps')
    tail = []
    for row in reversed(ordered):
        if not finite(row.get(variable)):
            break
        if tail and datetime.fromisoformat(tail[-1]['timestamp_utc']) - datetime.fromisoformat(row['timestamp_utc']) != timedelta(hours=1):
            break
        tail.append(row)
    return list(reversed(tail))


def future_forecast(records, variable, issued_at):
    if issued_at.tzinfo is None:
        raise ValueError('Forecast issuance must have an explicit timezone')
    issued_at = issued_at.astimezone(timezone.utc)
    series = consecutive_tail(records, variable)
    if len(series) < 24:
        raise ValueError('Need at least 24 consecutive completed observation hours')
    origin = datetime.fromisoformat(series[-1]['timestamp_utc']).astimezone(timezone.utc)
    issue_hour = issued_at.replace(minute=0, second=0, microsecond=0)
    if origin >= issue_hour:
        raise ValueError('Training data includes an incomplete or future hour')
    first_target = issue_hour + timedelta(hours=1)
    gap = (first_target-origin).total_seconds()/3600
    if not gap.is_integer() or not 1 <= gap <= 24:
        raise ValueError('Observation-to-target gap is not an integral hour or exceeds 24 hours')
    gap = int(gap)
    # Bridge the unobserved current hour recursively, then emit 24 strictly future targets.
    estimates = moving_predictions([float(r[variable]) for r in series], gap+23)
    return [{'variable': variable, 'model': 'moving_average_24h', 'origin_utc': origin.isoformat(),
             'issued_at_utc': issued_at.isoformat(), 'forecast_hour': i+1, 'horizon_hours': gap+i,
             'timestamp_utc': (first_target+timedelta(hours=i)).isoformat(), 'predicted': estimates[gap-1+i],
             'status': 'unevaluated_future_prediction'} for i in range(24)]


def evaluate(records, variable, issued_at=None):
    series = consecutive_tail(records, variable)
    if len(series) < 96:
        raise ValueError('Need at least 72 contiguous training hours plus 24 holdout hours')
    train, holdout = series[:-24], series[-24:]
    train_values = [float(r[variable]) for r in train]
    actual = [float(r[variable]) for r in holdout]
    metrics, predictions = [], []
    for model in MODELS:
        estimates = predict(train_values, model=model)
        metrics.append({'variable': variable, 'model': model, 'train_hours': len(train), 'test_hours': 24,
                        'train_end': train[-1]['timestamp_utc'], 'test_start': holdout[0]['timestamp_utc'],
                        'test_end': holdout[-1]['timestamp_utc'], **score(actual, estimates)})
        predictions.extend({'variable': variable, 'model': model, 'horizon_hours': i + 1, 'timestamp_utc': row['timestamp_utc'],
                            'actual': value, 'predicted': predicted} for i, (row, value, predicted) in enumerate(zip(holdout, actual, estimates)))
    # Fixed method, selected before holdout evaluation; report all baselines.
    future = predict([float(r[variable]) for r in series], model='moving_average_24h')
    origin = datetime.fromisoformat(series[-1]['timestamp_utc'])
    future_rows = [{'variable': variable, 'model': 'moving_average_24h', 'origin_utc': origin.isoformat(), 'horizon_hours': i + 1,
                    'timestamp_utc': (origin + timedelta(hours=i+1)).isoformat(), 'predicted': value,
                    'status': 'retrospective_continuation_not_live_forecast'} for i, value in enumerate(future)]
    if issued_at is not None:
        future_rows = future_forecast(series, variable, issued_at)
    return metrics, predictions, future_rows


def collect(city, latitude, longitude, output):
    params = urllib.parse.urlencode({'latitude': latitude, 'longitude': longitude, 'hourly': 'pm2_5,us_aqi',
                                    'past_days': 7, 'forecast_days': 1, 'timezone': 'UTC'})
    url = 'https://air-quality-api.open-meteo.com/v1/air-quality?' + params
    request = urllib.request.Request(url, headers={'User-Agent': 'WeatherAWS-FinalTerm-academic-analysis/1.0'})
    with urllib.request.urlopen(request, timeout=30) as response:
        blob = response.read()
    payload = json.loads(blob)
    if payload.get('utc_offset_seconds') != 0:
        raise ValueError('Forecast source must be UTC')
    hourly = payload['hourly']
    if not all(len(hourly[k]) == len(hourly['time']) for k in ('pm2_5', 'us_aqi')):
        raise ValueError('API arrays differ in length')
    cutoff = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    records = []
    for i, timestamp in enumerate(hourly['time']):
        utc = datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc)
        if utc < cutoff:
            records.append({'city': city, 'timestamp_utc': utc.isoformat(), 'pm2_5': hourly['pm2_5'][i], 'us_aqi': hourly['us_aqi'][i]})
    if not records:
        raise ValueError('No historical timestamps before collection cutoff')
    write_json(output / f'{city}_api.json', payload)
    return records, {'city': city, 'url': url, 'captured_at': datetime.now(timezone.utc).isoformat(),
                     'historical_cutoff_exclusive_utc': cutoff.isoformat(), 'retained_hours': len(records),
                     'source_kind': 'Open-Meteo CAMS model series downloaded retrospectively; not archived Lambda measurements or vintage operational forecasts'}


def plots(output, holdout, future):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    for variable, unit in [('us_aqi', 'US AQI'), ('pm2_5', 'PM2.5 (µg/m³)')]:
        fig, axes = plt.subplots(3, 1, figsize=(11, 10))
        for ax, city in zip(axes, CITIES):
            rows = [r for r in holdout if r['city'] == city and r['variable'] == variable]
            reference = [r for r in rows if r['model'] == 'moving_average_24h']
            x = list(range(1, 25))
            ax.plot(x, [r['actual'] for r in reference], color='black', marker='o', markersize=3, label='Dữ liệu mô hình giữ lại')
            for model, color, label in [('persistence', '#64748b', 'Giữ giá trị cuối'), ('seasonal_naive_24h', '#d97706', 'Lặp 24 giờ trước'), ('moving_average_24h', '#2563eb', 'Trung bình trượt 24 giờ')]:
                values = [r['predicted'] for r in rows if r['model'] == model]
                ax.plot(x, values, label=label, color=color, linestyle='--')
            ax.set_title(LABELS[city]); ax.set_ylabel(unit); ax.grid(alpha=.2); ax.legend(fontsize=8, ncol=2)
        axes[-1].set_xlabel('Giờ trong khoảng đánh giá giữ lại (1–24)')
        fig.suptitle('Đánh giá hồi cứu 24 giờ trên dữ liệu mô hình Open-Meteo; không dùng dữ liệu kiểm tra để dự báo')
        fig.tight_layout(rect=(0, .02, 1, .96)); fig.savefig(output / f'holdout_{variable}.png', dpi=180); plt.close(fig)
        fig, ax = plt.subplots(figsize=(11, 4.5))
        for city, color in zip(CITIES, ['#2563eb', '#dc2626', '#059669']):
            selected = [r for r in future if r['city'] == city and r['variable'] == variable]
            ax.plot(range(1, 25), [r['predicted'] for r in selected], label=LABELS[city], color=color)
        ax.set(xlabel='Thứ tự 24 giờ đích sau thời điểm phát hành', ylabel=unit, title='Dự báo trung bình trượt 24 giờ — chưa có dữ liệu thực tế để đánh giá')
        ax.legend(); ax.grid(alpha=.2); fig.tight_layout(); fig.savefig(output / f'forecast_{variable}.png', dpi=180); plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a new forecast output directory')
    args.output.mkdir(parents=True)
    sources, all_records, metrics, holdout, future = [], [], [], [], []
    for city, (lat, lon) in CITIES.items():
        records, source = collect(city, lat, lon, args.output)
        all_records.extend(records); sources.append(source)
        for variable in ('us_aqi', 'pm2_5'):
            scored, checked, estimated = evaluate(records, variable, issued_at=datetime.now(timezone.utc))
            for target, entries in [(metrics, scored), (holdout, checked), (future, estimated)]:
                target.extend({'city': city, **r} for r in entries)
    for name, rows in [('hourly_model_history', all_records), ('forecast_metrics', metrics), ('holdout_predictions', holdout), ('forecast_24h', future)]:
        write_csv(args.output / f'{name}.csv', rows, list(rows[0]))
    write_json(args.output / 'provenance.json', {'sources': sources, 'method': 'Fixed recursive trailing24-hour arithmetic mean; chronological24h holdout; persistence/seasonal-naive baselines',
               'model_selected_using_test_set': False, 'evaluation_kind': 'Retrospective CAMS model reconstruction, not archived forecast-vintage skill',
               'future_predictions_evaluated': False,
               'future_target_rule': '24 whole-hour timestamps strictly after issued_at_utc; bridge unobserved hours recursively; horizon_hours is relative to last observation, forecast_hour is 1..24',
               'attribution': 'Open-Meteo; Copernicus Atmosphere Monitoring Service (CAMS); source terms https://open-meteo.com/en/docs/air-quality-api'})
    plots(args.output, holdout, future)
    print(json.dumps({'historical_model_rows': len(all_records), 'evaluation_rows': len(holdout), 'metrics_rows': len(metrics), 'future_prediction_rows': len(future)}))


if __name__ == '__main__':
    main()
