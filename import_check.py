import importlib
import pprint
import sys
import traceback

print("PYTHON:", sys.executable)
pprint.pprint(sys.path[:6])
p = r"C:\Development\tui\tui-engine\src"
sys.path.insert(0, p)
try:
    print("IMPORTS_OK")
except Exception as e:
    print("IMPORT_FAILED", type(e).__name__, e)
    traceback.print_exc()

print("mypy", importlib.util.find_spec("mypy") is not None)
print("pytest", importlib.util.find_spec("pytest") is not None)
print("ruff", importlib.util.find_spec("ruff") is not None)
