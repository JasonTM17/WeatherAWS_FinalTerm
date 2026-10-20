"""Validate authenticated data and the current canonical template evidence."""
import json
from pathlib import Path
from snapshot_validation import ROOT, digest, load, validate


def validate_current_template():
    folder = ROOT / 'tuan_4/results/template_validation_2026_10_19'
    manifest = load(folder / 'manifest.json')
    files = {p.name for p in folder.iterdir() if p.is_file() and p.name != 'manifest.json'}
    if set(manifest) != files:
        raise ValueError('Current template evidence membership differs')
    for name, expected in manifest.items():
        target = (folder/name).resolve()
        if not target.is_relative_to(folder.resolve()) or digest(target.read_bytes()) != expected:
            raise ValueError('Current template evidence hash differs')
    canonical = (ROOT/'tuan_4/infrastructure/weather-stack.json').read_text(encoding='utf-8').encode()
    if canonical != (folder/'template.json').read_bytes():
        raise ValueError('Canonical template differs from validated version')
    build = load(folder/'build.json')
    for profile in ('default','quyen'):
        proof = load(folder/f'{profile}.json')
        if proof['status'] != 'PASS' or proof['resource_count'] != 17 or proof['stack_created']:
            raise ValueError('Template API validation proof unavailable')
        if proof['template_sha256'] != digest(canonical) or build['template_sha256'] != digest(canonical):
            raise ValueError('Template digest differs from API/build evidence')
    return {'current_template_resources':17,'current_template_validation':'PASS'}


if __name__ == '__main__':
    from verify_advanced import validate as validate_advanced
    print(json.dumps({**validate(), **validate_current_template(), 'advanced':validate_advanced()}))
