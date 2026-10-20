"""Three chronological 24h historical holdouts; fixed recursive MA24, no issued-forecast claims."""
from __future__ import annotations

import argparse
from datetime import datetime,timedelta,timezone
import json
import math
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tuan_3/scripts'))
from common import digest,write_csv,write_json
from forecast import CITIES,LABELS,collect,predict,score

MODEL='moving_average_24h'
VARIABLES=('us_aqi','pm2_5')


def evaluate(records):
    series={city:{} for city in CITIES}
    for row in records:
        if row['city'] not in series:raise ValueError('Unexpected city')
        stamp=datetime.fromisoformat(row['timestamp_utc'])
        if stamp.utcoffset()!=timedelta(0):raise ValueError('Use UTC source timestamps')
        if stamp in series[row['city']]:raise ValueError('Repeated city/hour')
        series[row['city']][stamp]=row
    if any(not rows for rows in series.values()):raise ValueError('All three cities are required')
    end=min(max(rows) for rows in series.values())
    start=end-timedelta(hours=71)
    predictions=[];metrics=[]
    for window in range(3):
        first=start+timedelta(hours=24*window)
        training_times=[first-timedelta(hours=24-i) for i in range(24)]
        target_times=[first+timedelta(hours=i) for i in range(24)]
        for city,by_time in series.items():
            if any(stamp not in by_time for stamp in training_times+target_times):
                raise ValueError('A window has missing training/target hours')
            for variable in VARIABLES:
                train=[float(by_time[stamp][variable]) for stamp in training_times]
                actual=[float(by_time[stamp][variable]) for stamp in target_times]
                if not all(math.isfinite(v) for v in train+actual):raise ValueError('Nonfinite window data')
                # Only the 24 hours before the origin enter predict; holdout is never fed back.
                estimates=predict(train,horizon=24,model=MODEL)
                metadata={'window':window+1,'city':city,'variable':variable,'model':MODEL,
                    'train_start_utc':training_times[0].isoformat(),'train_end_utc':training_times[-1].isoformat(),
                    'target_start_utc':target_times[0].isoformat(),'target_end_utc':target_times[-1].isoformat()}
                metrics.append({**metadata,'train_hours':24,'target_hours':24,**score(actual,estimates)})
                predictions.extend({**metadata,'horizon_hours':i+1,'timestamp_utc':stamp.isoformat(),
                    'actual_model_value':actual[i],'predicted':estimates[i],
                    'error':estimates[i]-actual[i]} for i,stamp in enumerate(target_times))
    if len(predictions)!=432 or len(metrics)!=18:raise ValueError('Backtest coverage differs')
    return predictions,metrics


def plots(folder,predictions,metrics):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
    colors=['#2563eb','#db2777','#059669']
    for variable,title,unit in [('us_aqi','US AQI','Điểm AQI'),('pm2_5','PM2.5','µg/m³')]:
        fig,axes=plt.subplots(3,3,figsize=(14,9),squeeze=False)
        for row,city in enumerate(CITIES):
            for column,window in enumerate((1,2,3)):
                points=[p for p in predictions if p['city']==city and p['variable']==variable and p['window']==window]
                ax=axes[row][column]
                ax.plot(range(1,25),[p['actual_model_value'] for p in points],color='#d97706',label='Mô hình đối chiếu')
                ax.plot(range(1,25),[p['predicted'] for p in points],color=colors[column],linestyle='--',label='MA24 đệ quy')
                ax.set_title(f'{LABELS[city]} — cửa sổ {window}')
                ax.set_ylabel(unit);ax.grid(alpha=.2)
                if row==2:ax.set_xlabel('Bước dự báo 1–24')
                if row==0:ax.legend(fontsize=7)
        fig.suptitle(f'Backtest ba cửa sổ lịch sử 24 giờ — {title}',fontsize=13)
        fig.tight_layout(rect=(0,0,1,.96));fig.savefig(folder/f'backtest_{variable}.png',dpi=170);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    for ax,variable,unit in zip(axes,VARIABLES,('Điểm AQI','µg/m³')):
        for i,window in enumerate((1,2,3)):
            values=[next(m['mae'] for m in metrics if m['window']==window and m['city']==city and m['variable']==variable) for city in CITIES]
            bars=ax.bar([j+(i-1)*.24 for j in range(3)],values,width=.24,color=colors[i],label=f'Cửa sổ {window}')
            ax.bar_label(bars,fmt='%.2f',fontsize=7,padding=2)
        ax.set_xticks(range(3),[LABELS[c] for c in CITIES]);ax.set_ylabel('MAE, '+unit)
        ax.set_title('US AQI' if variable=='us_aqi' else 'PM2.5');ax.legend();ax.grid(axis='y',alpha=.2)
    fig.suptitle('Sai số tuyệt đối trung bình theo cửa sổ lịch sử');fig.tight_layout()
    fig.savefig(folder/'backtest_mae.png',dpi=170);plt.close(fig)


def run(output):
    output.mkdir(parents=True,exist_ok=False)
    protocol={'kind':'retrospective_chronological_backtest','model':MODEL,'windows':3,
        'training_hours_per_window':24,'target_hours_per_window':24,'cities':list(CITIES),
        'variables':list(VARIABLES),'model_fixed_before_evaluation':True,
        'operational_issued_forecasts':False,'station_observations':False}
    write_json(output/'protocol.json',protocol)
    records=[];sources=[]
    for city,(latitude,longitude) in CITIES.items():
        rows,source=collect(city,latitude,longitude,output/'model_source')
        records.extend(rows);sources.append(source)
    cutoff=min(datetime.fromisoformat(s['historical_cutoff_exclusive_utc']) for s in sources)
    records=[r for r in records if datetime.fromisoformat(r['timestamp_utc'])<cutoff]
    predictions,metrics=evaluate(records)
    write_csv(output/'history.csv',records,list(records[0]))
    write_csv(output/'predictions.csv',predictions,list(predictions[0]))
    write_csv(output/'metrics.csv',metrics,list(metrics[0]))
    plots(output,predictions,metrics)
    summary={**protocol,'status':'PASS','captured_at_utc':datetime.now(timezone.utc).isoformat(),
        'shared_cutoff_exclusive_utc':cutoff.isoformat(),'prediction_rows':len(predictions),
        'metric_rows':len(metrics),'target_hours':72,'sources':sources}
    write_json(output/'summary.json',summary)
    manifest={p.relative_to(output).as_posix():digest(p.read_bytes()) for p in sorted(output.rglob('*')) if p.is_file()}
    write_json(output/'manifest.json',manifest)
    return {k:v for k,v in summary.items() if k!='sources'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    try:print(json.dumps(run(args.output)))
    except Exception as error:
        print(json.dumps({'status':'FAIL','error_type':type(error).__name__}))
        raise SystemExit(1)
