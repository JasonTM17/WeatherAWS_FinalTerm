"""Reconcile native counters, API dimensions and lifecycle logs without invoking Lambda."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re

from common import FUNCTION, PROFILES, client, digest, session, write_csv, write_json
from dashboard import DASHBOARD, ERROR_RATE, build_dashboard, metric_consistency, reconcile_periods

FIELDS=['namespace','metric','statistic','timestamp_utc','value','unit']
NAMES=('Invocations','Errors','Throttles')


def timestamp(value):
    if isinstance(value,str): value=datetime.fromisoformat(value)
    if value.tzinfo is None: raise ValueError('Explicit timezone required')
    return value.astimezone(timezone.utc)


def statistics(cw,start,end,period=300,resource=False):
    dims=[{'Name':'FunctionName','Value':FUNCTION}]
    if resource: dims.append({'Name':'Resource','Value':FUNCTION})
    rows=[]
    for name in NAMES:
        points=cw.get_metric_statistics(Namespace='AWS/Lambda',MetricName=name,Dimensions=dims,
            StartTime=start,EndTime=end,Period=period,Statistics=['Sum']).get('Datapoints',[])
        rows.extend({'namespace':'AWS/Lambda','metric':name,'statistic':'Sum','timestamp_utc':timestamp(p['Timestamp']).isoformat(),
                     'value':p['Sum'],'unit':p['Unit']} for p in sorted(points,key=lambda p:p['Timestamp']))
    return rows


def metric_data(cw,start,end):
    queries=[{'Id':f'm{i}','MetricStat':{'Metric':{'Namespace':'AWS/Lambda','MetricName':name,
        'Dimensions':[{'Name':'FunctionName','Value':FUNCTION}]},'Period':300,'Stat':'Sum'},'ReturnData':True} for i,name in enumerate(NAMES)]
    rows=[];token=None;seen=set()
    while True:
        args={'MetricDataQueries':queries,'StartTime':start,'EndTime':end,'ScanBy':'TimestampAscending'}
        if token: args['NextToken']=token
        result=cw.get_metric_data(**args)
        for series in result['MetricDataResults']:
            if series['StatusCode']!='Complete' or len(series['Timestamps'])!=len(series['Values']):
                raise ValueError('MetricData series incomplete')
            name=NAMES[int(series['Id'][1:])]
            for t,v in zip(series['Timestamps'],series['Values']):
                key=(name,timestamp(t).isoformat())
                if key in seen: raise ValueError('Repeated metric point across pages')
                seen.add(key)
                rows.append({'namespace':'AWS/Lambda','metric':name,'statistic':'Sum','timestamp_utc':key[1],'value':v,'unit':'Count'})
        token=result.get('NextToken')
        if not token: break
    return rows


def point_map(rows):
    return {(r['metric'],r['timestamp_utc']):float(r['value']) for r in rows}


def classify_logs(events,start,end):
    """Retain typed, hashed lifecycle evidence, never raw application messages."""
    seen=set();rows=[];ids={kind:set() for kind in ('START','END','REPORT')}
    summary={'events_in_window':0,'result_lines':0,'complete_results':0,'partial_results':0,'error_lines':0,'malformed_results':0}
    for event in events:
        if event['eventId'] in seen: continue
        seen.add(event['eventId'])
        t=datetime.fromtimestamp(event['timestamp']/1000,timezone.utc)
        if not start<=t<end: continue
        summary['events_in_window']+=1
        message=event['message'];kind=None;request='';status='';records='';alerts=''
        match=re.match(r'^(START|END|REPORT) RequestId:\s*([\w-]+)',message)
        if match:
            kind=match[1];request=digest(match[2].encode())[:20];ids[kind].add(request)
            if kind=='REPORT':
                status='explicit_error' if re.search(r'Status:\s*(error|timeout)\b|Error Type:',message) else 'report_present'
        elif '[INFO] Result: ' in message:
            kind='RESULT';summary['result_lines']+=1
            try:
                result=json.loads(message.split('[INFO] Result: ',1)[1])
                status=result['collection_status']
                if status not in ('complete','partial','failed'): raise ValueError('Unknown status')
                records=int(result['records_collected']);alerts=int(result['alerts_sent'])
            except (KeyError,TypeError,ValueError):
                status='malformed';summary['malformed_results']+=1
            else:
                summary['complete_results']+=status=='complete'
                summary['partial_results']+=status=='partial'
        elif '[ERROR]' in message:
            kind='ERROR_LINE';summary['error_lines']+=1
        elif message.startswith('INIT_REPORT') and re.search(r'Status:\s*(error|timeout)\b',message):
            kind='INIT_ERROR'
        if kind:
            rows.append({'timestamp_utc':t.isoformat(),'event_hash':digest(event['eventId'].encode())[:20],
                'stream_hash':digest(event['logStreamName'].encode())[:20],'kind':kind,'request_hash':request,
                'status':status,'reported_records':records,'alerts_sent':alerts})
    summary.update({'unique_start_requests':len(ids['START']),'unique_end_requests':len(ids['END']),
        'unique_report_requests':len(ids['REPORT']),'matched_start_end_report':len(ids['START']&ids['END']&ids['REPORT']),
        'explicit_error_reports':sum(r['status']=='explicit_error' for r in rows),'init_error_lines':sum(r['kind']=='INIT_ERROR' for r in rows),
        'semantics':'Unique lifecycle request hashes and matching Result lines are distinct observations; no native error-rate inference from absent log lines'})
    return sorted(rows,key=lambda r:(r['timestamp_utc'],r['kind'])),summary


def update_dashboard(cw,topic,folder,backup,start,end):
    folder.mkdir(parents=True,exist_ok=True)
    before=json.loads(cw.get_dashboard(DashboardName=DASHBOARD)['DashboardBody'])
    if 'Source: tuan_3/scripts/dashboard.py' not in before['widgets'][0]['properties'].get('markdown',''):
        raise ValueError('Dashboard ownership marker differs; no overwrite')
    write_json(backup/'dashboard-before.json',{'name':DASHBOARD,'body':before})
    body=build_dashboard(topic)
    response=cw.put_dashboard(DashboardName=DASHBOARD,DashboardBody=json.dumps(body))
    try:
        if response.get('DashboardValidationMessages'): raise ValueError('Dashboard validation failed')
        if json.loads(cw.get_dashboard(DashboardName=DASHBOARD)['DashboardBody'])!=body:
            raise ValueError('Dashboard readback differs')
    except Exception:
        cw.put_dashboard(DashboardName=DASHBOARD,DashboardBody=json.dumps(before))
        raise
    write_json(folder/'dashboard.json',body)
    images=[]
    for index in (1,3,7):
        props=dict(body['widgets'][index]['properties'])
        props.update({'start':start.isoformat(),'end':end.isoformat(),'width':1200,'height':550})
        blob=cw.get_metric_widget_image(MetricWidget=json.dumps(props),OutputFormat='png')['MetricWidgetImage']
        if not blob.startswith(b'\x89PNG\r\n\x1a\n'): raise ValueError('Invalid widget PNG')
        (folder/f'cloudwatch_{index:02d}.png').write_bytes(blob)
        images.append({'widget':index,'bytes':len(blob)})
    return {'dashboard':DASHBOARD,'readback_matches':True,'images':images,'period_seconds':300,
        'semantics':'Native AWS widget images, not console screenshots; diagnostic gaps remain visible'}


def check_metric_math(cw,start,end):
    """Read-only expression tests over real input points, not injected metrics/events."""
    cases=[('missing_errors','raw_inv','IF(HOUR(raw_inv)==8,raw_inv*0)'),
           ('errors_above_invocations','raw_inv','raw_inv*2'),
           ('missing_invocations','IF(HOUR(raw_inv)==8,raw_inv)','raw_inv*0'),
           ('zero_invocations','raw_inv*0','raw_inv*0'),
           ('valid_zero_errors','raw_inv','raw_inv*0'),
           ('valid_half_errors','raw_inv*2','raw_inv')]
    queries=[{'Id':'raw_inv','MetricStat':{'Metric':{'Namespace':'AWS/Lambda','MetricName':'Invocations',
        'Dimensions':[{'Name':'FunctionName','Value':FUNCTION}]},'Period':300,'Stat':'Sum'},'ReturnData':True}]
    previous='IF(inv>0,IF(FILL(err,-1)>=0,IF(err<=inv,100*err/inv)))'
    for i,(_,inv,err) in enumerate(cases):
        queries.extend([{'Id':f'i{i}','Expression':inv,'Period':300,'ReturnData':False},
                        {'Id':f'e{i}','Expression':err,'Period':300,'ReturnData':False}])
        for prefix,formula in (('old',previous),('new',ERROR_RATE)):
            queries.append({'Id':f'{prefix}{i}','Expression':formula.replace('inv',f'i{i}').replace('err',f'e{i}'),
                            'Period':300,'ReturnData':True})
    response=cw.get_metric_data(MetricDataQueries=queries,StartTime=start,EndTime=end,ScanBy='TimestampAscending')
    if response.get('NextToken') or any(r['StatusCode']!='Complete' for r in response['MetricDataResults']):
        raise ValueError('Metric-math verification response incomplete')
    results={r['Id']:{timestamp(t).isoformat():float(v) for t,v in zip(r['Timestamps'],r['Values'])} for r in response['MetricDataResults']}
    inputs=results['raw_inv']
    if not inputs or not any(timestamp(t).hour==8 for t in inputs) or not any(timestamp(t).hour!=8 for t in inputs):
        raise ValueError('Verification window needs both selected and excluded native input periods')
    checks=[]
    for i,(name,_,_) in enumerate(cases):
        if name in ('missing_errors','missing_invocations'):
            expected={t:0.0 for t in inputs if timestamp(t).hour==8}
        elif name in ('errors_above_invocations','zero_invocations'): expected={}
        elif name=='valid_zero_errors': expected={t:0.0 for t in inputs}
        else: expected={t:50.0 for t in inputs}
        actual=results[f'new{i}']
        if actual!=expected: raise ValueError('Repaired metric-math expression failed a missing/invalid/valid case')
        checks.append({'case':name,'previous_output':results[f'old{i}'],'repaired_output':actual,'expected':expected,'status':'PASS'})
    return {'operation':'GetMetricData expression evaluation only','native_input_points':inputs,'checks':checks,
        'status':'PASS','synthetic_metrics_or_events_written':False,
        'semantics':'Transformed series are verification inputs, not native observation counters or pipeline evidence',
        'reference':'https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/using-metric-math.html'}


def run(profile,output,backup,start,end,apply):
    folder=output/profile;folder.mkdir(parents=True,exist_ok=False)
    sess=session(profile);cw=client(sess,'cloudwatch')
    config=client(sess,'lambda').get_function_configuration(FunctionName=FUNCTION)
    if config['FunctionArn'].split(':')[4]!=client(sess,'sts').get_caller_identity()['Account']:
        raise ValueError('Lambda identity does not match session')
    native=statistics(cw,start,end)
    data=metric_data(cw,start,end)
    resource=statistics(cw,start,end,resource=True)
    minute=statistics(cw,start,end,period=60)
    if point_map(native)!=point_map(data): raise ValueError('The two metric APIs disagree')
    aligned=reconcile_periods(native)
    for filename,rows in (('native_statistics.csv',native),('native_data.csv',data),('resource_statistics.csv',resource),('minute_statistics.csv',minute)):
        write_csv(folder/filename,rows,FIELDS)
    write_csv(folder/'period_reconciliation.csv',aligned['periods'],['timestamp_utc','invocations','errors','status','error_rate_percent'])
    events=[]
    logs=client(sess,'logs')
    for page in logs.get_paginator('filter_log_events').paginate(logGroupName=f'/aws/lambda/{FUNCTION}',startTime=int(start.timestamp()*1000),endTime=int(end.timestamp()*1000)):
        events.extend(page.get('events',[]))
    lifecycle,log_summary=classify_logs(events,start,end)
    write_csv(folder/'log_lifecycle.csv',lifecycle,['timestamp_utc','event_hash','stream_hash','kind','request_hash','status','reported_records','alerts_sent'])
    catalog=[{'metric':m['MetricName'],'dimensions':m['Dimensions']} for page in cw.get_paginator('list_metrics').paginate(Namespace='AWS/Lambda',Dimensions=[{'Name':'FunctionName','Value':FUNCTION}]) for m in page.get('Metrics',[])]
    write_json(folder/'metric_catalog.json',catalog)
    dashboard=None
    if apply:
        topic=config['Environment']['Variables']['SNS_TOPIC_ARN'].split(':')[-1]
        dashboard=update_dashboard(cw,topic,folder,backup/profile,start,end)
    result={'student':PROFILES[profile],'captured_at_utc':datetime.now(timezone.utc).isoformat(),'window_start_utc':start.isoformat(),
        'window_end_exclusive_utc':end.isoformat(),'namespace':'AWS/Lambda','function':FUNCTION,'statistic':'Sum','period_seconds':300,
        'api_parity':True,'resource_dimension_same_points':point_map(resource)==point_map(native),
        'minute_totals':{name:sum(float(r['value']) for r in minute if r['metric']==name) for name in NAMES},
        'native_summary':metric_consistency(native),'period_reconciliation':aligned,'log_summary':log_summary,'dashboard_update':dashboard,
        'lambda_state':config['State'],'lambda_last_update_status':config['LastUpdateStatus'],
        'lambda_invoked':False,'synthetic_events_injected':False,'lambda_code_or_configuration_changed':False}
    write_json(folder/'summary.json',result)
    print(json.dumps({'profile':profile,'native':result['native_summary'],'paired_periods':aligned['valid_periods'],
        'unpaired_periods':aligned['unpaired_periods'],'log_lifecycle':log_summary['matched_start_end_report'],'dashboard_applied':apply}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--start',type=timestamp)
    parser.add_argument('--end',type=timestamp)
    parser.add_argument('--apply-dashboard',action='store_true')
    parser.add_argument('--backup',type=Path)
    args=parser.parse_args()
    end=args.end or datetime.now(timezone.utc).replace(second=0,microsecond=0)
    if args.end is None: end-=timedelta(minutes=end.minute%5)
    start=args.start or end-timedelta(hours=3)
    if start>=end or any(t.second or t.microsecond or t.minute%5 for t in (start,end)):
        parser.error('Window must have aligned five-minute boundaries and positive duration')
    if args.output.exists() or args.apply_dashboard and (args.backup is None or args.backup.exists()):
        parser.error('Use new output and private backup folders')
    for profile in PROFILES:
        run(profile,args.output,args.backup,start,end,args.apply_dashboard)
    write_json(args.output/'manifest.json',{'files':[{'path':p.relative_to(args.output).as_posix(),'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size}
        for p in sorted(args.output.rglob('*')) if p.is_file()]})
