"""Offline acceptance fails when evidence or computed results are altered."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tuan_4/scripts'))
from verify_advanced import compare, manifest
import verify_advanced as evidence


class AdvancedEvidenceIntegrity(unittest.TestCase):
    def assert_changed_proof_rejected(self, filename, alter):
        original = evidence.load

        def changed(path):
            value = original(path)
            if path.name == filename:
                alter(value)
            return value

        with patch.object(evidence, 'load', side_effect=changed), self.assertRaises(ValueError):
            evidence.validate()

    def test_mixed_invocation_request_is_rejected_after_manifest_check(self):
        self.assert_changed_proof_rejected('invocation.json', lambda v: v.update(request_hash='0' * 20))

    def test_stale_standalone_select_is_rejected(self):
        self.assert_changed_proof_rejected('athena_exact.json', lambda v: v.update(query_id='stale-query'))

    def test_unconfirmed_recipient_cannot_be_blessed_by_valid_hashes(self):
        self.assert_changed_proof_rejected('recipient_confirmation.json', lambda v:
            v['profiles']['default'].update(recipient_receipt='AWAITING_USER_CONFIRMATION'))

    def test_benchmark_statistics_must_match_trial_proof(self):
        self.assert_changed_proof_rejected('registered_json_1.json', lambda v:
            v.update(engine_ms=v['engine_ms'] + 1))

    def test_benchmark_median_is_recomputed(self):
        def change(value):
            if 'medians' in value:
                value['medians']['registered_json']['total_ms'] += 1
        self.assert_changed_proof_rejected('summary.json', change)

    def test_benchmark_aggregate_is_recomputed_from_frozen_raw(self):
        original = evidence.rows

        def changed(path):
            value = original(path)
            if path.name == 'registered_json_1.csv':
                value[0]['samples'] = '999'
            return value

        with patch.object(evidence, 'rows', side_effect=changed), self.assertRaises(ValueError):
            evidence.validate()

    def test_changed_bytes_or_unlisted_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source = folder / 'result.json'
            source.write_bytes(b'original')
            (folder / 'manifest.json').write_text(json.dumps({
                'result.json': hashlib.sha256(b'original').hexdigest()}))
            manifest(folder)
            source.write_bytes(b'changed')
            with self.assertRaises(ValueError):
                manifest(folder)
            source.write_bytes(b'original')
            (folder / 'unexpected.txt').write_text('unreviewed')
            with self.assertRaises(ValueError):
                manifest(folder)

    def test_prediction_or_window_metadata_cannot_change(self):
        expected = [{'predicted': 12.5, 'window': 1, 'city': 'HaNoi'}]
        compare(expected, [{'predicted': '12.5', 'window': '1', 'city': 'HaNoi'}])
        for row in [{'predicted': '12.6', 'window': '1', 'city': 'HaNoi'},
                    {'predicted': '12.5', 'window': '2', 'city': 'HaNoi'}]:
            with self.subTest(row=row), self.assertRaises(ValueError):
                compare(expected, [row])


if __name__ == '__main__':
    unittest.main()
