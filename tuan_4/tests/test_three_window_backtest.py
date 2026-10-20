"""Causal window boundaries and complete measured output, not just file existence."""
from datetime import datetime,timedelta,timezone
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tuan_4/scripts'))
from backtest_three_windows import evaluate,CITIES


def fixture():
    start=datetime(2026,1,1,tzinfo=timezone.utc)
    return [dict(city=city,timestamp_utc=(start+timedelta(hours=i)).isoformat(),us_aqi=20+i,pm2_5=5+i/5)
            for city in CITIES for i in range(120)]


class HistoricalBacktestTests(unittest.TestCase):
    def test_exact_three_window_coverage_and_strict_temporal_boundary(self):
        predictions,metrics=evaluate(fixture())
        self.assertEqual((len(predictions),len(metrics)),(432,18))
        for row in metrics:
            self.assertEqual(datetime.fromisoformat(row['target_start_utc'])-datetime.fromisoformat(row['train_end_utc']),timedelta(hours=1))
        self.assertEqual({row['window'] for row in predictions},{1,2,3})

    def test_heldout_values_never_change_same_origin_predictions(self):
        records=fixture();before,_=evaluate(records)
        # Mutate final window targets only, leaving timestamps/origin/training unchanged.
        final_start=max(datetime.fromisoformat(r['timestamp_utc']) for r in records)-timedelta(hours=23)
        for row in records:
            if datetime.fromisoformat(row['timestamp_utc'])>=final_start:row['us_aqi']+=10000;row['pm2_5']+=10000
        after,_=evaluate(records)
        self.assertEqual([r['predicted'] for r in before if r['window']==3],
                         [r['predicted'] for r in after if r['window']==3])
        self.assertNotEqual([r['actual_model_value'] for r in before if r['window']==3],
                            [r['actual_model_value'] for r in after if r['window']==3])

    def test_missing_hour_does_not_get_filled_or_silently_skipped(self):
        records=fixture();records.pop(85)
        with self.assertRaisesRegex(ValueError,'missing'):evaluate(records)

    def test_duplicate_city_hour_is_rejected(self):
        records=fixture();records.append(dict(records[-1]))
        with self.assertRaisesRegex(ValueError,'Repeated'):evaluate(records)

    def test_nonfinite_data_is_rejected(self):
        records=fixture();records[-1]['pm2_5']=float('nan')
        with self.assertRaisesRegex(ValueError,'Nonfinite'):evaluate(records)


if __name__=='__main__':unittest.main()
