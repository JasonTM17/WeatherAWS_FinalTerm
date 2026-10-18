"""Offline reconciliation for retained Week 3 evidence and CSV/figure manifests."""
import json
import math

from benchmark import assert_equal_groups
from common import ROOT, digest, read_csv
from forecast import evaluate
from quality import inspect_rows


def verify(folder):
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        path = (folder / item['path']).resolve()
        if not path.is_relative_to(folder.resolve()) or digest(path.read_bytes()) != item['sha256'] or path.stat().st_size != item['bytes']:
            raise ValueError('Retained evidence path/hash mismatch')
    for profile in ('default', 'quyen'):
        raw = read_csv(folder / 'snapshot' / profile / 'raw_all.csv')
        actual, groups = inspect_rows(raw)
        saved = json.loads((folder / 'snapshot' / profile / 'snapshot.json').read_text(encoding='utf-8'))
        for key in ('records', 'week3_calendar_records', 'issues', 'city_hour_groups'):
            if actual[key] != saved[key]:
                raise ValueError('Snapshot quality mismatch')
        if len(groups) != len(read_csv(folder / 'snapshot' / profile / 'hourly_city.csv')):
            raise ValueError('Snapshot hourly group count mismatch')
        benchmark = read_csv(folder / 'benchmark' / profile / 'benchmark.csv')
        if len(benchmark) != 9 or any(r['result_reused'].lower() != 'false' for r in benchmark):
            raise ValueError('Benchmark trial count/reuse mismatch')
        tables = json.loads((folder / 'benchmark' / profile / 'tables.json').read_text())
        if any(item['registered_partitions'] for item in tables.values() if item['projected']):
            raise ValueError('Projection evidence uses registered partitions')
        reference = read_csv(folder / 'benchmark' / profile / 'queries/registered_json_1.csv')
        for trial in benchmark:
            observed = read_csv(folder / 'benchmark' / profile / 'queries' / f"{trial['format']}_{trial['trial']}.csv")
            assert_equal_groups(reference, observed)
    history = read_csv(folder / 'forecast/hourly_model_history.csv')
    metrics = read_csv(folder / 'forecast/forecast_metrics.csv')
    for city in sorted({r['city'] for r in history}):
        for variable in ('us_aqi', 'pm2_5'):
            expected, _, _ = evaluate([r for r in history if r['city'] == city], variable)
            for row in expected:
                saved = next(r for r in metrics if r['city'] == city and r['variable'] == variable and r['model'] == row['model'])
                for field in ('mae', 'rmse', 'bias'):
                    if not math.isclose(float(saved[field]), row[field], rel_tol=1e-11, abs_tol=1e-9):
                        raise ValueError('Forecast holdout error mismatch')
    return {'status': 'PASS', 'manifest_files': len(manifest['files']), 'profiles': 2, 'benchmark_trials': 18, 'forecast_metrics': len(metrics)}


if __name__ == '__main__':
    print(json.dumps(verify(ROOT / 'tuan_3/results/integration_2026_10_18')))
