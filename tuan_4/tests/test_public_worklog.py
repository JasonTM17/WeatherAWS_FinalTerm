"""Local-only reading material must not satisfy published worklog evidence."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('public_audit', ROOT/'tuan_2/scripts/repository_audit.py')
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class PublicWorklogTests(unittest.TestCase):
    def check_evidence(self, evidence, published):
        hours = [(1,'24110054','9.5'),(1,'24110051','9.0'),
                 (2,'24110054','10.0'),(2,'24110051','9.5'),
                 (3,'24110054','10.0'),(3,'24110051','10.0'),
                 (4,'24110054','10.0'),(4,'24110051','10.0')]
        rows = [dict(week=f'Tuần {week}',student_id=student,duration_hours=duration,
                     evidence_paths=evidence) for week,student,duration in hours]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'private.md').write_text('local reading',encoding='utf-8')
            (root/'report.md').write_text('published proof',encoding='utf-8')
            (root/'records').mkdir()
            (root/'records'/'raw.csv').write_text('a\n1\n',encoding='utf-8')
            with patch.object(audit,'ROOT',root), patch.object(audit,'csv_rows',return_value=([],rows)), patch.object(audit,'repository_paths',return_value=published):
                return audit.validate_worklogs()

    def test_local_only_existing_file_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'not published'):
            self.check_evidence('private.md',['report.md'])

    def test_directory_without_published_members_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'not published'):
            self.check_evidence('records',['report.md'])

    def test_published_file_preserves_confirmed_total(self):
        self.assertEqual(self.check_evidence('report.md',['report.md']),'78.0')

    def test_directory_with_published_member_is_allowed(self):
        self.assertEqual(self.check_evidence('records',['records/raw.csv']),'78.0')


if __name__ == '__main__':
    unittest.main()
