"""Verify only resources from the isolated stack Outputs, with one explicit invocation."""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import sys
import time
import urllib.request
import uuid
import zipfile

from botocore.config import Config

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tuan_3/scripts'))
from common import client,digest,session,write_csv,write_json
from deploy_stack import ENVIRONMENTS,owned_stack,output_path,error_code
from run_demo_check import comparison,exact_query
from verify_environment import storage_check,verified_result


def validate_outputs(outputs,account,environment):
    expected={'DataBucket':f'weather-w4-{environment}-{account}-us-east-1',
        'FunctionName':f'weather-w4-{environment}-collector','RuleName':f'weather-w4-{environment}-hourly',
        'DatabaseName':f'weather_w4_{environment}','Workgroup':f'weather-w4-{environment}',
        'TopicArn':f'arn:aws:sns:us-east-1:{account}:weather-w4-{environment}-alerts',
        'DashboardName':f'WeatherAirQuality-Week4-{environment}'}
    if any(outputs.get(k)!=v for k,v in expected.items()):
        raise ValueError('Stack Outputs point outside the isolated application')
    if not outputs.get('SecretArn','').startswith(f'arn:aws:secretsmanager:us-east-1:{account}:secret:'):
        raise ValueError('Secret belongs to another environment')
    return expected


def query_records(sess,outputs,records,folder):
    sql=exact_query(records)
    (folder/'exact_records.sql').write_text(sql+';\n',encoding='utf-8')
    athena=client(sess,'athena')
    token=uuid.uuid4().hex
    write_json(folder/'query.pending.json',{'client_token':token,'database':outputs['DatabaseName'],'workgroup':outputs['Workgroup']})
    qid=athena.start_query_execution(QueryString=sql,ClientRequestToken=token,
        QueryExecutionContext={'Database':outputs['DatabaseName']},WorkGroup=outputs['Workgroup'],
        ResultReuseConfiguration={'ResultReuseByAgeConfiguration':{'Enabled':False}})['QueryExecutionId']
    deadline=time.monotonic()+180
    while True:
        execution=athena.get_query_execution(QueryExecutionId=qid)['QueryExecution']
        if execution['Status']['State'] in ('SUCCEEDED','FAILED','CANCELLED'):break
        if time.monotonic()>deadline:
            athena.stop_query_execution(QueryExecutionId=qid)
            raise TimeoutError('Stack SELECT timed out')
        time.sleep(1)
    if (execution['Status']['State']!='SUCCEEDED' or execution.get('WorkGroup')!=outputs['Workgroup'] or
        execution.get('QueryExecutionContext',{}).get('Database')!=outputs['DatabaseName']):
        raise ValueError('Query did not succeed in the exact stack database/workgroup')
    statistics=execution.get('Statistics',{})
    if statistics.get('ResultReuseInformation',{}).get('ReusedPreviousResult',False):
        raise ValueError('Cached result cannot prove the new invocation')
    rows=[];header=None
    for page in athena.get_paginator('get_query_results').paginate(QueryExecutionId=qid):
        result=page['ResultSet']
        if header is None:header=[column['Name'] for column in result['ResultSetMetadata']['ColumnInfo']]
        for item in result.get('Rows',[]):
            values=[cell.get('VarCharValue','') for cell in item['Data']]
            if not rows and values==header:continue
            rows.append(dict(zip(header,values+['']*(len(header)-len(values)))))
    actual={row['record_id']:row for row in rows};expected={row['record_id']:row for row in records}
    if len(rows)!=3 or set(actual)!=set(expected) or any(
        actual[k]['city']!=expected[k]['city'] or float(actual[k]['us_aqi'])!=float(expected[k]['us_aqi']) or
        float(actual[k]['pm2_5'])!=float(expected[k]['pm2_5']) for k in expected):
        raise ValueError('Stack SELECT differs from exact raw records')
    write_csv(folder/'athena_exact.csv',rows,header)
    proof={'status':'PASS','query_id':qid,'database':outputs['DatabaseName'],'workgroup':outputs['Workgroup'],
        'records':len(rows),'result_reused':False,'bytes_scanned':statistics.get('DataScannedInBytes',0),
        'engine_ms':statistics.get('EngineExecutionTimeInMillis',0),'total_ms':statistics.get('TotalExecutionTimeInMillis',0)}
    write_json(folder/'athena_exact.json',proof)
    (folder/'query.pending.json').unlink()
    return proof


def verify(profile,output,invoke=False):
    output=output_path(output);output.mkdir(parents=True,exist_ok=False)
    sess=session(profile);account=client(sess,'sts').get_caller_identity()['Account']
    environment=ENVIRONMENTS[profile]
    stack=client(sess,'cloudformation').describe_stacks(StackName=f'weather-w4-{environment}')['Stacks'][0]
    owned_stack(stack,environment)
    if stack['StackStatus']!='CREATE_COMPLETE':raise ValueError('Stack must be CREATE_COMPLETE')
    outputs={item['OutputKey']:item['OutputValue'] for item in stack['Outputs']}
    validate_outputs(outputs,account,environment)
    cfg=client(sess,'lambda').get_function_configuration(FunctionName=outputs['FunctionName'])
    if cfg['Role']!=f'arn:aws:iam::{account}:role/LabRole' or cfg['State']!='Active' or cfg.get('LastUpdateStatus')!='Successful':
        raise ValueError('Stack collector role/state differs')
    variables=cfg['Environment']['Variables']
    if (variables.get('S3_BUCKET_NAME')!=outputs['DataBucket'] or variables.get('SECRET_NAME')!=outputs['SecretArn'] or
        variables.get('SNS_TOPIC_ARN')!=outputs['TopicArn']):raise ValueError('Collector environment differs from stack Outputs')
    function=client(sess,'lambda').get_function(FunctionName=outputs['FunctionName'])
    with urllib.request.urlopen(function['Code']['Location'],timeout=30) as response:blob=response.read()
    if base64.b64encode(bytes.fromhex(digest(blob))).decode()!=cfg['CodeSha256']:raise ValueError('Code package hash mismatch')
    with zipfile.ZipFile(io.BytesIO(blob)) as package:
        source=package.read('lambda_function.py')
    local=(ROOT/'tuan_2/lambda/lambda_function.py').read_text(encoding='utf-8').replace('\r\n','\n').encode()
    if source!=local:raise ValueError('Stack source differs from canonical collector')
    events=client(sess,'events')
    rule=events.describe_rule(Name=outputs['RuleName'])
    targets=events.list_targets_by_rule(Rule=outputs['RuleName'])['Targets']
    if (rule['State']!='DISABLED' or rule['ScheduleExpression']!='rate(1 hour)' or len(targets)!=1 or targets[0]['Arn']!=cfg['FunctionArn']):
        raise ValueError('New schedule must remain disabled and target the isolated collector')
    storage=storage_check(sess,outputs['DataBucket'])
    if storage['status']!='PASS' or storage['versioning']!='Enabled':raise ValueError('New stack storage controls differ')
    table=client(sess,'glue').get_table(DatabaseName=outputs['DatabaseName'],Name='weather_airquality_records')['Table']
    workgroup=client(sess,'athena').get_work_group(WorkGroup=outputs['Workgroup'])['WorkGroup']
    if (table['Parameters'].get('projection.enabled')!='true' or len(table['StorageDescriptor']['Columns'])!=20 or
        len(table['PartitionKeys'])!=3 or not workgroup['Configuration'].get('EnforceWorkGroupConfiguration')):
        raise ValueError('Projection/schema or enforced workgroup differs')
    subscriptions=[]
    for page in client(sess,'sns').get_paginator('list_subscriptions_by_topic').paginate(TopicArn=outputs['TopicArn']):
        subscriptions.extend({'protocol':s['Protocol'],'confirmed':s['SubscriptionArn'].startswith('arn:')} for s in page['Subscriptions'])
    proof={'status':'PASS','profile':profile,'stack_name':f'weather-w4-{environment}',
        'captured_at_utc':datetime.now(timezone.utc).isoformat(),'stack_status':stack['StackStatus'],
        'function_name':outputs['FunctionName'],'database':outputs['DatabaseName'],'workgroup':outputs['Workgroup'],
        'artifact_sha256':digest(blob),'source_sha256':digest(source),'schedule_state':'DISABLED',
        'storage':storage,'projection_enabled':True,'schema_data_columns':20,'schema_partition_columns':3,
        'subscriptions':subscriptions,'invocation_executed':False}
    write_json(output/'configuration.json',proof)
    if not invoke:return proof
    settings=json.loads(client(sess,'secretsmanager').get_secret_value(SecretId=outputs['SecretArn'])['SecretString'])
    once=sess.client('lambda',config=Config(connect_timeout=10,read_timeout=90,retries={'total_max_attempts':1}))
    write_json(output/'invocation.json',{'status':'PREPARED','function_name':outputs['FunctionName'],'event':{}})
    try:response=once.invoke(FunctionName=outputs['FunctionName'],InvocationType='RequestResponse',Payload=b'{}')
    except Exception:
        write_json(output/'invocation.json',{'status':'UNKNOWN_ACKNOWLEDGEMENT','retry_automatically':False})
        raise RuntimeError('Inspect isolated collector logs before another invocation') from None
    if response.get('FunctionError') or response['StatusCode']!=200:raise ValueError('Stack collector execution failed')
    result=json.loads(response['Payload'].read())
    records,valid=verified_result(result,outputs['DataBucket'],client(sess,'s3'),output,{})
    verdict=comparison(records,result,settings)
    if not valid or verdict['status']!='PASS':raise ValueError('Stack records or SNS acceptance differs')
    write_csv(output/'raw_invocation.csv',records,list(records[0]))
    write_json(output/'invocation.json',{**verdict,'function_name':outputs['FunctionName'],
        'request_hash':digest(response['ResponseMetadata']['RequestId'].encode())[:20],
        'saved_files':result['saved_files'],'source_sha256':digest(source)})
    query=query_records(sess,outputs,records,output)
    if events.describe_rule(Name=outputs['RuleName'])['State']!='DISABLED':raise ValueError('Isolated schedule changed during verification')
    summary={**proof,'invocation_executed':True,'records':len(records),'alerts':verdict,'athena':query}
    write_json(output/'summary.json',summary)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',required=True,choices=tuple(ENVIRONMENTS))
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--invoke',action='store_true')
    args=parser.parse_args()
    try:print(json.dumps(verify(args.profile,args.output,args.invoke)),flush=True)
    except Exception as error:
        print(json.dumps({'status':'FAIL','error_code':error_code(error),'inspect_private_output':True}),flush=True)
        raise SystemExit(1)
