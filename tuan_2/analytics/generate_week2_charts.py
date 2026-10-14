"""Draw report-sized figures from exact two-account Week 2 analysis CSVs."""
from pathlib import Path
from datetime import datetime,timezone
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from weekly_comparison_charts import make_comparison_figure

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'results/week2_analysis';OUT=ROOT/'results/week2_charts'
OUT.mkdir(exist_ok=True)
CITY={'HoChiMinh':'TP. Hồ Chí Minh','HaNoi':'Hà Nội','DaNang':'Đà Nẵng'}
CITIES=['HoChiMinh','HaNoi','DaNang'];PROFILES=['default','quyen'];LABEL={'default':'Sinh viên Tiến Sơn','quyen':'Sinh viên Ngọc Quyên'}
COLOR={'default':'#2563EB','quyen':'#F59E0B'}
CITY_COLOR={'HoChiMinh':'#0D9488','HaNoi':'#7C3AED','DaNang':'#2563EB'}
plt.rcParams.update({'font.family':'Times New Roman','font.size':11,'axes.titlesize':13,'axes.labelsize':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white'})
manifest=[]
def rows(name):
    with (DATA/f'{name}.csv').open(encoding='utf-8-sig',newline='') as handle:return list(csv.DictReader(handle))
def value(row,key):return float(row[key])
def finish(fig,name,title,source):
    fig.suptitle(title,fontsize=14,y=.99)
    fig.text(.02,.01,'Nguồn: báo cáo dữ liệu của sinh viên Tiến Sơn và sinh viên Ngọc Quyên',fontsize=8,color='#444444')
    if name!='correlations':fig.tight_layout(rect=(0,.035,1,.865 if getattr(fig,'shared_legend',False) else .96))
    filename=f'{len(manifest)+1:02d}_{name}.png';fig.savefig(OUT/filename,dpi=250,bbox_inches='tight',pad_inches=.16);plt.close(fig)
    manifest.append({'file':filename,'title':title,'source_csv':source,'student_labels':LABEL,'account_colors':COLOR})

def shared_legend(fig,axis):
    handles,labels=axis.get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.955),ncol=2,frameon=False,fontsize=10)
    fig.shared_legend=True
def grouped(ax,items,keys,labels,ylabel):
    x=np.arange(len(items));width=.32
    for i,(key,label,color) in enumerate(zip(keys,labels,['#93C5FD','#2563EB'])):
        y=[value(row,key) for row in items];bars=ax.bar(x+(i-.5)*width,y,width,color=color,label=label)
        ax.bar_label(bars,labels=[f'{v:g}' if v.is_integer() else f'{v:.2f}' for v in y],padding=3,fontsize=9)
    ax.set_xticks(x,[LABEL[row['profile']] for row in items]);ax.set_ylabel(ylabel);ax.legend(frameon=False,ncol=2);ax.set_ylim(0,max(value(r,k) for r in items for k in keys)*1.2)

inventory=rows('account_inventory')
fig,ax=plt.subplots(figsize=(8.8,4.6));grouped(ax,inventory,['all_records','week2_records'],['Toàn bộ dữ liệu raw','Dữ liệu thuộc Tuần 2'],'Số bản ghi')
finish(fig,'data_scope','Quy mô dữ liệu tải về và phạm vi Tuần 2','account_inventory.csv')

stats=rows('city_statistics')
fig,ax=plt.subplots(figsize=(9,4.7));x=np.arange(3);w=.34
for i,p in enumerate(PROFILES):
    selected=[next(r for r in stats if r['profile']==p and r['city']==city) for city in CITIES]
    y=[value(r,'avg_aqi') for r in selected];sd=[value(r,'sd_aqi') for r in selected]
    bars=ax.bar(x+(i-.5)*w,y,w,yerr=sd,capsize=4,color=COLOR[p],label=f'{LABEL[p]} (n={selected[0]["sample_count"]}/đô thị)')
    ax.bar_label(bars,labels=[f'{v:.2f}' for v in y],padding=8,fontsize=9)
ax.set_xticks(x,[CITY[c] for c in CITIES]);ax.set_ylabel('US AQI');ax.set_ylim(0,200);ax.legend(frameon=False,fontsize=10);ax.axhline(100,color='#777777',linestyle='--',linewidth=1)
finish(fig,'aqi_city','AQI trung bình và độ lệch chuẩn của mẫu Tuần 2','city_statistics.csv')

fig,axes=plt.subplots(1,2,figsize=(10.2,4.7),sharey=True)
for ax,metric,title in zip(axes,['avg_pm2_5','avg_pm10'],['PM2.5','PM10']):
    for i,p in enumerate(PROFILES):
        data=[next(r for r in stats if r['profile']==p and r['city']==city) for city in CITIES]
        y=[value(r,metric) for r in data];bars=ax.bar(x+(i-.5)*w,y,w,color=COLOR[p],label=LABEL[p]);ax.bar_label(bars,fmt='%.2f',padding=3,fontsize=9)
    ax.set_xticks(x,['TP. HCM','Hà Nội','Đà Nẵng']);ax.set_title(title);ax.set_ylim(0,95)
shared_legend(fig,axes[0])
axes[0].set_ylabel('Nồng độ trung bình (µg/m³)')
finish(fig,'particulates','PM2.5 và PM10 trung bình theo đô thị và nguồn dữ liệu','city_statistics.csv')

raw=rows('raw_week2_both_accounts')
fig,ax=plt.subplots(figsize=(9.2,4.8));values=[];labels=[]
for city in CITIES:
    for p in PROFILES:
        values.append([value(r,'us_aqi') for r in raw if r['profile']==p and r['city']==city]);labels.append(f'{CITY[city]}\n{LABEL[p]}\n(n={len(values[-1])})')
box=ax.boxplot(values,patch_artist=True,tick_labels=labels,showmeans=True,meanprops={'marker':'D','markerfacecolor':'black','markeredgecolor':'black','markersize':4},medianprops={'color':'black'})
ax.tick_params(axis='x',labelsize=9)
for i,patch in enumerate(box['boxes']):patch.set_facecolor(COLOR[PROFILES[i%2]]);patch.set_alpha(.5)
ax.set_ylabel('US AQI');ax.set_ylim(0,190)
finish(fig,'aqi_distribution','Trung vị khoảng tứ phân vị và độ phân tán AQI','raw_week2_both_accounts.csv; distribution_statistics.csv')

hourly=rows('hourly_city');times=sorted({r['timestamp_utc'] for r in hourly});index={t:i for i,t in enumerate(times)}
fig,axes=plt.subplots(3,1,figsize=(9,7.5),sharex=True)
start=datetime.fromisoformat(times[0])
time_positions=[(datetime.fromisoformat(t)-start).total_seconds()/3600 for t in times]
for ax,city in zip(axes,CITIES):
    for p in PROFILES:
        points=sorted((r for r in hourly if r['profile']==p and r['city']==city),key=lambda r:r['timestamp_utc'])
        xp=[(datetime.fromisoformat(r['timestamp_utc'])-start).total_seconds()/3600 for r in points];yp=[value(r,'avg_aqi') for r in points]
        # Separate segments at gaps so absent hours are not drawn as measured trends.
        segx=[];segy=[]
        for i,(a,b) in enumerate(zip(xp,yp)):
            if i and a-xp[i-1]>1.01:segx.append(np.nan);segy.append(np.nan)
            segx.append(a);segy.append(b)
        ax.plot(segx,segy,marker='o' if p=='default' else 's',linestyle='-' if p=='default' else '--',color=COLOR[p],label=LABEL[p],linewidth=1.5,markersize=4)
    ax.set_title(CITY[city],loc='left',fontsize=11);ax.set_ylabel('AQI');ax.grid(axis='y',alpha=.2)
axes[0].legend(frameon=False,ncol=2,fontsize=10);ticks=list(range(0,int(max(time_positions))+1,2));axes[-1].set_xticks(ticks);axes[-1].set_xlabel('Số giờ kể từ mốc đầu tiên có dữ liệu trong mẫu Tuần 2')
finish(fig,'hourly_aqi','Biến thiên AQI tại các giờ thực sự có dữ liệu','hourly_city.csv')

fig,ax=plt.subplots(figsize=(10,4.3));grid=np.full((6,int(max(time_positions))+1),np.nan)
for ci,city in enumerate(CITIES):
    for pi,p in enumerate(PROFILES):
        for r in hourly:
            if r['city']==city and r['profile']==p:
                h=int((datetime.fromisoformat(r['timestamp_utc'])-start).total_seconds()/3600);grid[ci*2+pi,h]=value(r,'sample_count')
masked=np.ma.masked_invalid(grid);cmap=plt.cm.Blues.copy();cmap.set_bad('white');im=ax.imshow(masked,aspect='auto',vmin=0,vmax=np.nanmax(grid),cmap=cmap)
for i in range(6):
    for j in range(grid.shape[1]):
        if not np.isnan(grid[i,j]):ax.text(j,i,str(int(grid[i,j])),ha='center',va='center',color='white' if grid[i,j]>1.5 else 'black',fontsize=9)
ax.set_yticks(range(6),[f'{CITY[c]}\n{LABEL[p]}' for c in CITIES for p in PROFILES],fontsize=9);ax.set_xticks(range(0,grid.shape[1],2));ax.set_xlabel('Số giờ kể từ mốc đầu tiên có dữ liệu');fig.colorbar(im,ax=ax,label='Số mẫu trong giờ',ticks=[0,1,2,3])
finish(fig,'sampling_coverage','Mật độ lấy mẫu theo đô thị, sinh viên và giờ','hourly_city.csv')

cat=rows('category_distribution');fig,ax=plt.subplots(figsize=(9.8,4.8));labels=[];positions=range(6);colors={'Good':'#16A34A','Moderate':'#EAB308','Unhealthy':'#DC2626'}
for label in ['Good','Moderate','Unhealthy']:
    y=[]
    for city in CITIES:
        for p in PROFILES:
            entry=next((r for r in cat if r['city']==city and r['profile']==p and r['aqi_category']==label),None);y.append(value(entry,'fraction')*100 if entry else 0)
    ax.bar(positions,y,color=colors[label],label={'Good':'Tốt','Moderate':'Trung bình','Unhealthy':'Không tốt'}[label])
ax.set_xticks(positions,[f'{CITY[c]}\n{LABEL[p]}' for c in CITIES for p in PROFILES],fontsize=9);ax.set_ylabel('Tỷ lệ mẫu (%)');ax.set_ylim(0,120);ax.legend(frameon=False,ncol=3)
for i in positions:ax.text(i,102,'100%',ha='center',fontsize=9)
finish(fig,'categories','Cấp AQI xuất hiện trong mẫu Tuần 2 của mỗi đô thị','category_distribution.csv')

threshold=rows('threshold_exceedance');fig,ax=plt.subplots(figsize=(9,4.5))
for i,condition in enumerate(['AQI >= 100','PM2.5 >= 35.5','AQI OR PM2.5']):
    y=[value(next(r for r in threshold if r['city']==c and r['profile']==p and r['condition']==condition),'fraction')*100 for c in CITIES for p in PROFILES]
    ax.bar(np.arange(6)+(i-1)*.23,y,.23,color=['#2563EB','#F59E0B','#16A34A'][i],label=condition)
ax.set_xticks(range(6),[f'{CITY[c]}\n{LABEL[p]}' for c in CITIES for p in PROFILES],fontsize=9);ax.set_ylim(0,120);ax.set_ylabel('Tỷ lệ mẫu thỏa điều kiện (%)');ax.legend(frameon=False,fontsize=9,ncol=3)
finish(fig,'exceedance','Tỷ lệ mẫu vượt các ngưỡng cấu hình cảnh báo','threshold_exceedance.csv')

paired=rows('matched_account_hours');fig,axes=plt.subplots(1,2,figsize=(10.2,4.8))
for ax,metric,label in zip(axes,['delta_us_aqi','delta_pm2_5'],['Chênh lệch AQI','Chênh lệch PM2.5 (µg/m³)']):
    for i,c in enumerate(CITIES):
        data=[value(r,metric) for r in paired if r['city']==c];ax.scatter([i]*len(data),data,color=CITY_COLOR[c],alpha=.75,s=38);ax.plot([i-.2,i+.2],[np.mean(data)]*2,color=CITY_COLOR[c],linewidth=2)
    ax.set_xticks(range(3),['TP. HCM','Hà Nội','Đà Nẵng']);ax.axhline(0,color='#999999',linestyle='--');ax.set_ylabel(label)
finish(fig,'matched_account_difference','Chênh lệch Sinh viên Ngọc Quyên trừ Sinh viên Tiến Sơn','matched_account_hours.csv')

corr=rows('correlations');fig,axes=plt.subplots(1,2,figsize=(10.5,5.6))
for ax,key,title in zip(axes,['pearson_r','spearman_r'],['Pearson','Spearman']):
    arr=np.array([[value(next(r for r in corr if r['city']==c and r['profile']==p and r['variable']==v),key) for v in ['temperature_2m','relative_humidity_2m','wind_speed_10m']] for c in CITIES for p in PROFILES])
    im=ax.imshow(arr,vmin=-1,vmax=1,cmap='coolwarm',aspect='auto')
    for i in range(6):
        for j in range(3):ax.text(j,i,f'{arr[i,j]:.3f}',ha='center',va='center',fontsize=10,color='white' if abs(arr[i,j])>.8 else 'black')
    ax.set_title(title);ax.set_xticks(range(3),['Nhiệt độ','Độ ẩm','Gió']);ax.set_yticks(range(6),[f'{CITY[c]}\n{LABEL[p]}' for c in CITIES for p in PROFILES],fontsize=9)
fig.subplots_adjust(left=.16,right=.84,bottom=.14,top=.83,wspace=.65)
color_axis=fig.add_axes([.88,.16,.02,.64]);fig.colorbar(im,cax=color_axis,label='Hệ số tương quan')
finish(fig,'correlations','Tương quan PM2.5 với khí tượng trong tập mẫu Tuần 2','correlations.csv')

fig,axes=plt.subplots(1,3,figsize=(10.5,4.4))
for ax,c in zip(axes,CITIES):
    for p in PROFILES:
        group=[r for r in raw if r['city']==c and r['profile']==p];ax.scatter([value(r,'temperature_2m') for r in group],[value(r,'pm2_5') for r in group],label=f'{LABEL[p]} n={len(group)}',color=COLOR[p],marker='o' if p=='default' else '^',alpha=.8,s=30)
    ax.set_title(CITY[c],fontsize=11);ax.set_xlabel('Nhiệt độ (°C)')
shared_legend(fig,axes[0])
axes[0].set_ylabel('PM2.5 (µg/m³)')
finish(fig,'pm25_temperature','Quan hệ giữa nhiệt độ và PM2.5 trên các bản ghi thực tế','raw_week2_both_accounts.csv')

dist=rows('distribution_statistics');fig,axes=plt.subplots(1,3,figsize=(10.5,4.5))
for ax,v,title in zip(axes,['carbon_monoxide','nitrogen_dioxide','ozone'],['CO','NO₂','O₃']):
    for i,p in enumerate(PROFILES):
        y=[value(next(r for r in dist if r['city']==c and r['profile']==p and r['variable']==v),'mean') for c in CITIES];bars=ax.bar(np.arange(3)+(i-.5)*.34,y,.34,color=COLOR[p],label=LABEL[p]);ax.bar_label(bars,fmt='%.1f',fontsize=8,padding=3)
    ax.set_xticks(range(3),['TP.HCM','Hà Nội','Đà Nẵng']);ax.set_title(title);ax.set_ylim(0,ax.get_ylim()[1]*1.2)
shared_legend(fig,axes[0])
axes[0].set_ylabel('Nồng độ trung bình (µg/m³)')
finish(fig,'gaseous_pollutants','CO NO₂ và O₃ trung bình theo đô thị và nguồn dữ liệu','distribution_statistics.csv')

runtime=[r for r in rows('lambda_runtime') if r['scope']=='week2'];fig,axes=plt.subplots(1,2,figsize=(9.3,4.5))
for ax,key,label in zip(axes,['duration_ms','billed_duration_ms'],['Thời gian xử lý (ms)','Thời gian tính phí (ms)']):
    arrays=[[value(r,key) for r in runtime if r['profile']==p] for p in PROFILES];box=ax.boxplot(arrays,tick_labels=[f'{LABEL[p]}\n(n={len(a)})' for p,a in zip(PROFILES,arrays)],patch_artist=True,medianprops={'color':'black'});ax.tick_params(axis='x',labelsize=9)
    for patch,p in zip(box['boxes'],PROFILES):patch.set_facecolor(COLOR[p]);patch.set_alpha(.5)
    ax.set_ylabel(label);ax.set_ylim(0,max(max(v) for v in arrays)*1.15)
finish(fig,'lambda_runtime','Phân bố thời gian Lambda từ các dòng REPORT thuộc Tuần 2','lambda_runtime.csv')

scan=rows('partition_scan_comparison');fig,ax=plt.subplots(figsize=(8.8,4.7))
for i,key in enumerate(['time_only_bytes','partition_filtered_bytes']):
    bars=ax.bar(np.arange(2)+(i-.5)*.34,[value(r,key)/1024 for r in scan],.34,label=['Chỉ lọc timestamp','Lọc thêm phân vùng'][i],color=['#93C5FD','#2563EB'][i]);ax.bar_label(bars,fmt='%.2f',padding=3)
ax.set_xticks(range(2),[f'{LABEL[r["profile"]]}\nGiảm quét {value(r,"scan_reduction_fraction")*100:.2f}%' for r in scan]);ax.set_ylabel('Dung lượng quét (KiB)');ax.legend(frameon=False);ax.set_ylim(0,150)
finish(fig,'partition_scan','Đối chứng dung lượng quét với cùng số bản ghi Tuần 2','partition_scan_comparison.csv')

query=rows('query_metrics');names=[r['name'] for r in query if r['profile']=='default'];fig,ax=plt.subplots(figsize=(10,6.3))
for i,p in enumerate(PROFILES):
    y=[value(next(r for r in query if r['profile']==p and r['name']==name),'execution_time_ms') for name in names];ax.barh(np.arange(len(names))+(i-.5)*.34,y,.34,color=COLOR[p],label=LABEL[p])
ax.set_yticks(range(len(names)),[name.replace('_',' ') for name in names]);ax.invert_yaxis();ax.set_xlabel('EngineExecutionTime (ms)');ax.legend(frameon=False)
finish(fig,'query_time','Thời gian thực thi 24 truy vấn trong hai báo cáo dữ liệu','query_metrics.csv')

comparison=rows('weekly_comparison');fig,axes=plt.subplots(1,2,figsize=(10.2,4.8))
for ax,p in zip(axes,PROFILES):
    data=[next(r for r in comparison if r['profile']==p and r['city']==c) for c in CITIES]
    for i,key in enumerate(['week1_avg_aqi','week2_avg_aqi']):
        bars=ax.bar(np.arange(3)+(i-.5)*.34,[value(r,key) for r in data],.34,color=['#93C5FD','#2563EB'][i],label=f'Tuần {i+1}');ax.bar_label(bars,fmt='%.2f',fontsize=8,padding=3)
    ax.set_xticks(range(3),['TP.HCM','Hà Nội','Đà Nẵng']);ax.set_title(f'{LABEL[p]}: n₁={data[0]["week1_samples"]}, n₂={data[0]["week2_samples"]} / đô thị');ax.set_ylim(0,200);ax.legend(frameon=False)
axes[0].set_ylabel('AQI trung bình')
finish(fig,'week_comparison','So sánh các mẫu thuộc Tuần 1 và Tuần 2 trong dữ liệu vừa tải','weekly_comparison.csv')

submitted=rows('submitted_week1_comparison')
for metric,name,title in [
    ('aqi','submitted_week1_aqi','AQI trung bình: bộ báo cáo Tuần 1 và mẫu Tuần 2'),
    ('pm25','submitted_week1_pm25','PM2.5 trung bình: bộ báo cáo Tuần 1 và mẫu Tuần 2'),
]:
    fig,series=make_comparison_figure(submitted,metric)
    finish(fig,name,title,'submitted_week1_comparison.csv')
    manifest[-1]['comparison_scope']='Retained Week 1 submission including backfill; separate observed Week 2 student samples.'
    manifest[-1]['series']=series

(OUT/'chart_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'charts':len(manifest),'output':str(OUT)},ensure_ascii=False))
