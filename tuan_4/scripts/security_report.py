"""Separate observed AWS storage controls from template declarations and IAM access."""
from pathlib import Path
from report_io import FOLDER, csv_bytes, load, run

OUTPUT = Path(__file__).resolve().parents[1] / 'results/security'


def generate_security_report(source=FOLDER):
    """Build a source-linked security matrix, not an unconditional PASS list."""
    source, rows = Path(source), []
    for profile in ('default','quyen'):
        folder = source / 'environment' / profile
        storage, role = load(folder/'storage.json'), load(folder/'role.json')
        for name, good, observed in [
            ('S3 Block Public Access',storage['all_public_access_blocks'],str(storage['all_public_access_blocks'])),
            ('S3 public ACL absent',not storage['public_acl'],str(storage['public_acl'])),
            ('S3 public policy absent',not storage['public_policy'],storage['bucket_policy']),
            ('S3 encryption',storage['encryption_algorithms']==['AES256'],','.join(storage['encryption_algorithms'])),
        ]:
            rows.append({'profile':profile,'scope':'observed_environment','control':name,
                'observed':observed,'status':'PASS' if good else 'FAIL',
                'evidence':f'verification_2026_10_19/environment/{profile}/storage.json'})
        rows.append({'profile':profile,'scope':'observed_environment','control':'S3 versioning',
            'observed':storage['versioning'],'status':'PASS' if storage['versioning']=='Enabled' else 'NOT_ENABLED',
            'evidence':f'verification_2026_10_19/environment/{profile}/storage.json'})
        rows.append({'profile':profile,'scope':'observed_environment','control':'Read LabRole policies',
            'observed':role.get('error_code',role['status']),'status':role['status'],
            'evidence':f'verification_2026_10_19/environment/{profile}/role.json'})
    for control in ('HTTPS-only bucket policy','Bound alarm-to-SNS Publish permission'):
        rows.append({'profile':'new_stack','scope':'declared_template','control':control,
            'observed':'Configured in canonical template','status':'DECLARED',
            'evidence':'../infrastructure/weather-stack.json'})
    return {'security_controls_audit.csv':csv_bytes(rows,list(rows[0]))}


if __name__ == '__main__':
    run(generate_security_report, OUTPUT)
