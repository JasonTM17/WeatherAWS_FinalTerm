"""Deploy an isolated live CloudWatch dashboard and save native AWS graphs."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

from botocore.exceptions import ClientError
from common import PROFILES, FUNCTION, client, session, write_csv, write_json

DASHBOARD = 'WeatherAirQuality-Week3'
ERROR_RATE = 'IF(inv>0,IF(FILL(err,-1)>=0,IF(err<=inv,100*err/inv)))'


def metric_consistency(rows):
    totals = {}
    for name in ('Invocations', 'Errors'):
        values = [float(r['value']) for r in rows if r['namespace'] == 'AWS/Lambda'
                  and r['metric'] == name and r['statistic'] == 'Sum']
        totals[name] = sum(values) if values else None
    invocations, errors = totals['Invocations'], totals['Errors']
    status, ratio = 'UNAVAILABLE', None
    if invocations is not None and errors is not None:
        if errors < 0 or invocations < 0 or errors > invocations:
            status = 'INCONSISTENT_COUNTS'
        elif invocations > 0:
            status, ratio = 'VALID', 100 * errors / invocations
    return {'lambda_sums': totals, 'error_rate_status': status, 'error_rate_percent': ratio,
            'limitation': 'Missing metrics are not zero; inconsistent counters cannot establish an error rate or root cause'}


def build_dashboard(topic, region='us-east-1'):
    def metric(name, stat='Sum', **options):
        return ['AWS/Lambda', name, 'FunctionName', FUNCTION, {'stat': stat, **options}]

    groups = [
        ('Lambda invocations / errors / throttles', [metric('Invocations'), metric('Errors'), metric('Throttles')]),
        ('Execution duration (ms)', [metric('Duration', 'Average'), metric('Duration', 'Maximum')]),
        ('Error rate (%) - requires present and consistent counters', [metric('Invocations', id='inv', visible=False), metric('Errors', id='err', visible=False), [{'expression': ERROR_RATE, 'id': 'rate', 'label': 'Errors / Invocations (%)'}]]),
        ('SNS published / delivered / failed', [['AWS/SNS', name, 'TopicName', topic, {'stat': 'Sum'}] for name in ('NumberOfMessagesPublished', 'NumberOfNotificationsDelivered', 'NumberOfNotificationsFailed')]),
        ('Canonical hourly rule', [['AWS/Events', name, 'RuleName', 'WeatherCollectionSchedule', {'stat': 'Sum'}] for name in ('TriggeredRules', 'Invocations', 'FailedInvocations')]),
        ('Matching collection log lines (not invocation counts)', [['WeatherAWS/Collection', name, {'stat': 'Sum'}] for name in ('ResultLogLines', 'ErrorLogLines')]),
    ]
    widgets = [{'type': 'text', 'x': 0, 'y': 0, 'width': 24, 'height': 2,
                'properties': {'markdown': '# WeatherAWS Week 3\nSource: tuan_3/scripts/dashboard.py. Metrics share 300s periods and the selected window. Missing points are not measured zero; delivery counts are not email-read confirmations.'}}]
    for i, (title, metrics) in enumerate(groups):
        widgets.append({'type': 'metric', 'x': (i % 2) * 12, 'y': 2 + (i // 2) * 6, 'width': 12, 'height': 6,
                        'properties': {'region': region, 'title': title, 'period': 300, 'stat': 'Sum', 'view': 'timeSeries', 'metrics': metrics}})
    return {'start': '-PT24H', 'periodOverride': 'inherit', 'widgets': widgets}


def run(profile, output, backup):
    sess = session(profile)
    config = client(sess, 'lambda').get_function_configuration(FunctionName=FUNCTION)
    topic = config['Environment']['Variables']['SNS_TOPIC_ARN'].split(':')[-1]
    cw = client(sess, 'cloudwatch')
    folder = output / profile
    folder.mkdir(parents=True, exist_ok=True)
    original = backup / profile / 'dashboard-before.json'
    if not original.exists():
        try:
            old = cw.get_dashboard(DashboardName=DASHBOARD)['DashboardBody']
        except ClientError as error:
            if error.response['Error']['Code'] not in ('ResourceNotFound', 'ResourceNotFoundException'):
                raise
            old = None
        write_json(original, {'name': DASHBOARD, 'previous_body': json.loads(old) if old else None})
    body = build_dashboard(topic)
    result = cw.put_dashboard(DashboardName=DASHBOARD, DashboardBody=json.dumps(body))
    if result.get('DashboardValidationMessages'):
        raise RuntimeError('CloudWatch dashboard validation messages; inspect before accepting')
    actual = json.loads(cw.get_dashboard(DashboardName=DASHBOARD)['DashboardBody'])
    if actual != body:
        raise ValueError('Saved dashboard body differs')
    write_json(folder / 'dashboard.json', body)
    start = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(hours=24)
    end = start + timedelta(hours=24)
    rows = []
    for namespace, dimension, name, metrics in [
        ('AWS/Lambda', 'FunctionName', FUNCTION, [('Invocations', 'Sum'), ('Errors', 'Sum'), ('Throttles', 'Sum'), ('Duration', 'Average')]),
        ('AWS/SNS', 'TopicName', topic, [(m, 'Sum') for m in ('NumberOfMessagesPublished', 'NumberOfNotificationsDelivered', 'NumberOfNotificationsFailed')]),
        ('AWS/Events', 'RuleName', 'WeatherCollectionSchedule', [(m, 'Sum') for m in ('TriggeredRules', 'Invocations', 'FailedInvocations')])]:
        for name_metric, stat in metrics:
            points = cw.get_metric_statistics(Namespace=namespace, MetricName=name_metric, Dimensions=[{'Name': dimension, 'Value': name}], StartTime=start, EndTime=end, Period=300, Statistics=[stat]).get('Datapoints', [])
            for point in sorted(points, key=lambda r: r['Timestamp']):
                rows.append({'namespace': namespace, 'metric': name_metric, 'statistic': stat, 'timestamp_utc': point['Timestamp'].astimezone(timezone.utc).isoformat(), 'value': point[stat], 'unit': point['Unit']})
    write_csv(folder / 'metrics.csv', rows, ['namespace', 'metric', 'statistic', 'timestamp_utc', 'value', 'unit'])
    write_json(folder / 'metric-consistency.json', metric_consistency(rows))
    graph_status = []
    for i, widget in enumerate(body['widgets']):
        if widget['type'] != 'metric':
            continue
        # Widget-image supports metric properties, not dashboard grid coordinates.
        props = {k: v for k, v in widget['properties'].items() if k != 'view'}
        props.update({'width': 1200, 'height': 550, 'start': start.isoformat(), 'end': end.isoformat(), 'view': 'timeSeries'})
        try:
            image = cw.get_metric_widget_image(MetricWidget=json.dumps(props), OutputFormat='png')['MetricWidgetImage']
        except ClientError as error:
            graph_status.append({'widget': i, 'status': 'UNAVAILABLE', 'code': error.response['Error']['Code']})
        else:
            if not image.startswith(b'\x89PNG\r\n\x1a\n'):
                raise ValueError('AWS metric image is not PNG')
            (folder / f'cloudwatch_{i:02d}.png').write_bytes(image)
            graph_status.append({'widget': i, 'status': 'PNG_RETURNED', 'bytes': len(image)})
    write_json(folder / 'dashboard-verification.json', {'profile': profile, 'dashboard': DASHBOARD, 'validation_messages': [], 'get_matches_put': True,
               'window_start': start.isoformat(), 'window_end': end.isoformat(), 'period_seconds': 300, 'metric_rows': len(rows),
               'images': graph_status, 'graph_semantics': 'Native AWS GetMetricWidgetImage snapshots; not screenshots of the Console UI'})
    print(json.dumps({'profile': profile, 'dashboard_matches': True, 'metric_rows': len(rows), 'images': graph_status}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--backup', type=Path, required=True)
    args = parser.parse_args()
    for profile in PROFILES:
        run(profile, args.output, args.backup)


if __name__ == '__main__':
    main()
