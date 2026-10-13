"""Root test entry point for SDK regressions."""
import importlib.util
from pathlib import Path
target=Path(__file__).resolve().parents[1]/'tuan_2/tests/test_sdk.py'
spec=importlib.util.spec_from_file_location('_tuan2_test_sdk',target)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
TestSdk=module.TestSdk
