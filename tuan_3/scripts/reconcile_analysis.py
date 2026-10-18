"""Recompute descriptive statistics and exploratory MA3 from retained evidence."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import shutil
import statistics
import subprocess

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from common import ROOT, PROFILES, digest, read_csv, write_csv, write_json
from forecast import CITIES, LABELS, collect, evaluate, score
from quality import instant

VARIABLES = {
    'us_aqi': ('US AQI', 'điểm'), 'pm2_5': ('PM2.5', 'µg/m³'), 'pm10': ('PM10', 'µg/m³'),
    'temperature_2m': ('Nhiệt độ', '°C'), 'relative_humidity_2m': ('Độ ẩm', '%'),
    'wind_speed_10m': ('Tốc độ gió', 'km/h'), 'carbon_monoxide': ('CO', 'µg/m³'), 'ozone': ('Ozone', 'µg/m³')}
WEATHER = ('temperature_2m', 'relative_humidity_2m', 'wind_speed_10m', 'carbon_monoxide', 'ozone')


def ranks(values):
    ordered = sorted(range(len(values)), key=lambda i: values[i])
    result = [0.0] * len(values)
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and values[ordered[end]] == values[ordered[start]]:
            end += 1
        for position in range(start, end):
            result[ordered[position]] = (start + 1 + end) / 2
        start = end
    return result


def correlation(x, y):
    if len(x) != len(y) or len(x) < 2:
        return None
    if not all(math.isfinite(float(v)) for v in [*x, *y]):
        raise ValueError('Nonfinite correlation input')
    if len(set(x)) < 2 or len(set(y)) < 2:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def recursive_mean(values, window, steps=24):
    if type(window) is not int or window < 1 or len(values) < window or steps < 1:
        raise ValueError('Invalid recursive-mean window/horizon')
    history = [float(v) for v in values]
    if not all(math.isfinite(v) for v in history):
        raise ValueError('Nonfinite training data')
    predictions = []
    for _ in range(steps):
        value = statistics.mean(history[-window:])
        history.append(value)
        predictions.append(value)
    return predictions


def descriptive(values):
    values = [float(v) for v in values]
    if not values or not all(math.isfinite(v) for v in values):
        raise ValueError('Descriptive statistics require finite observations')
    return {'n': len(values), 'mean': statistics.mean(values), 'median': statistics.median(values),
            'sample_std': statistics.stdev(values) if len(values) > 1 else None,
            'min': min(values), 'max': max(values),
            **{f'p{q}': float(np.percentile(values, q, method='linear')) for q in (25, 75, 90, 95)}}


def hourly_rows(raw):
    grouped = defaultdict(list)
    for row in raw:
        grouped[row['city'], instant(row['timestamp_utc']).replace(minute=0, second=0, microsecond=0)].append(row)
    return [{'city': city, 'timestamp_utc': hour.isoformat(), 'collection_count': len(rows),
             **{v: statistics.mean(float(r[v]) for r in rows) for v in VARIABLES}}
            for (city, hour), rows in sorted(grouped.items())]


def partial_comparison(issued, later, cutoff):
    lookup = {(r['city'], r['timestamp_utc']): r for r in later}
    compared = []
    for row in issued:
        target = datetime.fromisoformat(row['timestamp_utc'])
        if target >= cutoff or target <= datetime.fromisoformat(row['issued_at_utc']):
            continue
        actual = lookup.get((row['city'], row['timestamp_utc']))
        if actual is not None:
            value = actual[row['variable']]
            if value is not None and math.isfinite(float(value)):
                compared.append({**row, 'later_model_value': float(value),
                                 'error_vs_later_model': float(row['predicted']) - float(value),
                                 'comparison_status': 'compared_with_later_model_value'})
    return compared


def plots(output, stats, corrs, metrics):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
    fig, ax = plt.subplots(figsize=(11, 5))
    for i, (profile, color) in enumerate((('default', '#2563eb'), ('quyen', '#db2777'))):
        rows = [next(r for r in stats if r['profile'] == profile and r['scope'] == 'city_hour' and r['city'] == c and r['variable'] == 'us_aqi') for c in CITIES]
        bars = ax.bar(np.arange(3) + (i-.5)*.34, [r['mean'] for r in rows], .34,
                      yerr=[r['sample_std'] for r in rows], capsize=4, color=color, label=PROFILES[profile])
        for bar, row in zip(bars, rows):
            ax.annotate(f"n={row['n']}", (bar.get_x()+bar.get_width()/2, bar.get_height()),
                        xytext=(0, 5), textcoords='offset points', ha='center', fontsize=8)
    ax.set(xticks=np.arange(3), xticklabels=[LABELS[c] for c in CITIES], ylabel='US AQI',
           title='AQI trung bình theo đô thị–giờ; thanh sai số là độ lệch chuẩn mẫu')
    ax.legend(); ax.grid(axis='y', alpha=.2); fig.tight_layout(); fig.savefig(output/'city_hour_aqi.png', dpi=180); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), sharey=True)
    for ax, profile in zip(axes, PROFILES):
        matrix = [[next(r['pearson_r'] for r in corrs if r['profile'] == profile and r['scope'] == 'city_hour' and r['city'] == c and r['variable'] == v and r['target'] == 'pm2_5') for v in WEATHER] for c in CITIES]
        heat = ax.imshow(matrix, vmin=-1, vmax=1, cmap='RdBu_r', aspect='auto')
        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                if value is not None:
                    ax.text(x, y, f'{value:.2f}', ha='center', va='center', color='white' if abs(value) > .65 else 'black')
        ax.set(xticks=range(5), xticklabels=[VARIABLES[v][0] for v in WEATHER], yticks=range(3),
               yticklabels=[LABELS[c] for c in CITIES], title=PROFILES[profile]); ax.tick_params(axis='x', rotation=30)
    fig.subplots_adjust(bottom=.25, top=.82, right=.86, wspace=.2)
    color_axis = fig.add_axes([.90,.25,.015,.55])
    fig.colorbar(heat, cax=color_axis, label='Pearson r với PM2.5')
    fig.suptitle('Liên hệ trong tập giờ đã lưu; không diễn giải quan hệ nhân quả')
    fig.savefig(output/'hourly_correlations.png', dpi=180); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, variable in zip(axes, ('us_aqi', 'pm2_5')):
        for i, (model, color, label) in enumerate((('persistence','#64748b','Giá trị cuối'),('seasonal_naive_24h','#d97706','Lặp 24 giờ'),('moving_average_24h','#2563eb','MA 24 giờ'),('moving_average_3h','#059669','MA 3 giờ'))):
            vals = [next(r['mae'] for r in metrics if r['city'] == c and r['variable'] == variable and r['model'] == model) for c in CITIES]
            ax.bar(np.arange(3)+(i-1.5)*.18, vals, .18, color=color, label=label)
        ax.set(xticks=range(3), xticklabels=[LABELS[c] for c in CITIES], ylabel='MAE', title=VARIABLES[variable][0]); ax.tick_params(axis='x', rotation=15); ax.grid(axis='y',alpha=.2)
    axes[0].legend(fontsize=8); fig.suptitle('Thử nghiệm bổ sung MA 3 giờ trên cùng tập giữ lại; không đánh giá dữ liệu tương lai')
    fig.tight_layout(rect=(0,0,1,.94)); fig.savefig(output/'holdout_ma_comparison.png',dpi=180); plt.close(fig)


def run(output, collect_later=False, snapshot=None, later_source=None):
    output.mkdir(parents=True, exist_ok=False)
    base = ROOT/'tuan_3/results/integration_2026_10_18'
    stats, corrs, inputs = [], [], []
    for profile in PROFILES:
        path = ((snapshot or base/'snapshot')/profile/'raw_all.csv').resolve()
        raw = read_csv(path)
        inputs.append({'profile': profile, 'path': path.relative_to(ROOT).as_posix(), 'sha256': digest(path.read_bytes()), 'records': len(raw)})
        for scope, rows in (('raw',raw),('city_hour',hourly_rows(raw))):
            for city in CITIES:
                group = [r for r in rows if r['city'] == city]
                for variable, (_,unit) in VARIABLES.items():
                    stats.append({'profile':profile,'student':PROFILES[profile],'scope':scope,'city':city,'variable':variable,'unit':unit,**descriptive([r[variable] for r in group])})
                for target in ('pm2_5','us_aqi'):
                    for variable in WEATHER:
                        x,y = [float(r[variable]) for r in group],[float(r[target]) for r in group]
                        corrs.append({'profile':profile,'scope':scope,'city':city,'variable':variable,'target':target,'n':len(group),
                                      'pearson_r':correlation(x,y),'spearman_rho':correlation(ranks(x),ranks(y))})
    write_csv(output/'descriptive.csv',stats,list(stats[0]))
    write_csv(output/'correlations.csv',corrs,list(corrs[0]))
    history = read_csv(base/'forecast/hourly_model_history.csv')
    metrics, predictions = [], []
    for city in CITIES:
        rows = sorted((r for r in history if r['city'] == city),key=lambda r:r['timestamp_utc'])
        for variable in ('us_aqi','pm2_5'):
            old, checked, _ = evaluate(rows,variable)
            metrics.extend({'city':city,**r} for r in old)
            predictions.extend({'city':city,**r} for r in checked)
            estimated = recursive_mean([r[variable] for r in rows[:-24]],3)
            actual = [float(r[variable]) for r in rows[-24:]]
            metrics.append({'city':city,'variable':variable,'model':'moving_average_3h','train_hours':len(rows)-24,'test_hours':24,
                            'train_end':rows[-25]['timestamp_utc'],'test_start':rows[-24]['timestamp_utc'],'test_end':rows[-1]['timestamp_utc'],**score(actual,estimated)})
            predictions.extend({'city':city,'variable':variable,'model':'moving_average_3h','horizon_hours':i+1,'timestamp_utc':r['timestamp_utc'],'actual':a,'predicted':p}
                               for i,(r,a,p) in enumerate(zip(rows[-24:],actual,estimated)))
    write_csv(output/'ma_comparison_metrics.csv',metrics,list(metrics[0]))
    write_csv(output/'ma_comparison_predictions.csv',predictions,list(predictions[0]))
    later_status = {'status':'NOT_REQUESTED','matched_prediction_rows':0}
    if collect_later or later_source:
        later,sources = [],[]
        if later_source:
            later = read_csv(later_source/'history.csv')
            sources = json.loads((later_source/'provenance.json').read_text(encoding='utf-8'))['sources']
            (output/'later_model').mkdir()
            for city in CITIES:
                shutil.copyfile(later_source/f'{city}_api.json',output/'later_model'/f'{city}_api.json')
        else:
            for city,(lat,lon) in CITIES.items():
                rows,source = collect(city,lat,lon,output/'later_model')
                later.extend(rows);sources.append(source)
        write_csv(output/'later_model/history.csv',later,list(later[0]))
        issued = read_csv(ROOT/'tuan_3/results/forecast_issued_2026_10_18/forecast_24h.csv')
        cutoff = min(datetime.fromisoformat(s['historical_cutoff_exclusive_utc']) for s in sources)
        compared = partial_comparison(issued,later,cutoff)
        write_csv(output/'later_model/comparison.csv',compared,[*issued[0],'later_model_value','error_vs_later_model','comparison_status'])
        write_json(output/'later_model/provenance.json',{'sources':sources,'cutoff_exclusive_utc':cutoff.isoformat(),
                   'comparison_kind':'Previously issued predictions vs later downloaded CAMS model values, not station truth; retrospective model revisions possible'})
        later_status = {'status':'COLLECTED','matched_prediction_rows':len(compared),'issued_prediction_rows':len(issued),
                        'matched_hours_per_city_variable':len(compared)//6,'target_values_complete':len(compared)==len(issued)}
    plots(output,stats,corrs,metrics)
    write_json(output/'provenance.json',{'created_at':datetime.now(timezone.utc).isoformat(),
               'repository_head_at_capture':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
               'analysis_script_sha256_lf':digest(Path(__file__).read_bytes().replace(b'\r\n',b'\n')),'inputs':inputs,
               'statistics':'Raw and separately equal-weighted city-hour means; sample SD ddof1; linear percentiles; average tied ranks',
               'ma3_experiment':'Post-hoc exploratory comparison after reviewing the original holdout; no production model change or independent generalization claim',
               'aws_refresh':'Input snapshots retain their capture time/source/rules; consult snapshot.json for current AWS evidence',
               'later_model':later_status})
    files = [{'path':p.relative_to(output).as_posix(),'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size}
             for p in sorted(output.rglob('*')) if p.is_file()]
    write_json(output/'manifest.json',{'files':files})
    print(json.dumps({'descriptive_rows':len(stats),'correlation_rows':len(corrs),'metrics_rows':len(metrics),
                      'holdout_prediction_rows':len(predictions),'later_model':later_status,'retained_files':len(files)}),flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--collect-later-model',action='store_true')
    parser.add_argument('--snapshot',type=Path)
    parser.add_argument('--later-source',type=Path)
    args = parser.parse_args()
    run(args.output,args.collect_later_model,args.snapshot,args.later_source)
