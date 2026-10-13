"""Root test wrapper delegating to tuan_2/tests/test_analytics.py."""
import importlib.util
from pathlib import Path

_target = Path(__file__).resolve().parent.parent / "tuan_2" / "tests" / "test_analytics.py"
_spec = importlib.util.spec_from_file_location("_tuan2_test_analytics", _target)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

TestAnalytics = _mod.TestAnalytics
__all__ = ["TestAnalytics"]
