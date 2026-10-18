"""Build or deploy only the reviewed Lambda module, with identity and rollback guards."""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

import boto3
from common import ROOT, FUNCTION, OPTIONS, digest, write_json


def package(source):
    buffer = io.BytesIO()
    # Stored bytes avoid zlib-version differences between Windows and Linux.
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_STORED) as archive:
        entry = zipfile.ZipInfo('lambda_function.py', date_time=(2026, 1, 1, 0, 0, 0))
        entry.create_system = 3
        entry.compress_type = zipfile.ZIP_STORED
        entry.external_attr = 0o644 << 16
        archive.writestr(entry, source)
    return buffer.getvalue()


def fingerprint(config):
    keys = ['Runtime', 'Role', 'Handler', 'Timeout', 'MemorySize', 'Environment', 'VpcConfig', 'KMSKeyArn',
            'TracingConfig', 'Layers', 'Architectures', 'EphemeralStorage', 'DeadLetterConfig', 'LoggingConfig']
    return digest(json.dumps({k: config.get(k) for k in keys}, sort_keys=True, default=str).encode())


def deployment(sess, expected_account, blob, evidence):
    account = sess.client('sts', config=OPTIONS).get_caller_identity()['Account']
    if account != expected_account:
        raise ValueError('Authenticated account differs from selected environment; nothing deployed')
    client = sess.client('lambda', config=OPTIONS)
    old = client.get_function(FunctionName=FUNCTION)
    before = old['Configuration']
    if before['Runtime'] != 'python3.12' or before['Handler'] != 'lambda_function.lambda_handler' or before['State'] != 'Active':
        raise ValueError('Unexpected Lambda runtime/handler/state; nothing deployed')
    with urllib.request.urlopen(old['Code']['Location'], timeout=30) as response:
        previous = response.read()
    if base64.b64encode(hashlib.sha256(previous).digest()).decode() != before['CodeSha256']:
        raise ValueError('Backup package digest mismatch; nothing deployed')
    evidence.mkdir(parents=True, exist_ok=False)
    (evidence / 'previous.zip').write_bytes(previous)
    proof = {'previous_package_sha256': digest(previous), 'requested_package_sha256': digest(blob), 'code_only': True}
    write_json(evidence / 'release.json', proof)
    update = client.update_function_code(FunctionName=FUNCTION, ZipFile=blob, RevisionId=before['RevisionId'])
    write_json(evidence / 'update.json', {'revision_id': update['RevisionId'], 'code_sha256': update['CodeSha256']})
    expected_sha = base64.b64encode(hashlib.sha256(blob).digest()).decode()
    try:
        client.get_waiter('function_updated_v2').wait(FunctionName=FUNCTION, WaiterConfig={'Delay': 3, 'MaxAttempts': 30})
        config = client.get_function_configuration(FunctionName=FUNCTION)
        if (config['CodeSha256'] != expected_sha or config['LastUpdateStatus'] != 'Successful'
                or config['State'] != 'Active' or fingerprint(config) != fingerprint(before)):
            raise RuntimeError('Post-deployment identity/configuration check failed')
    except Exception:
        # Never overwrite a revision created by another operator or pipeline.
        current = client.get_function_configuration(FunctionName=FUNCTION)
        proof['status'] = 'FAIL'
        if current['RevisionId'] != update['RevisionId']:
            proof['rollback_status'] = 'BLOCKED_CONCURRENT_REVISION'
        else:
            try:
                client.update_function_code(FunctionName=FUNCTION, ZipFile=previous, RevisionId=update['RevisionId'])
                client.get_waiter('function_updated_v2').wait(FunctionName=FUNCTION, WaiterConfig={'Delay': 3, 'MaxAttempts': 30})
                restored = client.get_function_configuration(FunctionName=FUNCTION)
                proof['rollback_verified'] = (restored['CodeSha256'] == before['CodeSha256']
                                              and restored['LastUpdateStatus'] == 'Successful'
                                              and fingerprint(restored) == fingerprint(before))
            except Exception:
                proof['rollback_status'] = 'FAILED_OR_UPDATE_STILL_IN_PROGRESS'
        write_json(evidence / 'release.json', proof)
        raise RuntimeError('Deployment verification failed; inspect sanitized rollback proof') from None
    proof.update({'status': 'PASS', 'configuration_unchanged': True, 'state': config['State'], 'last_update_status': config['LastUpdateStatus'], 'deployed_package_sha256': digest(blob)})
    write_json(evidence / 'release.json', proof)
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--deploy', action='store_true')
    parser.add_argument('--expected-account')
    parser.add_argument('--confirm-environment', choices=['tien-son', 'ngoc-quyen'])
    args = parser.parse_args()
    source = (ROOT / 'tuan_2/lambda/lambda_function.py').read_bytes()
    blob = package(source)
    if args.deploy:
        if not args.expected_account or not args.confirm_environment:
            parser.error('Deployment needs explicit account and environment confirmation')
        proof = deployment(boto3.Session(region_name='us-east-1'), args.expected_account, blob, args.output)
        print(json.dumps({k: proof[k] for k in ('status', 'configuration_unchanged', 'state')}))
    else:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'lambda.zip').write_bytes(blob)
        write_json(args.output / 'manifest.json', {'module_sha256': digest(source), 'package_sha256': digest(blob),
                   'entry': 'lambda_function.py', 'deployed': False})
        print('Built reproducible Lambda artifact; no AWS call performed')


if __name__ == '__main__':
    main()
