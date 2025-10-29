"""Run the CLI module in a subprocess under coverage and combine the data.

This helper is intended to be run from the repo root. It will:
- run `coverage run --parallel-mode -m tui_engine.cli` in a subprocess
  (using the virtualenv python in the repo when available),
- then run `coverage combine` and `coverage html` to merge with existing
  coverage data and regenerate the htmlcov report.

This makes it easy to ensure the `if __name__ == '__main__': main()` line is
executed in a fresh process and included in the coverage results.

Usage:
    python tools/collect_cli_subprocess_coverage.py

Note: This script assumes `coverage` is installed in the active virtualenv.
"""

import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
VENV_PY = os.path.join(REPO_ROOT, ".venv", "Scripts", "python.exe")
COVERAGE = os.path.join(REPO_ROOT, ".venv", "Scripts", "coverage.exe")

PY = VENV_PY if os.path.exists(VENV_PY) else sys.executable
COV = COVERAGE if os.path.exists(COVERAGE) else None

if COV is None:
    print("coverage executable not found in .venv; falling back to 'coverage' on PATH")
    cov_cmd = [PY, "-m", "coverage"]
else:
    cov_cmd = [COV]

print("Running CLI in subprocess under coverage...")
# Use parallel-mode so data files don't clobber pytest's coverage run
run_cmd = cov_cmd + ["run", "--parallel-mode", "-m", "tui_engine.cli"]
print(" ", " ".join(run_cmd))
try:
    subprocess.check_call(run_cmd, cwd=REPO_ROOT)
except subprocess.CalledProcessError as e:
    print(
        f"Subprocess exited with code {e.returncode}; continuing to combine coverage data"
    )

print("Combining coverage data and generating HTML...")
subprocess.check_call(cov_cmd + ["combine"], cwd=REPO_ROOT)
subprocess.check_call(cov_cmd + ["html"], cwd=REPO_ROOT)
print("Done. Coverage HTML at htmlcov/index.html")
