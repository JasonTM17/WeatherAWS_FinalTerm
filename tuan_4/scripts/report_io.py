"""Deterministic reports from the authenticated, immutable source snapshot."""
import argparse
import csv
import io
import json
from pathlib import Path
from snapshot_validation import FOLDER, validate


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def csv_bytes(rows, fields):
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode('utf-8')


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def publish(files, output, check=False):
    output = Path(output)
    if check:
        for name, blob in files.items():
            if (output / name).read_bytes() != blob:
                raise ValueError(f'Derived report differs from source: {name}')
    else:
        output.mkdir(parents=True, exist_ok=False)
        for name, blob in files.items():
            (output / name).write_bytes(blob)


def run(generator, default_output):
    parser = argparse.ArgumentParser(description=generator.__doc__)
    parser.add_argument('--source', type=Path, default=FOLDER)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if not args.check and args.output is None:
        parser.error('Provide a new output directory or use --check for the saved reports')
    validate(args.source)
    files = generator(args.source)
    publish(files, args.output or default_output, args.check)
    print(json.dumps({'status':'PASS','report_files':len(files),'aws_calls':False}))
