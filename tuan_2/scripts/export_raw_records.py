"""Export raw Athena records, or explicitly copy the saved raw CSV snapshot."""
from pathlib import Path
import argparse
import tempfile
import shutil
from athena_export import main as export_main

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='*')
    parser.add_argument('--output', '-o', action='append', default=[])
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--region', default='us-east-1')
    args = parser.parse_args()
    targets = [Path(path) for path in args.paths + args.output]
    if not targets:
        targets = [ROOT / 'results/data_exports/raw_weather_aqi_records.csv']
    source = ROOT / 'results/athena_queries/raw_weather_aqi_records.csv'
    with tempfile.TemporaryDirectory() as temporary:
        if not args.offline:
            export_main(['--only', 'raw_weather_aqi_records', '--region', args.region, '--output', temporary])
            source = Path(temporary) / 'raw_weather_aqi_records.csv'
        if not source.is_file():
            raise FileNotFoundError('No saved raw data is available.')
        for target in targets:
            if target.resolve() == source.resolve():
                raise ValueError('The destination must differ from the saved source.')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    print('Copied saved raw records.' if args.offline else 'Exported raw records from Athena.')

if __name__ == '__main__':
    main()
