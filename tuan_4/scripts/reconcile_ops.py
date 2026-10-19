"""Derive controlled reconciliation from preserved logs, raw and native counters."""
from pathlib import Path
from report_io import FOLDER, csv_bytes, json_bytes, load, read_csv, run

OUTPUT_DIR = Path(__file__).resolve().parents[1] / 'results/monitoring'


def generate_reconciliation_dataset(source=FOLDER):
    """Reproduce observed controlled requests without manufacturing hourly runs."""
    source, rows = Path(source), []
    for profile in ('default','quyen'):
        controlled = load(source / 'controlled' / f'{profile}.json')
        matched = [r for r in read_csv(source / 'environment' / profile / 'collection_s3.csv')
                   if r['request_hash'] == controlled['request_hash']]
        if len(matched) != 1 or matched[0]['status'] != 'PASS':
            raise ValueError('Controlled request is not uniquely matched in preserved logs')
        log = matched[0]
        if int(log['verified_records']) != controlled['s3_records']:
            raise ValueError('S3 counts differ from request proof')
        rows.append({'profile':profile,'student':controlled['student'],
            'request_hash':controlled['request_hash'],'timestamp_utc':log['timestamp_utc'],
            'native_invocations':controlled['native_invocations'],'native_errors':controlled['native_errors'],
            'reported_records':int(log['reported_records']),'s3_verified_records':int(log['verified_records']),
            'cities':int(log['cities']),'sns_acceptances':controlled['sns_acceptances'],
            'metric_filter_result_lines':'','status':'MATCH',
            'evidence':f'verification_2026_10_19/controlled/{profile}.json'})
    summary = {'status':'PASS','controlled_requests':len(rows),
        'records_verified':sum(r['s3_verified_records'] for r in rows),
        'native_invocations_in_controlled_periods':sum(r['native_invocations'] for r in rows),
        'native_errors_in_controlled_periods':sum(r['native_errors'] for r in rows),
        'scope':'Two controlled requests with lifecycle, raw and Athena evidence',
        'whole_window_error_rate_percent':None,'all_objects_orphan_scan_performed':False,
        'all_invocations_audited':False,'metric_filter_counts_measured':False}
    return {'log_metric_s3_reconciliation.csv':csv_bytes(rows,list(rows[0])),
            'reconciliation_summary.json':json_bytes(summary)}


if __name__ == '__main__':
    run(generate_reconciliation_dataset, OUTPUT_DIR)
