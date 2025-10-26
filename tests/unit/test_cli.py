from pathlib import Path
from types import SimpleNamespace

from tests.conftest_questionary import setup_questionary_mocks
from tests.helpers.test_helpers import load_module_from_path

# For local runs we want to exercise the CLI callbacks. Comment out the
# coverage-based skip and install the canonical questionary mock so imports
# resolve deterministically and no real prompt_toolkit sessions are created.
# skip_if_coverage_excluded("src/questionary_extended/cli.py")

# Install canonical mock before loading the CLI module
_module_q = setup_questionary_mocks(None)

cli = load_module_from_path(
    "questionary_extended.cli",
    Path("src/questionary_extended/cli.py").resolve(),
)

try:
    cli.questionary = _module_q
except Exception:
    pass


def make_answer(val):
    return SimpleNamespace(ask=lambda *a, **k: val)


def test_themes_runs(monkeypatch):
    # patch console.print to avoid side effects
    printed = {}
    monkeypatch.setattr(
        cli,
        "console",
        SimpleNamespace(print=lambda *a, **k: printed.update({"called": True})),
    )
    # Call the underlying callback to avoid Click parsing argv
    cli.themes.callback()
    assert printed.get("called")


def test_quick_various_prompt_types(monkeypatch):
    # patch enhanced_text
    monkeypatch.setattr(cli, "enhanced_text", lambda *a, **k: make_answer("txt"))
    monkeypatch.setattr(cli, "number", lambda *a, **k: make_answer("123"))
    monkeypatch.setattr(cli, "date_prompt", lambda *a, **k: make_answer("2020-01-01"))
    # patch questionary.select
    monkeypatch.setattr(cli.questionary, "select", lambda *a, **k: make_answer("opt"))
    monkeypatch.setattr(cli, "rating", lambda *a, **k: make_answer(5))
    monkeypatch.setattr(cli, "color", lambda *a, **k: make_answer("#fff"))

    # patch console.print to capture outputs
    monkeypatch.setattr(cli, "console", SimpleNamespace(print=lambda *a, **k: None))

    # run for each prompt type
    for pt in ["text", "number", "date", "select", "rating", "color"]:
        # call the underlying callback directly to avoid Click argv parsing
        cli.quick.callback(pt)


def test_main_keyboardinterrupt_and_exception(monkeypatch):
    # Mock cli() to raise KeyboardInterrupt
    monkeypatch.setattr(
        cli, "cli", lambda *a, **k: (_ for _ in ()).throw(KeyboardInterrupt())
    )
    # patch console to avoid real printing
    monkeypatch.setattr(cli, "console", SimpleNamespace(print=lambda *a, **k: None))

    try:
        cli.main()
    except SystemExit as e:
        assert e.code == 1

    # Mock cli() to raise generic exception
    monkeypatch.setattr(
        cli, "cli", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    try:
        cli.main()
    except SystemExit as e:
        assert e.code == 1
