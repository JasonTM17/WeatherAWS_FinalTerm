"""Analyze two live exports independently and retain explicit provenance."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
from collections import defaultdict,Counter
import csv,json,hashlib,math,statistics,argparse
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PROFILES=['default','quyen']
LABEL={'default':'Sơn','quyen':'Quyên'}
FIELDS=['temperature_2m','relative_humidity_2m','surface_pressure','wind_speed_10m','pm2_5','pm10','carbon_monoxide','nitrogen_dioxide','sulphur_dioxide','ozone','us_aqi']
START=datetime(2026,10,11,17,tzinfo=timezone.utc)
END=datetime(2026,10,18,17,tzinfo=timezone.utc)
def instant(value):
    parsed=datetime.fromisoformat(str(value).replace('Z','+00:00'))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
def read_csv(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as handle:return list(csv.DictReader(handle))
def write_csv(path,rows,headers=None):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    headers=headers or list(rows[0])
    with path.open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=headers,quoting=csv.QUOTE_ALL,lineterminator='\n');writer.writeheader();writer.writerows(rows)
def json_save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False,default=str)+'\n',encoding='utf-8')
def numbers(rows,key):
    return [float(r[key]) for r in rows if r.get(key) not in ('',None) and math.isfinite(float(r[key]))]
def ranks(values):
    ordered=sorted((value,index) for index,value in enumerate(values));result=[0.0]*len(values);i=0
    while i<len(ordered):
        j=i+1
        while j<len(ordered) and ordered[j][0]==ordered[i][0]:j+=1
        rank=(i+j-1)/2+1
        for _,index in ordered[i:j]:result[index]=rank
        i=j
    return result
def correlation(x,y):return statistics.correlation(x,y) if len(x)>=3 and statistics.pstdev(x)>0 and statistics.pstdev(y)>0 else None
def analyze(source,private,destination):
    source,private,destination=Path(source),Path(private),Path(destination)
    destination.mkdir(parents=True,exist_ok=True)
    collection=json.loads((private/'collection_manifest.json').read_text(encoding='utf-8'))
    at=instant(collection['started_at_utc'])
    all_rows={p:read_csv(source/p/'raw_all.csv') for p in PROFILES}
    weekly={p:read_csv(source/p/'raw_week2.csv') for p in PROFILES}
    inventory=[];quality=[];distribution=[];city_stats=[];hour_rows=[];day_rows=[];categories=[];thresholds=[];corr=[];hour_groups={};services=[];runtime=[];operational=[];cost=[];histories=[];objects=[];duplicate_rows=[]
    for profile in PROFILES:
        full,rows=all_rows[profile],weekly[profile]
        extracted=[]
        for path in (private/profile/'raw_objects').rglob('*'):
            if not path.is_file():continue
            text=path.read_text(encoding='utf-8-sig')
            try:
                parsed=json.loads(text);extracted.extend(parsed if isinstance(parsed,list) else [parsed])
            except json.JSONDecodeError:extracted.extend(json.loads(line) for line in text.splitlines() if line.strip())
        # Compare complete S3 and complete fresh Athena export by ID and sensor values.
        original={r['record_id']:r for r in extracted};assert len(full)==len(extracted)==len(original)
        for row in full:
            assert row['record_id'] in original
            for field in FIELDS:assert float(row[field])==float(original[row['record_id']][field])
        selected=[r for r in full if START<=instant(r['timestamp_utc'])<END]
        assert {r['record_id'] for r in selected}=={r['record_id'] for r in rows}
        manifests=json.loads((private/profile/'raw_download_manifest.json').read_text(encoding='utf-8'))
        for obj in manifests:objects.append({'profile':profile,**obj})
        keys=Counter((r['city'],r['timestamp_utc']) for r in full)
        for (city,timestamp),count in keys.items():
            if count>1:duplicate_rows.append({'profile':profile,'city':city,'timestamp_utc':timestamp,'record_count':count})
        hours=sorted({instant(r['timestamp_utc']).replace(minute=0,second=0,microsecond=0) for r in rows})
        inventory.append({'profile':profile,'account_label':LABEL[profile],'raw_objects':len(manifests),'raw_bytes':sum(o['bytes'] for o in manifests),'all_records':len(full),'unique_record_ids':len(original),'week2_records':len(rows),'week2_observed_hours':len(hours),'week2_days_observed':len({(instant(r['timestamp_utc'])+timedelta(hours=7)).date() for r in rows}),'week2_first_utc':min(r['timestamp_utc'] for r in rows),'week2_last_utc':max(r['timestamp_utc'] for r in rows),'duplicate_city_timestamp_rows':sum(n-1 for n in keys.values())})
        for scope,data in [('all',full),('week2',rows)]:
            for field in FIELDS:
                values=numbers(data,field)
                quality.append({'profile':profile,'scope':scope,'field':field,'records':len(data),'null_or_nonfinite':len(data)-len(values),'zero_values':sum(v==0 for v in values),'negative_values':sum(v<0 for v in values),'distinct_values':len(set(values))})
        bycity=defaultdict(list)
        for row in rows:bycity[row['city']].append(row)
        bucket_groups=defaultdict(list)
        for row in rows:bucket_groups[(row['city'],instant(row['timestamp_utc']).replace(minute=0,second=0,microsecond=0))].append(row)
        hour_groups[profile]=bucket_groups
        for (city,bucket),group in sorted(bucket_groups.items()):
            local=bucket+timedelta(hours=7);week_day=(local.date()-datetime(2026,10,12).date()).days+1
            hour_rows.append({'profile':profile,'city':city,'timestamp_utc':bucket.isoformat(),'day_of_week2':week_day,'hour_utc':bucket.hour,'sample_count':len(group),'avg_aqi':statistics.mean(numbers(group,'us_aqi')),'avg_pm2_5':statistics.mean(numbers(group,'pm2_5')),'avg_pm10':statistics.mean(numbers(group,'pm10'))})
        for city,data in sorted(bycity.items()):
            aq=numbers(data,'us_aqi');pm=numbers(data,'pm2_5')
            city_stats.append({'profile':profile,'city':city,'sample_count':len(data),'avg_aqi':statistics.mean(aq),'sd_aqi':statistics.stdev(aq),'min_aqi':min(aq),'median_aqi':statistics.median(aq),'max_aqi':max(aq),'avg_pm2_5':statistics.mean(pm),'avg_pm10':statistics.mean(numbers(data,'pm10')),'avg_temp':statistics.mean(numbers(data,'temperature_2m')),'avg_humidity':statistics.mean(numbers(data,'relative_humidity_2m')),'aqi_alert_count':sum(v>=100 for v in aq),'pm25_alert_count':sum(v>=35.5 for v in pm),'combined_alert_count':sum(float(r['us_aqi'])>=100 or float(r['pm2_5'])>=35.5 for r in data)})
            for field in FIELDS:
                values=numbers(data,field);q1,median,q3,p95=np.quantile(values,[.25,.5,.75,.95],method='linear')
                distribution.append({'profile':profile,'city':city,'variable':field,'n':len(values),'mean':statistics.mean(values),'sd':statistics.stdev(values) if len(values)>1 else None,'min':min(values),'q1':float(q1),'median':float(median),'q3':float(q3),'p95':float(p95),'max':max(values),'iqr':float(q3-q1)})
            counts=Counter(r['aqi_category'] for r in data)
            for label,count in sorted(counts.items()):categories.append({'profile':profile,'city':city,'aqi_category':label,'sample_count':count,'fraction':count/len(data)})
            for condition,rule in [('AQI >= 100',lambda r:float(r['us_aqi'])>=100),('PM2.5 >= 35.5',lambda r:float(r['pm2_5'])>=35.5),('AQI OR PM2.5',lambda r:float(r['us_aqi'])>=100 or float(r['pm2_5'])>=35.5)]:
                count=sum(rule(r) for r in data);thresholds.append({'profile':profile,'city':city,'condition':condition,'sample_count':len(data),'exceedance_count':count,'fraction':count/len(data)})
            days=defaultdict(list)
            for row in data:days[(instant(row['timestamp_utc'])+timedelta(hours=7)).date()].append(row)
            for day,group in sorted(days.items()):day_rows.append({'profile':profile,'city':city,'day_of_week2':(day-datetime(2026,10,12).date()).days+1,'sample_count':len(group),'avg_aqi':statistics.mean(numbers(group,'us_aqi')),'avg_pm2_5':statistics.mean(numbers(group,'pm2_5'))})
            for field in ['temperature_2m','relative_humidity_2m','wind_speed_10m']:
                x=numbers(data,field);y=numbers(data,'pm2_5')
                corr.append({'profile':profile,'city':city,'variable':field,'sample_count':len(x),'pearson_r':correlation(x,y),'spearman_r':correlation(ranks(x),ranks(y))})
        # Independent raw calculation versus fresh Athena summaries.
        sqlcity=read_csv(source/profile/'city_week2.csv')
        for sqlrow in sqlcity:
            local=next(r for r in city_stats if r['profile']==profile and r['city']==sqlrow['city'])
            for field,value in sqlrow.items():
                if field=='city':continue
                assert math.isclose(float(value),float(local[field]),rel_tol=1e-10,abs_tol=1e-8),(profile,field)
        sqlcorr=read_csv(source/profile/'correlation_week2.csv')
        for sqlrow in sqlcorr:
            for column,variable in [('corr_temp_pm25','temperature_2m'),('corr_humidity_pm25','relative_humidity_2m'),('corr_wind_pm25','wind_speed_10m')]:
                local=next(r for r in corr if r['profile']==profile and r['city']==sqlrow['city'] and r['variable']==variable)
                assert math.isclose(float(sqlrow[column]),local['pearson_r'],abs_tol=1e-10)
        for point in json.loads((private/profile/'operational_metrics.json').read_text(encoding='utf-8')):
            timestamp=instant(point['timestamp'])
            operational.append({'profile':profile,**point,'timestamp':timestamp.isoformat(),'scope':'week2' if START<=timestamp<END else 'earlier'})
        for entry in json.loads((private/profile/'lambda_runtime_reports.json').read_text(encoding='utf-8')):
            timestamp=datetime.fromtimestamp(entry['timestamp_ms']/1000,tz=timezone.utc)
            runtime.append({'profile':profile,'timestamp_utc':timestamp.isoformat(),'scope':'week2' if START<=timestamp<END else 'earlier','duration_ms':entry.get('Duration'),'billed_duration_ms':entry.get('Billed Duration'),'configured_memory_mb':entry.get('Memory Size'),'max_memory_used_mb':entry.get('Max Memory Used'),'init_duration_ms':entry.get('Init Duration')})
        for query in json.loads((private/profile/'project_query_history.json').read_text(encoding='utf-8')):
            timestamp=instant(query['Status']['SubmissionDateTime']);stat=query.get('Statistics',{})
            histories.append({'profile':profile,'query_id':query['QueryExecutionId'],'statement_type':query.get('StatementType'),'state':query['Status']['State'],'submitted_at_utc':timestamp.isoformat(),'scope':'week2' if START<=timestamp<END else 'earlier','engine_time_ms':stat.get('EngineExecutionTimeInMillis'),'bytes_scanned':stat.get('DataScannedInBytes'),'error_category':query['Status'].get('AthenaError',{}).get('ErrorCategory'),'error_type':query['Status'].get('AthenaError',{}).get('ErrorType')})
        for daily in json.loads((private/profile/'cost_daily.json').read_text(encoding='utf-8')).get('ResultsByTime',[]):
            for group in daily['Groups']:
                cost.append({'profile':profile,'day':daily['TimePeriod']['Start'],'service':group['Keys'][0],'unblended_cost_usd':float(group['Metrics']['UnblendedCost']['Amount']),'estimated':daily.get('Estimated',False),'scope':'week2' if daily['TimePeriod']['Start']>='2026-10-12' else 'earlier'})
        config=json.loads((private/profile/'lambda_configuration.json').read_text(encoding='utf-8'))
        rules=json.loads((private/profile/'eventbridge_rules.json').read_text(encoding='utf-8')).get('Rules',[])
        subs=json.loads((private/profile/'sns_subscriptions_weather-airquality-alerts.json').read_text(encoding='utf-8'))
        alarms=json.loads((private/profile/'cloudwatch_alarms.json').read_text(encoding='utf-8')).get('MetricAlarms',[])
        code=json.loads((private/profile/'deployed_code_identity.json').read_text(encoding='utf-8'))
        services.append({'profile':profile,'lambda_state':config['State'],'runtime':config['Runtime'],'memory_mb':config['MemorySize'],'timeout_s':config['Timeout'],'enabled_schedules':sum(r['State']=='ENABLED' for r in rules),'schedule_names':'; '.join(r['Name'] for r in rules),'confirmed_email_subscriptions':sum(s['Protocol']=='email' and s['SubscriptionArn'].startswith('arn:') for s in subs),'alarm_state':'; '.join(a['StateValue'] for a in alarms),'deployed_source_sha256':code['deployed_source_sha256'],'local_source_matches_deployed':code['local_matches_deployed']})
    weekly_comparison=[]
    for profile in PROFILES:
        earlier=[r for r in all_rows[profile] if datetime(2026,10,4,17,tzinfo=timezone.utc)<=instant(r['timestamp_utc'])<START]
        for city in sorted({r['city'] for r in earlier}):
            a=[r for r in earlier if r['city']==city];b=[r for r in weekly[profile] if r['city']==city]
            weekly_comparison.append({'profile':profile,'city':city,'week1_samples':len(a),'week2_samples':len(b),'week1_avg_aqi':statistics.mean(numbers(a,'us_aqi')),'week2_avg_aqi':statistics.mean(numbers(b,'us_aqi')),'week1_avg_pm25':statistics.mean(numbers(a,'pm2_5')),'week2_avg_pm25':statistics.mean(numbers(b,'pm2_5'))})
    paired=[]
    for city,bucket in sorted(set(hour_groups['default'])&set(hour_groups['quyen'])):
        a=hour_groups['default'][(city,bucket)];b=hour_groups['quyen'][(city,bucket)]
        pair={'city':city,'timestamp_utc':bucket.isoformat(),'son_samples':len(a),'quyen_samples':len(b)}
        for key in ['us_aqi','pm2_5','pm10','temperature_2m','relative_humidity_2m']:
            av=statistics.mean(numbers(a,key));bv=statistics.mean(numbers(b,key))
            pair.update({f'son_{key}':av,f'quyen_{key}':bv,f'delta_{key}':bv-av})
        paired.append(pair)
    common_exact=set((r['city'],r['timestamp_utc']) for r in all_rows['default'])&set((r['city'],r['timestamp_utc']) for r in all_rows['quyen'])
    overlap=[]
    for city,timestamp in sorted(common_exact):
        a=next(r for r in all_rows['default'] if r['city']==city and r['timestamp_utc']==timestamp);b=next(r for r in all_rows['quyen'] if r['city']==city and r['timestamp_utc']==timestamp)
        mismatches=[key for key in FIELDS if float(a[key])!=float(b[key])]
        overlap.append({'city':city,'timestamp_utc':timestamp,'sensor_values_match':not mismatches,'different_fields':';'.join(mismatches)})
    operational_summary=[]
    for profile in PROFILES:
        subset=[m for m in operational if m['profile']==profile and m['scope']=='week2']
        summary={'profile':profile}
        for metric in ['Invocations','Errors','Throttles','NumberOfMessagesPublished','NumberOfNotificationsDelivered','NumberOfNotificationsFailed']:
            points=[m for m in subset if m['metric']==metric]
            summary[metric]=sum(m['value'] for m in points) if points else None
            summary[metric+'_points']=len(points)
        summary['error_rate_valid']=summary['Errors'] is not None and summary['Invocations'] is not None and summary['Errors']<=summary['Invocations']
        summary['error_rate']=summary['Errors']/summary['Invocations'] if summary['error_rate_valid'] and summary['Invocations'] else None
        logs=[r for r in runtime if r['profile']==profile and r['scope']=='week2']
        summary['runtime_log_count']=len(logs)
        for variable in ['duration_ms','billed_duration_ms','max_memory_used_mb']:
            values=[float(r[variable]) for r in logs if r[variable] is not None]
            summary[variable+'_mean']=statistics.mean(values) if values else None;summary[variable+'_p95']=float(np.quantile(values,.95)) if values else None;summary[variable+'_max']=max(values) if values else None
        operational_summary.append(summary)
    query_metrics=[]
    for profile in PROFILES:
        for row in read_csv(source/profile/'query_metrics.csv'):
            query_metrics.append({**row,'row_count':int(row['row_count']),'execution_time_ms':int(row['execution_time_ms']),'bytes_scanned':int(row['bytes_scanned'])})
    scan=[]
    for profile in PROFILES:
        a=next(r for r in query_metrics if r['profile']==profile and r['name']=='scan_week2_time_only');b=next(r for r in query_metrics if r['profile']==profile and r['name']=='scan_week2_partition')
        counta=int(read_csv(source/profile/'scan_week2_time_only.csv')[0]['sample_count']);countb=int(read_csv(source/profile/'scan_week2_partition.csv')[0]['sample_count'])
        assert counta==countb==len(weekly[profile])
        scan.append({'profile':profile,'matched_records':counta,'time_only_bytes':a['bytes_scanned'],'partition_filtered_bytes':b['bytes_scanned'],'scan_reduction_fraction':1-b['bytes_scanned']/a['bytes_scanned'],'time_only_ms':a['execution_time_ms'],'partition_filtered_ms':b['execution_time_ms']})
    datasets={'account_inventory':inventory,'data_quality':quality,'distribution_statistics':distribution,'city_statistics':city_stats,'hourly_city':hour_rows,'daily_city':day_rows,'category_distribution':categories,'threshold_exceedance':thresholds,'correlations':corr,'matched_account_hours':paired,'cross_account_overlap':overlap,'weekly_comparison':weekly_comparison,'service_status':services,'operational_metrics':operational,'operational_summary':operational_summary,'lambda_runtime':runtime,'query_history':histories,'query_metrics':query_metrics,'partition_scan_comparison':scan,'cost_by_service_day':cost,'object_inventory':objects}
    for name,data in datasets.items():write_csv(destination/f'{name}.csv',data)
    write_csv(destination/'duplicate_city_timestamp.csv',duplicate_rows,headers=['profile','city','timestamp_utc','record_count'])
    # Include all source records in a flat provenance table without modifying account originals.
    raw=[{'profile':profile,**row} for profile in PROFILES for row in weekly[profile]]
    write_csv(destination/'raw_week2_both_accounts.csv',raw)
    rawall=[{'profile':profile,**row} for profile in PROFILES for row in all_rows[profile]]
    write_csv(destination/'raw_all_both_accounts.csv',rawall)
    summary={'inventory':inventory,'city_statistics':city_stats,'operational_summary':operational_summary,'service_status':services,'scan_comparison':scan,'paired_city_hour_groups':len(paired),'exact_overlap_records':len(overlap),'conflicting_overlap_records':sum(not r['sensor_values_match'] for r in overlap),'week2_total_source_rows':len(raw),'sample_policy':'Accounts analyzed independently. Matched city/hour means compare equal time groups. Source rows are not pooled as independent observations.','week2_start_utc':START.isoformat(),'week2_end_exclusive_utc':END.isoformat(),'collected_at_utc':at.isoformat(),'credential_files_unchanged':True,'quantile_method':'linear interpolation, NumPy default; standard deviation uses n-1.'}
    json_save(destination/'analysis_summary.json',summary)
    json_save(destination/'analysis_manifest.json',{'source_mode':'Live S3 and Athena downloads','files':[{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(destination.glob('*.csv'))],'calculation_policy':summary['sample_policy'],'missing_values':'Null/nonfinite excluded per variable; numeric zeros retained and counted separately.','timezone':'Naive environmental timestamps are interpreted as UTC; AWS timezone-aware timestamps converted to UTC before filtering.','aws_mutations':'Only SELECT query result objects created; no infrastructure or credential changes.'})
    print(json.dumps({'status':'PASS','all_source_rows':len(rawall),'week2_rows':len(raw),'paired_city_hour_groups':len(paired),'exact_overlap_records':len(overlap),'conflicting_overlap_records':summary['conflicting_overlap_records'],'csv_count':len(list(destination.glob('*.csv')))},ensure_ascii=False))
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,default=ROOT/'results/week2_live');parser.add_argument('--evidence','--private',dest='evidence',type=Path,default=ROOT/'results/week2_evidence');parser.add_argument('--output',type=Path,default=ROOT/'results/week2_analysis');args=parser.parse_args();analyze(args.source,args.evidence,args.output)
