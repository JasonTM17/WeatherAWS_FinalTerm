"""Manage the WeatherAWS project through the Python AWS SDK."""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import re
import zipfile

import boto3
from botocore.exceptions import ClientError
from athena_export import AthenaExporter

ROOT = Path(__file__).resolve().parents[1]
TAGS = {'Project': 'WeatherAWS_FinalTerm', 'Owner': '24110054,24110051', 'Course': 'Cloud_FinalTerm'}
TAG_LIST = [{'Key': key, 'Value': value} for key, value in TAGS.items()]
FUNCTION = 'WeatherCollectorLambda'
RULE = 'WeatherCollectionSchedule'
TOPIC = 'weather-airquality-alerts'
SECRET = 'weather/api_config'
DATABASE = 'weather_aqi_db'
ALARM = 'WeatherCollector-Errors-Alarm'
DASHBOARD = 'WeatherAirQuality-Monitoring-Dashboard'
CONFIG = {
    'api_provider': 'open-meteo', 'aqi_threshold_pm25': 35.5,
    'aqi_threshold_pm10': 50.0, 'aqi_threshold_us_aqi': 100,
    'locations': [
        {'city': 'HoChiMinh', 'lat': 10.8231, 'lon': 106.6297},
        {'city': 'HaNoi', 'lat': 21.0285, 'lon': 105.8542},
        {'city': 'DaNang', 'lat': 16.0544, 'lon': 108.2022},
    ],
}


def missing(error):
    return isinstance(error, ClientError) and error.response['Error']['Code'] in (
        '404', 'NoSuchBucket', 'NoSuchKey', 'ResourceNotFoundException', 'EntityNotFoundException')


class AwsProject:
    def __init__(self, region='us-east-1', session=None):
        self.region = region
        self.session = session or boto3.Session(region_name=region)
        self.clients, self._identity = {}, None

    def client(self, service):
        if service not in self.clients:
            self.clients[service] = self.session.client(service, region_name=self.region)
        return self.clients[service]

    @property
    def identity(self):
        if self._identity is None:
            self._identity = self.client('sts').get_caller_identity()
        return self._identity

    @property
    def account(self):
        return self.identity['Account']

    @property
    def bucket(self):
        return f'weather-aqi-{self.account}'

    def arn(self, service, resource):
        partition = self.identity['Arn'].split(':')[1]
        return f'arn:{partition}:{service}:{self.region}:{self.account}:{resource}'

    def setup_s3(self):
        s3 = self.client('s3')
        try:
            s3.head_bucket(Bucket=self.bucket)
        except ClientError as error:
            if not missing(error):
                raise
            request = {'Bucket': self.bucket}
            if self.region != 'us-east-1':
                request['CreateBucketConfiguration'] = {'LocationConstraint': self.region}
            s3.create_bucket(**request)
        s3.put_public_access_block(Bucket=self.bucket, PublicAccessBlockConfiguration={
            'BlockPublicAcls': True, 'IgnorePublicAcls': True,
            'BlockPublicPolicy': True, 'RestrictPublicBuckets': True})
        s3.put_bucket_encryption(Bucket=self.bucket, ServerSideEncryptionConfiguration={
            'Rules': [{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}}]})
        s3.put_bucket_tagging(Bucket=self.bucket, Tagging={'TagSet': TAG_LIST})

    def setup_secrets(self):
        secrets = self.client('secretsmanager')
        try:
            secrets.describe_secret(SecretId=SECRET)
        except ClientError as error:
            if not missing(error):
                raise
            secrets.create_secret(Name=SECRET, SecretString=json.dumps(CONFIG), Tags=TAG_LIST)
        else:
            secrets.tag_resource(SecretId=SECRET, Tags=TAG_LIST)

    def setup_sns(self, email=None):
        sns = self.client('sns')
        topic = sns.create_topic(Name=TOPIC, Tags=TAG_LIST)['TopicArn']
        if email:
            existing = [subscription for page in sns.get_paginator('list_subscriptions_by_topic').paginate(TopicArn=topic)
                        for subscription in page.get('Subscriptions', [])]
            if not any(item.get('Endpoint') == email and item.get('Protocol') == 'email' for item in existing):
                sns.subscribe(TopicArn=topic, Protocol='email', Endpoint=email)
        return topic

    def deploy_lambda(self):
        client = self.client('lambda')
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.write(ROOT / 'lambda' / 'lambda_function.py', 'lambda_function.py')
        variables = {'S3_BUCKET_NAME': self.bucket, 'SECRET_NAME': SECRET,
                     'SNS_TOPIC_ARN': self.arn('sns', TOPIC)}
        try:
            old = client.get_function_configuration(FunctionName=FUNCTION)
        except ClientError as error:
            if not missing(error):
                raise
            partition = self.identity['Arn'].split(':')[1]
            client.create_function(FunctionName=FUNCTION, Runtime='python3.12',
                Role=f'arn:{partition}:iam::{self.account}:role/LabRole',
                Handler='lambda_function.lambda_handler', Code={'ZipFile': buffer.getvalue()},
                Timeout=60, MemorySize=256, Environment={'Variables': variables}, Tags=TAGS)
            client.get_waiter('function_active_v2').wait(FunctionName=FUNCTION)
        else:
            variables = {**old.get('Environment', {}).get('Variables', {}), **variables}
            client.update_function_code(FunctionName=FUNCTION, ZipFile=buffer.getvalue())
            client.get_waiter('function_updated_v2').wait(FunctionName=FUNCTION)
            client.update_function_configuration(FunctionName=FUNCTION, Timeout=60, MemorySize=256,
                                                 Environment={'Variables': variables})
            client.get_waiter('function_updated_v2').wait(FunctionName=FUNCTION)
            client.tag_resource(Resource=self.arn('lambda', f'function:{FUNCTION}'), Tags=TAGS)

    def setup_eventbridge(self, rate='rate(1 hour)'):
        events, lamb = self.client('events'), self.client('lambda')
        rule = events.put_rule(Name=RULE, ScheduleExpression=rate, State='ENABLED',
                               Description='Collect weather and air quality data each hour', Tags=TAG_LIST)['RuleArn']
        result = events.put_targets(Rule=RULE, Targets=[{'Id': '1', 'Arn': self.arn('lambda', f'function:{FUNCTION}')}])
        if result.get('FailedEntryCount', 0):
            raise RuntimeError('EventBridge could not attach the Lambda target.')
        statement = f'EventBridgeInvokePermission_{RULE}'
        try:
            policy = json.loads(lamb.get_policy(FunctionName=FUNCTION)['Policy'])
        except ClientError as error:
            if not missing(error):
                raise
            policy = {'Statement': []}
        matches = [item for item in policy.get('Statement', []) if item.get('Sid') == statement]
        if matches and matches[0].get('Condition', {}).get('ArnLike', {}).get('AWS:SourceArn') == rule:
            return
        if matches:
            lamb.remove_permission(FunctionName=FUNCTION, StatementId=statement)
        lamb.add_permission(FunctionName=FUNCTION, StatementId=statement,
                            Action='lambda:InvokeFunction', Principal='events.amazonaws.com', SourceArn=rule)

    def setup_catalog(self):
        glue = self.client('glue')
        try:
            glue.get_database(Name=DATABASE)
        except ClientError as error:
            if not missing(error):
                raise
            glue.create_database(DatabaseInput={'Name': DATABASE, 'Description': 'Weather and air quality data'})
        exporter = AthenaExporter(self.client('athena'), self.client('s3'), DATABASE,
                                  f's3://{self.bucket}/athena-results/')
        sql = (ROOT / 'athena' / 'create_table.sql').read_text(encoding='utf-8')
        sql = re.sub(r'weather-aqi-[\w-]+', self.bucket, sql)
        exporter.execute(sql)
        exporter.execute(f'MSCK REPAIR TABLE {DATABASE}.weather_airquality_records')
        try:
            table_type = glue.get_table(DatabaseName=DATABASE, Name='vietnam_weather_aqi')['Table'].get('TableType')
        except ClientError as error:
            if not missing(error):
                raise
            table_type = None
        if table_type in (None, 'VIRTUAL_VIEW'):
            exporter.execute((ROOT / 'athena' / 'create_view_vietnam_weather_aqi.sql').read_text(encoding='utf-8'))

    def setup_cloudwatch(self):
        cloudwatch = self.client('cloudwatch')
        cloudwatch.put_metric_alarm(AlarmName=ALARM, MetricName='Errors', Namespace='AWS/Lambda',
            Statistic='Sum', Period=300, Threshold=1, ComparisonOperator='GreaterThanOrEqualToThreshold',
            Dimensions=[{'Name': 'FunctionName', 'Value': FUNCTION}], EvaluationPeriods=1,
            TreatMissingData='notBreaching', AlarmActions=[self.arn('sns', TOPIC)], Tags=TAG_LIST)
        widgets = []
        for x, name, statistics in [(0, 'Invocations and errors', [('Invocations', 'Sum'), ('Errors', 'Sum')]),
                                     (12, 'Execution duration', [('Duration', 'Average'), ('Duration', 'Maximum')])]:
            widgets.append({'type': 'metric', 'x': x, 'y': 0, 'width': 12, 'height': 6,
                            'properties': {'region': self.region, 'title': name, 'period': 300,
                            'metrics': [['AWS/Lambda', metric, 'FunctionName', FUNCTION, {'stat': stat}]
                                        for metric, stat in statistics]}})
        result = cloudwatch.put_dashboard(DashboardName=DASHBOARD, DashboardBody=json.dumps({'widgets': widgets}))
        if result.get('DashboardValidationMessages'):
            raise RuntimeError('CloudWatch returned dashboard validation warnings.')

    def deploy(self, email=None, rate='rate(1 hour)'):
        for method in (self.setup_s3, self.setup_secrets):
            method()
        self.setup_sns(email)
        self.deploy_lambda()
        self.setup_eventbridge(rate)
        self.setup_catalog()
        self.setup_cloudwatch()

    def verify(self):
        configuration = self.client('lambda').get_function_configuration(FunctionName=FUNCTION)
        rule = self.client('events').describe_rule(Name=RULE)
        objects = sum(page.get('KeyCount', 0) for page in self.client('s3').get_paginator('list_objects_v2').paginate(
            Bucket=self.bucket, Prefix='raw/'))
        self.client('glue').get_table(DatabaseName=DATABASE, Name='weather_airquality_records')
        return {'account': self.account, 'region': self.region, 'lambda_state': configuration.get('State'),
                'schedule_state': rule.get('State'), 'raw_objects': objects, 'catalog_table': 'present'}

    def cleanup(self, confirm_account, delete_data=False):
        if confirm_account != self.account:
            raise ValueError('ConfirmAccount must match the authenticated account before any deletion.')
        if delete_data:
            tags = self.client('s3').get_bucket_tagging(Bucket=self.bucket)['TagSet']
            if not any(item == {'Key': 'Project', 'Value': TAGS['Project']} for item in tags):
                raise ValueError('Bucket project tag does not match; data deletion refused.')

        def remove(service, operation, **kwargs):
            try:
                return getattr(self.client(service), operation)(**kwargs)
            except ClientError as error:
                if not missing(error):
                    raise

        for rule in (RULE, 'WeatherCollectionHourlyRule'):
            targets = remove('events', 'list_targets_by_rule', Rule=rule)
            if targets and targets.get('Targets'):
                result = remove('events', 'remove_targets', Rule=rule, Ids=[item['Id'] for item in targets['Targets']])
                if result and result.get('FailedEntryCount', 0):
                    raise RuntimeError('Could not remove EventBridge targets.')
            remove('events', 'delete_rule', Name=rule)
        remove('cloudwatch', 'delete_dashboards', DashboardNames=[DASHBOARD])
        remove('cloudwatch', 'delete_alarms', AlarmNames=[ALARM])
        remove('lambda', 'delete_function', FunctionName=FUNCTION)
        remove('sns', 'delete_topic', TopicArn=self.arn('sns', TOPIC))
        for table in ('vietnam_weather_aqi', 'weather_airquality_records'):
            remove('glue', 'delete_table', DatabaseName=DATABASE, Name=table)
        remove('glue', 'delete_database', Name=DATABASE)
        remove('secretsmanager', 'delete_secret', SecretId=SECRET, RecoveryWindowInDays=7)
        remove('logs', 'delete_log_group', logGroupName=f'/aws/lambda/{FUNCTION}')
        if delete_data:
            s3 = self.client('s3')
            for page in s3.get_paginator('list_object_versions').paginate(Bucket=self.bucket):
                objects = [{'Key': item['Key'], 'VersionId': item['VersionId']}
                           for key in ('Versions', 'DeleteMarkers') for item in page.get(key, [])]
                for start in range(0, len(objects), 1000):
                    result = s3.delete_objects(Bucket=self.bucket, Delete={'Objects': objects[start:start+1000]})
                    if result.get('Errors'):
                        raise RuntimeError('Some S3 object versions could not be deleted.')
            s3.delete_bucket(Bucket=self.bucket)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['setup-s3', 'setup-secrets', 'setup-sns', 'deploy-lambda',
        'setup-eventbridge', 'setup-catalog', 'setup-cloudwatch', 'deploy', 'verify', 'cleanup'])
    parser.add_argument('--region', default='us-east-1')
    parser.add_argument('--email')
    parser.add_argument('--rate', default='rate(1 hour)')
    parser.add_argument('--confirm-account')
    parser.add_argument('--delete-data', action='store_true')
    args = parser.parse_args(argv)
    project = AwsProject(args.region)
    if args.action == 'deploy':
        project.deploy(args.email, args.rate)
    elif args.action == 'setup-sns':
        project.setup_sns(args.email)
    elif args.action == 'setup-eventbridge':
        project.setup_eventbridge(args.rate)
    elif args.action == 'cleanup':
        project.cleanup(args.confirm_account, args.delete_data)
    elif args.action == 'verify':
        print(json.dumps(project.verify(), indent=2))
    else:
        getattr(project, args.action.replace('-', '_'))()


if __name__ == '__main__':
    main()
