"""Create the isolated stack from an immutable artifact; private journal, disabled rule."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
import uuid

from botocore.config import Config
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tuan_3/scripts'))
from common import client, digest, session, write_json
from prepare_stack import build

ENVIRONMENTS = {'default': 'son', 'quyen': 'quyen'}
PROJECT = 'WeatherAWS_FinalTerm'


def error_code(error):
    return getattr(error, 'response', {}).get('Error', {}).get('Code', type(error).__name__)


def output_path(path):
    path = Path(path).resolve()
    if not path.is_relative_to((ROOT/'output').resolve()):
        raise ValueError('Deployment journal must remain in ignored output')
    return path


def owned_stack(stack, environment):
    tags = {t['Key']: t['Value'] for t in stack.get('Tags', [])}
    if tags.get('Project') != PROJECT or tags.get('Environment') != environment:
        raise ValueError('Existing stack is outside this deployment ownership')


def ensure_names_absent(sess, account, environment, template):
    """Refuse adoption/overwrite of deterministic resources outside a stack."""
    replacements={'EnvironmentName':environment,'AWS::AccountId':account,'AWS::Region':'us-east-1'}
    def name(resource, key):
        value=template['Resources'][resource]['Properties'][key]
        if isinstance(value,dict):value=value['Fn::Sub']
        for token,replacement in replacements.items():value=value.replace('${'+token+'}',replacement)
        if '${' in value:raise ValueError('Unresolved physical resource name')
        return value
    def absent(label, operation, missing):
        try:operation()
        except ClientError as error:
            if error_code(error) in missing:return
            raise
        raise ValueError('Existing physical resource: '+label)
    cloudwatch=client(sess,'cloudwatch')
    absent('dashboard',lambda:cloudwatch.get_dashboard(DashboardName=name('Dashboard','DashboardName')),
           {'ResourceNotFound'})
    topic=name('AlertTopic','TopicName')
    absent('topic',lambda:client(sess,'sns').get_topic_attributes(TopicArn=f'arn:aws:sns:us-east-1:{account}:{topic}'),
           {'NotFound','NotFoundException'})
    alarms=cloudwatch.describe_alarms(AlarmNames=[name('ErrorsAlarm','AlarmName')])
    if alarms.get('MetricAlarms') or alarms.get('CompositeAlarms'):raise ValueError('Existing physical resource: alarm')
    absent('raw bucket',lambda:client(sess,'s3').head_bucket(Bucket=name('DataBucket','BucketName'),ExpectedBucketOwner=account),
           {'404','NoSuchBucket','NotFound'})
    absent('collector',lambda:client(sess,'lambda').get_function_configuration(FunctionName=name('Collector','FunctionName')),
           {'ResourceNotFoundException'})
    absent('rule',lambda:client(sess,'events').describe_rule(Name=name('HourlyRule','Name'),EventBusName='default'),
           {'ResourceNotFoundException'})
    absent('database',lambda:client(sess,'glue').get_database(Name=template['Resources']['Database']['Properties']['DatabaseInput']['Name']['Fn::Sub'].replace('${EnvironmentName}',environment)),
           {'EntityNotFoundException'})
    logs=name('CollectorLogs','LogGroupName')
    for page in client(sess,'logs').get_paginator('describe_log_groups').paginate(logGroupNamePrefix=logs):
        if any(group['logGroupName']==logs for group in page.get('logGroups',[])):
            raise ValueError('Existing physical resource: log group')
    workgroup=name('QueryWorkgroup','Name')
    athena=client(sess,'athena')
    arguments={}
    while True:
        page=athena.list_work_groups(**arguments)
        if any(group['Name']==workgroup for group in page.get('WorkGroups',[])):
            raise ValueError('Existing physical resource: workgroup')
        token=page.get('NextToken')
        if not token:break
        arguments={'NextToken':token}
    # ApiConfig has no deterministic Name; its generated name cannot adopt an existing Secret.
    if 'Name' in template['Resources']['ApiConfig']['Properties']:
        absent('secret',lambda:client(sess,'secretsmanager').describe_secret(SecretId=name('ApiConfig','Name')),
               {'ResourceNotFoundException'})
    return {'status':'PASS','deterministic_names_checked':9}


def confirmed_email(sess, topic):
    endpoints = set()
    for page in client(sess, 'sns').get_paginator('list_subscriptions_by_topic').paginate(TopicArn=topic):
        for item in page['Subscriptions']:
            if item['Protocol'] == 'email' and item['SubscriptionArn'].startswith('arn:'):
                endpoints.add(item['Endpoint'])
    if len(endpoints) != 1:
        raise ValueError('Expected one existing confirmed recipient; do not guess an address')
    return endpoints.pop()


def artifact(sess, account, environment, folder, proof):
    s3 = client(sess, 's3')
    bucket = f'weather-w4-artifacts-{account}-us-east-1'
    created = False
    try:
        s3.head_bucket(Bucket=bucket, ExpectedBucketOwner=account)
    except ClientError as error:
        if error_code(error) not in ('404', 'NoSuchBucket', 'NotFound'):
            raise
        s3.create_bucket(Bucket=bucket, ObjectOwnership='BucketOwnerEnforced')
        created = True
    if not created:
        tags = {t['Key']: t['Value'] for t in s3.get_bucket_tagging(Bucket=bucket)['TagSet']}
        if tags.get('Project') != PROJECT or tags.get('Purpose') != 'week4-artifact':
            raise ValueError('Refuse to modify an unrelated existing artifact bucket')
        location = s3.get_bucket_location(Bucket=bucket)['LocationConstraint']
        if location not in (None, 'us-east-1'):
            raise ValueError('Artifact bucket region differs')
    if created:
        s3.put_bucket_tagging(Bucket=bucket, Tagging={'TagSet':[
            {'Key':'Project','Value':PROJECT},{'Key':'Purpose','Value':'week4-artifact'},
            {'Key':'Environment','Value':environment}]})
        s3.put_public_access_block(Bucket=bucket,PublicAccessBlockConfiguration={
            k:True for k in ('BlockPublicAcls','IgnorePublicAcls','BlockPublicPolicy','RestrictPublicBuckets')})
        s3.put_bucket_encryption(Bucket=bucket,ServerSideEncryptionConfiguration={
            'Rules':[{'ApplyServerSideEncryptionByDefault':{'SSEAlgorithm':'AES256'}}]})
        s3.put_bucket_versioning(Bucket=bucket,VersioningConfiguration={'Status':'Enabled'})
        s3.put_bucket_policy(Bucket=bucket,Policy=json.dumps({'Version':'2012-10-17','Statement':[{
            'Effect':'Deny','Principal':'*','Action':'s3:*',
            'Resource':[f'arn:aws:s3:::{bucket}',f'arn:aws:s3:::{bucket}/*'],
            'Condition':{'Bool':{'aws:SecureTransport':'false'}}}]}))
    controls=s3.get_public_access_block(Bucket=bucket)['PublicAccessBlockConfiguration']
    encryption=s3.get_bucket_encryption(Bucket=bucket)['ServerSideEncryptionConfiguration']['Rules']
    if (not all(controls.values()) or len(controls)!=4 or
        s3.get_bucket_versioning(Bucket=bucket).get('Status')!='Enabled' or
        encryption[0]['ApplyServerSideEncryptionByDefault']['SSEAlgorithm']!='AES256'):
        raise ValueError('Artifact bucket security/versioning differs')
    blob=(folder/'build'/'collector.zip').read_bytes()
    key=f"artifacts/week4/{proof['artifact_sha256']}/collector.zip"
    try:
        head=s3.head_object(Bucket=bucket,Key=key,ExpectedBucketOwner=account)
        version=head.get('VersionId')
    except ClientError as error:
        if error_code(error) not in ('404','NoSuchKey','NotFound'):raise
        put=s3.put_object(Bucket=bucket,Key=key,Body=blob,IfNoneMatch='*',ContentType='application/zip',
                          ServerSideEncryption='AES256',Metadata={'sha256':proof['artifact_sha256']})
        version=put.get('VersionId')
    if not version or version=='null':
        raise ValueError('Immutable artifact version missing')
    observed=s3.get_object(Bucket=bucket,Key=key,VersionId=version,ExpectedBucketOwner=account)['Body'].read()
    if observed!=blob or digest(observed)!=proof['artifact_sha256']:
        raise ValueError('Artifact readback differs')
    return bucket,key,version


def deploy(profile, output, apply=False, reuse_email=False):
    output=output_path(output)
    output.mkdir(parents=True,exist_ok=False)
    sess=session(profile)
    account=client(sess,'sts').get_caller_identity()['Account']
    environment=ENVIRONMENTS[profile]
    name=f'weather-w4-{environment}'
    cfg=client(sess,'lambda').get_function_configuration(FunctionName='WeatherCollectorLambda')
    role=f'arn:aws:iam::{account}:role/LabRole'
    if cfg['FunctionArn']!=f'arn:aws:lambda:us-east-1:{account}:function:WeatherCollectorLambda' or cfg['Role']!=role:
        raise ValueError('Canonical identity or role differs')
    cf=client(sess,'cloudformation')
    try:
        existing=cf.describe_stacks(StackName=name)['Stacks'][0]
    except ClientError as error:
        if error_code(error)!='ValidationError' or 'does not exist' not in error.response['Error'].get('Message',''):
            raise
        existing=None
    if existing:
        owned_stack(existing,environment)
        raise ValueError('Existing isolated stack found; inspect it instead of overwriting or invoking create again')
    proof=build(output/'build')
    template=(output/'build'/'weather-stack.json').read_text(encoding='utf-8')
    cf.validate_template(TemplateBody=template)
    names=ensure_names_absent(sess,account,environment,json.loads(template))
    write_json(output/'name_collision_check.json',names)
    if not apply:
        result={**proof,'status':'PREVIEW','profile':profile,'stack_name':name,'stack_created':False}
        write_json(output/'summary.json',result)
        return result
    bucket,key,version=artifact(sess,account,environment,output,proof)
    email=confirmed_email(sess,cfg['Environment']['Variables']['SNS_TOPIC_ARN']) if reuse_email else ''
    parameters={'EnvironmentName':environment,'LabRoleArn':role,'ArtifactBucket':bucket,
                'ArtifactKey':key,'ArtifactVersion':version,'AlertEmail':email}
    token='weather-w4-'+uuid.uuid4().hex
    # Journal precedes a single non-retried create; parameters/email never serialized.
    state={'status':'PREPARED','profile':profile,'stack_name':name,'client_token':token,
           'template_sha256':proof['template_sha256'],'artifact_sha256':proof['artifact_sha256'],
           'source_sha256':proof['source_sha256'],'artifact_version':version,
           'email_subscription_requested':bool(email),'created_at_utc':datetime.now(timezone.utc).isoformat()}
    write_json(output/'deployment.json',state)
    once=sess.client('cloudformation',config=Config(connect_timeout=10,read_timeout=45,retries={'total_max_attempts':1}))
    try:
        once.create_stack(StackName=name,TemplateBody=template,
            Parameters=[{'ParameterKey':k,'ParameterValue':v} for k,v in parameters.items()],
            Tags=[{'Key':'Project','Value':PROJECT},{'Key':'Environment','Value':environment}],
            ClientRequestToken=token,TimeoutInMinutes=20)
    except Exception as error:
        state.update(status='CREATE_REQUEST_NOT_CONFIRMED',error_code=error_code(error),retry_automatically=False)
        write_json(output/'deployment.json',state)
        raise RuntimeError('Inspect the named stack before another create request') from None
    last=None
    for _ in range(240):
        stack=cf.describe_stacks(StackName=name)['Stacks'][0]
        owned_stack(stack,environment)
        status=stack['StackStatus']
        if status!=last:
            print(json.dumps({'profile':profile,'stack_name':name,'stack_status':status}),flush=True)
            last=status
        if status not in ('CREATE_IN_PROGRESS','ROLLBACK_IN_PROGRESS','DELETE_IN_PROGRESS'):
            events=cf.describe_stack_events(StackName=name)['StackEvents']
            write_json(output/'events.json',[{'logical_id':e['LogicalResourceId'],
                'type':e['ResourceType'],'status':e['ResourceStatus'],
                'reason_hash':digest(e.get('ResourceStatusReason','').encode())} for e in events])
            result={**state,'status':'PASS' if status=='CREATE_COMPLETE' else 'FAIL',
                    'stack_status':status,'stack_created':status=='CREATE_COMPLETE',
                    'initial_schedule':'DISABLED','runtime_verified':False}
            write_json(output/'summary.json',result)
            if status=='CREATE_COMPLETE':
                write_json(output/'outputs.private.json',{o['OutputKey']:o['OutputValue'] for o in stack.get('Outputs',[])})
            return result
        time.sleep(5)
    state.update(status='WAIT_TIMEOUT',retry_automatically=False)
    write_json(output/'summary.json',state)
    return state


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',required=True,choices=tuple(ENVIRONMENTS))
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--reuse-confirmed-email',action='store_true')
    args=parser.parse_args()
    try:
        result=deploy(args.profile,args.output,args.apply,args.reuse_confirmed_email)
        print(json.dumps(result),flush=True)
        raise SystemExit(0 if result['status'] in ('PASS','PREVIEW') else 1)
    except Exception as error:
        print(json.dumps({'status':'BLOCKED_CAPABILITY' if error_code(error) in ('AccessDenied','AccessDeniedException') else 'FAIL',
                          'error_code':error_code(error),'inspect_private_output':True}),flush=True)
        raise SystemExit(1)
