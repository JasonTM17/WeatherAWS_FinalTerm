"""Root test wrapper delegating to tuan_2/tests/test_lambda_function.py."""
import importlib.util
from pathlib import Path

_target = Path(__file__).resolve().parent.parent / "tuan_2" / "tests" / "test_lambda_function.py"
_spec = importlib.util.spec_from_file_location("_tuan2_test_lambda", _target)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

TestWeatherCollectorLambda = _mod.TestWeatherCollectorLambda
__all__ = ["TestWeatherCollectorLambda"]
