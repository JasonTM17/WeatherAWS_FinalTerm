"""Compare unchanged issued predictions with newly downloaded completed CAMS hours."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from common import ROOT, digest, read_csv, write_csv, write_json
from forecast import CITIES, LABELS, collect, score
from reconcile_analysis import partial_comparison

ISSUED = ROOT / 'tuan_3/results/forecast_issued_2026_10_18/forecast_24h.csv'


def summarize(issued, compared):
    """Each score is specific to one city/variable and its currently matched hours."""
    result=[]
    for city in CITIES:
        for variable in ('us_aqi','pm2_5'):
            expected=[r for r in issued if r['city']==city and r['variable']==variable]
            rows=sorted((r for r in compared if r['city']==city and r['variable']==variable),key=lambda r:r['timestamp_utc'])
            if not rows:
                continue
            result.append({'city':city,'variable':variable,'matched_hours':len(rows),'issued_hours':len(expected),
                'first_target_utc':rows[0]['timestamp_utc'],'last_target_utc':rows[-1]['timestamp_utc'],
                **score([r['later_model_value'] for r in rows],[r['predicted'] for r in rows])})
    return result


def plot_comparison(folder, compared, matched_hours):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    fig,axes=plt.subplots(1,2,figsize=(13,6))
    for ax,variable,unit in zip(axes,('us_aqi','pm2_5'),('US AQI','PM2.5 (µg/m³)')):
        for city,color in zip(CITIES,('#2563eb','#db2777','#059669')):
            rows=sorted((r for r in compared if r['city']==city and r['variable']==variable),key=lambda r:r['timestamp_utc'])
            x=[datetime.fromisoformat(r['timestamp_utc']) for r in rows]
            ax.plot(x,[float(r['later_model_value']) for r in rows],color=color,marker='o',label=LABELS[city]+' — mô hình tải về sau')
            ax.plot(x,[float(r['predicted']) for r in rows],color=color,linestyle='--',marker='x',label=LABELS[city]+' — dự báo đã phát hành')
        ax.set(xlabel='Thời điểm đích UTC',ylabel=unit)
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3,maxticks=6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M',tz=timezone.utc))
        ax.tick_params(axis='x',rotation=20)
        ax.grid(alpha=.2)
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.01),ncol=3,fontsize=8)
    fig.suptitle(f'Đối chiếu {matched_hours}/24 giờ đích đã hoàn tất; dữ liệu CAMS, không phải số đo trạm')
    fig.tight_layout(rect=(0,.18,1,.94));fig.savefig(folder/'issued_vs_later_model.png',dpi=180);plt.close(fig)


def run(output):
    output.mkdir(parents=True,exist_ok=False)
    issued=read_csv(ISSUED)
    before=digest(ISSUED.read_bytes())
    later,sources=[],[]
    for city,(lat,lon) in CITIES.items():
        rows,source=collect(city,lat,lon,output/'model_source')
        later.extend(rows);sources.append(source)
    cutoff=min(datetime.fromisoformat(s['historical_cutoff_exclusive_utc']) for s in sources)
    compared=partial_comparison(issued,later,cutoff)
    if not compared:
        raise ValueError('No completed target hours available to compare')
    metrics=summarize(issued,compared)
    write_csv(output/'history.csv',later,list(later[0]))
    write_csv(output/'comparison.csv',compared,list(compared[0]))
    write_csv(output/'comparison_metrics.csv',metrics,list(metrics[0]))
    matched={r['timestamp_utc'] for r in compared}
    if len(compared)!=len(matched)*6 or len(metrics)!=6 or digest(ISSUED.read_bytes())!=before:
        raise ValueError('Comparison coverage differs across the six series or issued input changed')
    plot_comparison(output,compared,len(matched))
    write_json(output/'provenance.json',{'captured_at_utc':datetime.now(timezone.utc).isoformat(),'sources':sources,
        'cutoff_exclusive_utc':cutoff.isoformat(),'issued_path':ISSUED.relative_to(ROOT).as_posix(),'issued_sha256':before,
        'matched_target_hours':len(matched),'issued_target_hours':24,'matched_values':len(compared),'issued_values':len(issued),
        'comparison_kind':'Unchanged issued predictions vs later downloaded CAMS model values, not station truth; revisions possible',
        'script_sha256_lf':digest(Path(__file__).read_bytes().replace(b'\r\n',b'\n'))})
    write_json(output/'manifest.json',{'files':[{'path':p.relative_to(output).as_posix(),'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size}
        for p in sorted(output.rglob('*')) if p.is_file()]})
    print(json.dumps({'matched_target_hours':len(matched),'matched_values':len(compared),'cutoff':cutoff.isoformat()}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
