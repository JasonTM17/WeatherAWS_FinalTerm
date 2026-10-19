"""Summarize actual Cost Explorer groups, retaining precision and Estimated."""
from decimal import Decimal
from pathlib import Path
from report_io import FOLDER, csv_bytes, json_bytes, load, read_csv, run

COST_DIR = Path(__file__).resolve().parents[1] / 'results/cost'


def generate_cost_reports(source=FOLDER):
    """Reproduce billing evidence without price or Free Tier assumptions."""
    rows, summaries = [], []
    names = {'default':'Sinh viên Tiến Sơn','quyen':'Sinh viên Ngọc Quyên'}
    for profile, student in names.items():
        folder = Path(source) / 'environment' / profile
        proof, values = load(folder / 'cost.json'), read_csv(folder / 'cost_by_service.csv')
        if proof['status'] != 'PASS' or len(values) != proof['rows']:
            raise ValueError('Cost Explorer evidence is incomplete')
        total = sum((Decimal(r['amount_usd']) for r in values), Decimal('0'))
        if not total.is_finite() or total != Decimal(proof['total_unblended_usd']):
            raise ValueError('Cost total differs from original service groups')
        for item in values:
            if item['estimated'] not in ('True','False') or not Decimal(item['amount_usd']).is_finite():
                raise ValueError('Invalid billing group')
            rows.append({'profile':profile,'student':student,**item})
        rounded = total.quantize(Decimal('0.01'))
        summaries.append({'profile':profile,'student':student,'rows':len(values),
            'start_inclusive':proof['start_inclusive'],'end_exclusive':proof['end_exclusive'],
            'total_unblended_usd':str(total),'display_usd':'0.00' if rounded == 0 else str(rounded),
            'scope':'Account by service and record type, not allocated project/monthly billing'})
    return {'learner_lab_cost_breakdown.csv':csv_bytes(rows,
                ['profile','student','date_utc','service','record_type','amount_usd','estimated']),
            'cost_summary.json':json_bytes({'status':'PASS','profiles':summaries,
                'source':'verification_2026_10_19/environment/*/cost_by_service.csv'})}


if __name__ == '__main__':
    run(generate_cost_reports, COST_DIR)
