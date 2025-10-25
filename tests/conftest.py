import pytest

from .conftest_questionary import setup_questionary_mocks


# Ensure a minimal `questionary` mock is present at import/collection time so
# test modules that `import questionary` or `from questionary import ...` at
# module scope receive the compatibility shim. setup_questionary_mocks accepts
# monkeypatch=None and will write into sys.modules on its own.
setup_questionary_mocks(None)


@pytest.fixture(autouse=True)
def _install_questionary_mock(monkeypatch):
    """Autouse fixture: ensure the test-level monkeypatch is wired to the
    same mock so individual tests can override factories with the monkeypatch
    fixture if needed.
    """
    setup_questionary_mocks(monkeypatch)
    yield
import os
import threading
import logging
import sys
import pytest

from .logging_utils import (
    sanitize_nodeid,
    ensure_dir,
    default_log_dir,
    get_worker_id,
    JsonFormatter,
    RedactingFormatter,
)

# Default per-test timeout in seconds. Can be overridden with environment variable
# TEST_TIMEOUT_SECONDS. Choose a conservative default: 5s per unit test.
DEFAULT_TIMEOUT = int(os.getenv("TEST_TIMEOUT_SECONDS", "5"))

_has_timeout_plugin = False

def pytest_configure(config):
    global _has_timeout_plugin
    # pytest-timeout registers under name 'timeout'
    _has_timeout_plugin = config.pluginmanager.hasplugin("timeout")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook wrapper to attach the report object to the test `item` so
    fixtures can inspect the outcome during teardown.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


def pytest_runtest_setup(item):
    """Print the test name and configured timeout before the test runs.

    This echoes the nodeid and the effective timeout so test runners
    immediately see what is about to run.
    """
    # Determine effective timeout (env overrides default)
    timeout = int(os.getenv("TEST_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT)))
    # Print a concise RUNNING line to the terminal
    print(f"RUNNING {item.nodeid} (timeout={timeout}s)")

def pytest_runtest_call(item):
    """Run each test with a timeout fallback when pytest-timeout is not installed.

    If the pytest-timeout plugin is installed, we defer to it (it provides better
    integration and test interruption). Otherwise we run the test in a daemon
    thread and fail the test if it doesn't finish within the timeout. Note: the
    thread may continue to run in background if a timeout occurs; this avoids
    hanging the test runner while still reporting a clear failure.
    """
    if _has_timeout_plugin:
        # Let the timeout plugin manage test timeouts
        return None

    timeout = DEFAULT_TIMEOUT

    result = {}

    def _target():
        try:
            item.runtest()
            result['ok'] = True
        except Exception as e:
            result['exc'] = e

    t = threading.Thread(target=_target, name=f"test-thread-{item.nodeid}")
    t.daemon = True
    t.start()
    t.join(timeout)
    if t.is_alive():
        # Fail the test with a clear timeout message
        pytest.fail(f"Test '{item.nodeid}' exceeded time limit of {timeout} seconds", pytrace=False)

    if 'exc' in result:
        # Re-raise the captured exception so pytest records it normally
        raise result['exc']


@pytest.fixture(autouse=True)
def per_test_logger(request):
    """Per-test logging fixture.

    Creates a per-test log file and attaches a FileHandler for the duration
    of the test. By default logs are written to `test-logs/{worker}/{nodeid}.log`.

    Behavior controlled by env vars:
      TEST_LOG_DIR - base directory for logs (default: repo-root/test-logs)
      TEST_LOG_LEVEL - logging level (default: INFO)
      TEST_LOG_JSON - if set to '1' use JSON lines (not implemented fully)
      TEST_LOG_ECHO - if set to '1' also stream logs to stdout in real-time
    On test failure the per-test log is printed to the terminal so the
    developer can see the full diagnostics without opening the file.
    """
    cfg = request.config
    nodeid = request.node.nodeid
    worker = get_worker_id(cfg)

    base_dir = os.getenv("TEST_LOG_DIR", default_log_dir())
    worker_dir = os.path.join(base_dir, worker)
    ensure_dir(worker_dir)

    fname = sanitize_nodeid(nodeid) + ".log"
    path = os.path.join(worker_dir, fname)

    level_name = os.getenv("TEST_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # JSON and redaction options
    json_mode = os.getenv("TEST_LOG_JSON", "0") == "1"
    redact_mode = os.getenv("TEST_LOG_REDACT", "0") == "1"
    redact_patterns = None
    rp = os.getenv("TEST_LOG_REDACT_PATTERNS")
    if rp:
        try:
            # allow JSON list or semicolon-separated
            import json as _json

            redact_patterns = _json.loads(rp)
            if not isinstance(redact_patterns, list):
                redact_patterns = None
        except Exception:
            redact_patterns = [p for p in rp.split(";") if p]

    # Configure file handler
    fh = logging.FileHandler(path, encoding="utf8")
    if json_mode:
        inner_fmt = JsonFormatter()
        if redact_mode:
            fmt = RedactingFormatter(inner=inner_fmt, redaction_patterns=redact_patterns)
        else:
            fmt = inner_fmt
    else:
        base = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        if redact_mode:
            fmt = RedactingFormatter(fmt=base._fmt, redaction_patterns=redact_patterns, inner=base)
        else:
            fmt = base

    fh.setFormatter(fmt)
    fh.setLevel(level)

    root = logging.getLogger()
    # Inject nodeid/worker into each record so formatters (esp JSON) can include them
    class _InjectNodeFilter(logging.Filter):
        def __init__(self, nodeid, worker):
            super().__init__()
            self._nodeid = nodeid
            self._worker = worker

        def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
            record.nodeid = self._nodeid
            record.worker = self._worker
            return True

    inject_filter = _InjectNodeFilter(nodeid, worker)
    fh.addFilter(inject_filter)
    root.addHandler(fh)

    # Optionally echo logs in real time
    echo = os.getenv("TEST_LOG_ECHO", "0") == "1"
    sh = None
    if echo:
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(fmt)
        sh.setLevel(level)
        sh.addFilter(inject_filter)
        root.addHandler(sh)

    # Yield to the test
    try:
        yield
    finally:
        # On teardown, flush and remove handlers
        try:
            root.removeHandler(fh)
            fh.flush()
            fh.close()
        except Exception:
            pass

        if sh:
            try:
                root.removeHandler(sh)
                sh.flush()
                sh.close()
            except Exception:
                pass

        # If test failed during the call phase, print the log file to stdout
        rep = getattr(request.node, "rep_call", None)
        if rep is not None and rep.failed:
            print("\n=== LOG OUTPUT FOR FAILED TEST: {} ===".format(nodeid))
            try:
                with open(path, "r", encoding="utf8") as fh2:
                    for line in fh2:
                        # Print lines as-is so terminal preserves formatting
                        sys.stdout.write(line)
            except Exception as e:
                print(f"(failed to read log file {path}: {e})")
            print("=== END LOG OUTPUT ===\n")
"""Test conftest helpers.

This file patches importlib.util.module_from_spec to pre-set module.__package__
from the spec parent when tests use the common pattern:

    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

Setting __package__ this way avoids DeprecationWarning: __package__ != __spec__.parent
which appears when spec.parent is present but module.__package__ wasn't set.

This is a minimal, low-risk shim used only during test runs.
"""
import importlib.util as _iu
from pathlib import Path

import pytest

_orig_module_from_spec = _iu.module_from_spec


def _module_from_spec_with_pkg(spec):
    m = _orig_module_from_spec(spec)
    parent = getattr(spec, "parent", None)
    if parent:
        # Ensure package matches spec.parent to avoid DeprecationWarning
        try:
            m.__package__ = parent
        except Exception:
            pass
    return m


# Patch during test collection/runtime
_iu.module_from_spec = _module_from_spec_with_pkg


def pytest_collection_modifyitems(config, items):
    skip_marker = pytest.mark.skip(
        reason=("Skip local integration workflow during unit test run")
    )
    for item in items:
        try:
            p = Path(item.fspath)
            if "scripts" in p.parts and p.name == "test_ci_local.py":
                item.add_marker(skip_marker)
        except Exception:
            continue


# Autouse fixture to ensure a test-friendly `questionary` implementation is
# present early in every test. This prevents accidental creation of real
# prompt_toolkit sessions on headless CI/Windows and centralizes the test
# mock installation/teardown.
@pytest.fixture(autouse=True)
def ensure_questionary_mock(request, monkeypatch):
    import sys
    import importlib

    prev = sys.modules.get("questionary", None)
    from .conftest_questionary import setup_questionary_mocks

    mock = setup_questionary_mocks(monkeypatch)
    # Ensure the test module's `questionary` name (if present) points at
    # the mock so tests that do `import questionary` at module scope and
    # then call `monkeypatch.setattr(questionary, ...)` will modify the
    # same object the code-under-test uses.
    try:
        mod = getattr(request, "module", None)
        if mod is not None and hasattr(mod, "questionary"):
            setattr(mod, "questionary", mock)
    except Exception:
        pass

    try:
        yield mock
    finally:
        # Clear the runtime cache on teardown
        try:
            rt = importlib.import_module("questionary_extended._runtime")
            rt.clear_questionary_for_tests()
        except Exception:
            pass

        # Restore previous sys.modules entry for 'questionary' if any
        if prev is None:
            try:
                del sys.modules["questionary"]
            except Exception:
                pass
        else:
            sys.modules["questionary"] = prev

    # Create short aliases for modules under both 'questionary_extended' and
    # 'src.questionary_extended' package names. Some tests patch symbols using
    # the 'src.' prefix (eg. `src.questionary_extended.core.component`) while
    # others reference the non-src package name. Ensure both names point at the
    # same module object so such patches affect the actual module used by the
    # code-under-test.
    try:
        import sys as _sys

        aliases = [
            ("questionary_extended.core.component", "src.questionary_extended.core.component"),
            ("questionary_extended.prompts_core", "src.questionary_extended.prompts_core"),
            ("questionary_extended.prompts", "src.questionary_extended.prompts"),
            ("questionary_extended.core", "src.questionary_extended.core"),
        ]
        for base, alias in aliases:
            try:
                m = _sys.modules.get(base)
                if m is not None and alias not in _sys.modules:
                    _sys.modules[alias] = m
                m2 = _sys.modules.get(alias)
                if m2 is not None and base not in _sys.modules:
                    _sys.modules[base] = m2
            except Exception:
                continue
    except Exception:
        pass
