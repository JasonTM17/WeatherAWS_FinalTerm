"""Fail-closed report generation and actual PowerShell wrapper behavior."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tuan_4/scripts'))
from report_io import FOLDER, load, publish, validate
from cost_analysis import COST_DIR, generate_cost_reports
from reconcile_ops import OUTPUT_DIR, generate_reconciliation_dataset
from security_report import OUTPUT, generate_security_report


class TestWeek4Operations(unittest.TestCase):
    def test_report_import_after_infrastructure_helpers_uses_week4_snapshot(self):
        code = ("import sys;sys.path.insert(0,"+repr(str(ROOT/'tuan_4/scripts'))+
                ");import prepare_stack,verify_environment;import report_io;"
                "assert report_io.FOLDER.name == 'verification_2026_10_19'")
        result=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_saved_reports_reproduce_exactly_from_authenticated_source(self):
        validate()
        for generator,output in [(generate_cost_reports,COST_DIR),
            (generate_reconciliation_dataset,OUTPUT_DIR),(generate_security_report,OUTPUT)]:
            publish(generator(),output,check=True)

    def test_controlled_scope_does_not_become_a_whole_account_claim(self):
        files=generate_reconciliation_dataset()
        summary=json.loads(files['reconciliation_summary.json'])
        self.assertEqual(summary['controlled_requests'],2)
        self.assertEqual(summary['records_verified'],6)
        self.assertFalse(summary['all_objects_orphan_scan_performed'])
        self.assertFalse(summary['metric_filter_counts_measured'])
        self.assertIsNone(summary['whole_window_error_rate_percent'])

    def test_source_tampering_fails_before_report_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'source';shutil.copytree(FOLDER,folder)
            path=folder/'environment/default/cost_by_service.csv'
            path.write_bytes(path.read_bytes()+b'fabricated row\n')
            with self.assertRaises(ValueError): validate(folder)

    def test_cost_source_is_not_replaced_by_a_monthly_projection(self):
        summary=json.loads(generate_cost_reports()['cost_summary.json'])
        profiles=summary['profiles']
        self.assertEqual([p['rows'] for p in profiles],[70,47])
        self.assertEqual([p['display_usd'] for p in profiles],['0.00','0.14'])
        self.assertEqual(profiles[0]['start_inclusive'],'2026-10-12')
        self.assertEqual(profiles[1]['end_exclusive'],'2026-10-20')

    def test_iam_access_denial_is_not_labeled_pass(self):
        data=generate_security_report()['security_controls_audit.csv'].decode('utf-8')
        self.assertEqual(data.count('BLOCKED_CAPABILITY'),2)
        self.assertEqual(data.count('NOT_ENABLED'),4)  # observed value and status for each profile


class PowerShellWrapperTests(unittest.TestCase):
    def test_wrapper_preview_and_failure_exit_without_aws_calls(self):
        shell=shutil.which('pwsh') or shutil.which('powershell')
        if not shell: self.skipTest('PowerShell runtime not available')
        with tempfile.TemporaryDirectory(prefix='weather wrapper ') as tmp:
            fake=Path(tmp)/'fake python.ps1'
            fake.write_text("Write-Output ($args | ConvertTo-Json -Compress)\nexit 7\n",encoding='utf-8')
            state='output/week4_session_control/state with spaces.json'
            for wrapper,action in [('cleanup_resources.ps1','pause'),('start_resources.ps1','restore')]:
                command=[shell,'-NoProfile','-File',str(ROOT/'tuan_4/scripts'/wrapper),
                    '-Profile','default','-StateFile',state,'-Python',str(fake)]
                result=subprocess.run(command,text=True,encoding='utf-8',capture_output=True)
                self.assertEqual(result.returncode,7,result.stdout+result.stderr)
                args=json.loads(result.stdout.splitlines()[-1])
                self.assertIn(action,args)
                self.assertNotIn('--apply',args)
                self.assertTrue(args[-1].endswith('state with spaces.json'))
                result=subprocess.run(command+['-Apply'],text=True,encoding='utf-8',capture_output=True)
                self.assertEqual(result.returncode,7,result.stdout+result.stderr)
                self.assertEqual(json.loads(result.stdout.splitlines()[-1])[-1],'--apply')


if __name__ == '__main__':
    unittest.main()
