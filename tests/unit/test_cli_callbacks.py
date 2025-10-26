import sys
import types
from pathlib import Path

from tests.conftest_questionary import setup_questionary_mocks

# Centralized: skip this test module if the CLI wrapper is intentionally excluded
# skip_if_coverage_excluded("src/questionary_extended/cli.py")

# Install canonical questionary mock for deterministic imports
_module_q = setup_questionary_mocks(None)


class DummyPrompt:
    def __init__(self, value):
        self._value = value

    def ask(self):
        return self._value


class DummyProgressTracker:
    def __init__(self, *args, **kwargs):
        self.steps = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def step(self, msg: str):
        self.steps.append(msg)

    def complete(self, msg: str):
        self.completed = msg


def load_cli_module():
    # locate the cli.py relative to this test file
    repo_root = Path(__file__).resolve().parents[2]
    repo_root / "src" / "questionary_extended" / "cli.py"
    # Prefer importing the package from the local `src/` directory so package
    # metadata and relative imports resolve as expected. This avoids issues
    # when tests use an import-from-path loader that can inadvertently pick
    # up an installed package with the same name.
    src_dir = str(repo_root / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    import importlib

    pkg = importlib.import_module("questionary_extended")
    # Ensure package exposes a version for modules that expect it
    if not hasattr(pkg, "__version__"):
        pkg.__version__ = "0.0.0"

    module = importlib.import_module("questionary_extended.cli")
    try:
        # ensure the module references the canonical mock installed at module load
        module.questionary = _module_q
    except Exception:
        pass
    # replace rich Console with a simple print shim to avoid heavy rendering in tests
    module.console = types.SimpleNamespace(print=lambda *a, **k: print(*a, **k))
    return module


def test_themes_prints_table(capsys):
    cli = load_cli_module()
    # call the underlying function callback to avoid Click's CLI parsing
    cli.themes.callback()
    out = capsys.readouterr().out
    # Console printing may render a rich Table object; accept either the
    # rendered text or the table object's repr to keep tests stable in
    # headless environments.
    assert ("Available Themes" in out) or out.strip().startswith("<rich.table.Table")


def test_quick_variants_and_no_input(monkeypatch, capsys):
    cli = load_cli_module()

    # text
    monkeypatch.setattr(cli, "enhanced_text", lambda *a, **k: DummyPrompt("hello"))
    cli.quick.callback("text")
    out = capsys.readouterr().out
    assert "Result" in out and "hello" in out

    # number
    monkeypatch.setattr(cli, "number", lambda *a, **k: DummyPrompt("123"))
    cli.quick.callback("number")
    out = capsys.readouterr().out
    assert "Result" in out and ",123" in out or "123" in out

    # date
    monkeypatch.setattr(cli, "date_prompt", lambda *a, **k: DummyPrompt("2020-01-01"))
    cli.quick.callback("date")
    out = capsys.readouterr().out
    assert "Result" in out and "2020" in out

    # select
    dummy_q = types.SimpleNamespace(select=lambda *a, **k: DummyPrompt("Option 2"))
    monkeypatch.setattr(cli, "questionary", dummy_q)
    cli.quick.callback("select")
    out = capsys.readouterr().out
    assert "Result" in out and "Option 2" in out

    # rating
    monkeypatch.setattr(cli, "rating", lambda *a, **k: DummyPrompt(4))
    cli.quick.callback("rating")
    out = capsys.readouterr().out
    assert "Result" in out and "4" in out

    # color
    monkeypatch.setattr(cli, "color", lambda *a, **k: DummyPrompt("#ff0000"))
    cli.quick.callback("color")
    out = capsys.readouterr().out
    assert "Result" in out and "#ff0000" in out

    # no input (enhanced_text returning None)
    monkeypatch.setattr(cli, "enhanced_text", lambda *a, **k: DummyPrompt(None))
    cli.quick.callback("text")
    out = capsys.readouterr().out
    assert "No input provided" in out


def test_wizard_demo_runs_with_dummy_progress(monkeypatch, capsys):
    cli = load_cli_module()

    # patch ProgressTracker and questionary.text and time.sleep
    monkeypatch.setattr(cli, "ProgressTracker", DummyProgressTracker)
    # questionary is used via cli.questionary.text in wizard; ensure text returns a value
    monkeypatch.setattr(
        cli,
        "questionary",
        types.SimpleNamespace(text=lambda *a, **k: DummyPrompt("stepval")),
    )
    import time as _time

    monkeypatch.setattr(_time, "sleep", lambda s: None)

    # run with 2 steps to keep test short (call callback to avoid click parsing)
    cli.wizard_demo.callback(2)
    out = capsys.readouterr().out
    # should have printed captured values
    assert "Captured" in out or "Wizard completed" in out
