"""Validate the preserved final-week snapshot without contacting AWS."""
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tuan_3/scripts'))
from common import digest

FOLDER = ROOT / 'tuan_4/results/verification_2026_10_19'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate():
    manifest = load(FOLDER / 'manifest.json')
    for name, expected in manifest.items():
        path = (FOLDER / name).resolve()
        if not path.is_relative_to(FOLDER.resolve()) or digest(path.read_bytes()) != expected:
            raise ValueError('Snapshot hash differs')
    expected_files = {p.relative_to(FOLDER).as_posix() for p in FOLDER.rglob('*')
                      if p.is_file() and p != FOLDER / 'manifest.json'}
    if set(manifest) != expected_files:
        raise ValueError('Snapshot manifest does not cover all evidence files')
    for profile in ('default', 'quyen'):
        proof = load(FOLDER / 'e2e' / profile / 'e2e.json')
        period = load(FOLDER / 'controlled' / f'{profile}.json')
        query = load(FOLDER / 'e2e' / profile / 'athena_exact.json')
        if (proof['status'] != 'PASS' or proof['athena_status'] != 'PASS'
                or proof['records'] != 3 or proof['reported_sns_acceptances'] != proof['expected_alerts']
                or proof['request_hash'] != period['request_hash']
                or period['native_invocations'] != 1 or period['native_errors'] != 0
                or query['status'] != 'SUCCEEDED' or query['result_reused']):
            raise ValueError('Controlled execution proof differs')
        with (FOLDER / 'e2e' / profile / 'raw_invocation.csv').open(encoding='utf-8', newline='') as handle:
            raw = list(csv.DictReader(handle))
        with (FOLDER / 'e2e' / profile / 'athena_exact.csv').open(encoding='utf-8', newline='') as handle:
            selected = list(csv.DictReader(handle))
        source = {r['record_id']: r for r in raw}
        if (len(raw) != 3 or len(selected) != 3 or len(source) != 3 or
                {r['record_id'] for r in selected} != set(source)):
            raise ValueError('Exact-record selection differs')
        for row in selected:
            original = source[row['record_id']]
            if any(float(row[k]) != float(original[k]) for k in ('us_aqi', 'pm2_5')) or row['city'] != original['city']:
                raise ValueError('Athena values differ from raw')
        archived = [json.loads(line) for file in (FOLDER / 'e2e' / profile / 'objects').rglob('*.json')
                    for line in file.read_text(encoding='utf-8').splitlines() if line.strip()]
        normalized = [{k: str(v) for k,v in row.items()} for row in archived]
        if sorted(normalized, key=lambda r:r['record_id']) != sorted(raw, key=lambda r:r['record_id']):
            raise ValueError('CSV differs from preserved S3 objects')
        template = load(FOLDER / 'environment' / profile / 'template.json')
        if (template['status'] != 'PASS' or template['resource_count'] != 15 or template['stack_created']
                or template['template_sha256'] != digest((ROOT / 'tuan_4/infrastructure/weather-stack.json').read_bytes())):
            raise ValueError('Validated template differs from current source')
    return {'status': 'PASS', 'manifest_files': len(manifest), 'controlled_invocations': 2,
            'exact_records': 6, 'live_queries': 2, 'new_stack_created': False}


if __name__ == '__main__':
    print(json.dumps(validate()))
