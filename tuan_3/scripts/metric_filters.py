"""Configure two bounded log counters without changing Lambda or sending test events."""
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from common import FUNCTION, PROFILES, client, session, write_csv, write_json

NAMESPACE = 'WeatherAWS/Collection'
LOG_GROUP = f'/aws/lambda/{FUNCTION}'
SAMPLES = [
    '[INFO] Result: {"collection_status":"complete","records_collected":3}',
    '[INFO] Result: {"collection_status":"partial","records_collected":2}',
    '[ERROR] Failed to fetch data for ExampleCity: TimeoutError',
    '[WARN] High pollution detected at ExampleCity',
    '[INFO] Lambda execution started.',
]


def definitions():
    return [
        {'filterName': 'Week3CollectionResultLines', 'filterPattern': '"Result:"',
         'metricTransformations': [{'metricName': 'ResultLogLines', 'metricNamespace': NAMESPACE,
                                   'metricValue': '1', 'unit': 'Count'}]},
        {'filterName': 'Week3CollectionErrorLines', 'filterPattern': '"[ERROR]"',
         'metricTransformations': [{'metricName': 'ErrorLogLines', 'metricNamespace': NAMESPACE,
                                   'metricValue': '1', 'unit': 'Count'}]},
    ]


def validate_match(response, expected):
    messages = [item['eventMessage'] for item in response.get('matches', [])]
    if sorted(messages) != sorted(expected):
        raise ValueError('AWS filter test did not match the exact expected positive/negative samples')


def normalized(item):
    return {key: item[key] for key in ('filterName', 'filterPattern', 'metricTransformations')}


def configure(profile, output, backup):
    sess = session(profile)
    account = client(sess, 'sts').get_caller_identity()['Account']
    config = client(sess, 'lambda').get_function_configuration(FunctionName=FUNCTION)
    if config['FunctionArn'].split(':')[4] != account:
        raise ValueError('Lambda account differs from authenticated environment')
    logs = client(sess, 'logs')
    before = [item for page in logs.get_paginator('describe_metric_filters').paginate(
        logGroupName=LOG_GROUP, filterNamePrefix='Week3Collection') for item in page['metricFilters']]
    backup_path = backup / profile / 'filters-before.json'
    if backup_path.exists():
        raise FileExistsError('Use a new private backup directory')
    write_json(backup_path, before)
    tests = []
    for desired, expected in zip(definitions(), (SAMPLES[:2], SAMPLES[2:3])):
        response = logs.test_metric_filter(filterPattern=desired['filterPattern'], logEventMessages=SAMPLES)
        validate_match(response, expected)
        tests.append({'filter': desired['filterName'], 'expected_matches': len(expected),
                      'observed_matches': len(response.get('matches', [])), 'status': 'PASS'})
    # Test both patterns before creating either filter. Refuse to replace existing different settings.
    indexed = {item['filterName']: item for item in before}
    for desired in definitions():
        if desired['filterName'] in indexed and normalized(indexed[desired['filterName']]) != desired:
            raise ValueError('Existing filter settings differ; no filter replaced')
    created = []
    for desired in definitions():
        if desired['filterName'] not in indexed:
            logs.put_metric_filter(logGroupName=LOG_GROUP, **desired)
            created.append(desired['filterName'])
    actual = [normalized(item) for page in logs.get_paginator('describe_metric_filters').paginate(
        logGroupName=LOG_GROUP, filterNamePrefix='Week3Collection') for item in page['metricFilters']]
    for desired in definitions():
        if desired not in actual:
            raise ValueError('Metric filter readback differs')
    proof = {'student': PROFILES[profile], 'configured_at': datetime.now(timezone.utc).isoformat(),
             'configuration_verified': True, 'created_filters': created, 'definitions': definitions(),
             'pattern_tests': tests, 'synthetic_events_ingested': False, 'lambda_invoked': False,
             'semantics': 'Counts matching new log lines, not failed invocations or independent samples; no historical backfill and no missing-to-zero fill'}
    write_json(output / profile / 'configuration.json', proof)
    return proof


def observe(profile, output, start, end):
    cw = client(session(profile), 'cloudwatch')
    rows = []
    counts = {}
    for name in ('ResultLogLines', 'ErrorLogLines'):
        result = cw.get_metric_statistics(Namespace=NAMESPACE, MetricName=name, StartTime=start,
            EndTime=end, Period=60, Statistics=['Sum'])
        points = sorted(result.get('Datapoints', []), key=lambda item: item['Timestamp'])
        counts[name] = sum(point['Sum'] for point in points) if points else None
        rows.extend({'metric': name, 'timestamp_utc': point['Timestamp'].astimezone(timezone.utc).isoformat(),
                     'value': point['Sum']} for point in points)
    write_csv(output / profile / 'log_metrics.csv', rows, ['metric', 'timestamp_utc', 'value'])
    write_json(output / profile / 'observation.json', {'window_start': start.isoformat(), 'window_end': end.isoformat(),
        'metric_sums': counts, 'result_ingestion_observed': counts['ResultLogLines'] is not None,
        'limitation': 'No point is unknown, not zero; absence cannot establish no errors or failed collection'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--backup', type=Path)
    parser.add_argument('--observe-only', action='store_true')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a new output directory')
    if not args.observe_only and not args.backup:
        parser.error('Configuration needs a private backup path')
    for profile in PROFILES:
        if not args.observe_only:
            configure(profile, args.output, args.backup)
        end = datetime.now(timezone.utc)
        observe(profile, args.output, end-timedelta(hours=2), end)
        print(f'{profile}: ' + ('metrics read' if args.observe_only else 'patterns tested and configuration readback verified'), flush=True)


if __name__ == '__main__':
    main()
