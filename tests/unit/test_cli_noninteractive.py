import importlib
import sys
import types
from datetime import date


def _import_cli_with_stubs(monkeypatch):
    """Insert lightweight stubs for questionary and rich modules, then import cli."""
    # minimal questionary stub
    q = types.ModuleType("questionary")
    q.select = lambda *a, **k: DummyPrompt(None)
    q.text = lambda *a, **k: DummyPrompt(None)
    q.prompt = lambda *a, **k: {}
    q.confirm = lambda *a, **k: DummyPrompt(True)
    # Provide names imported by the package at top-level
    q.Question = type("Question", (), {})
    q.Separator = lambda title: f"SEP:{title}"
    q.autocomplete = lambda *a, **k: DummyPrompt(None)
    q.checkbox = lambda *a, **k: DummyPrompt(None)
    q.password = lambda *a, **k: DummyPrompt(None)
    q.path = lambda *a, **k: DummyPrompt(None)
    monkeypatch.setitem(sys.modules, "questionary", q)

    # minimal rich stubs
    rc = types.ModuleType("rich.console")

    class FakeConsole:
        def print(self, *a, **k):
            return None

    rc.Console = FakeConsole
    monkeypatch.setitem(sys.modules, "rich.console", rc)

    rt = types.ModuleType("rich.table")

    class FakeTable:
        def __init__(self, *a, **k):
            self.rows = []

        def add_column(self, *a, **k):
            pass

        def add_row(self, *a, **k):
            self.rows.append(a)

    rt.Table = FakeTable
    monkeypatch.setitem(sys.modules, "rich.table", rt)

    rp = types.ModuleType("rich.panel")

    class FakePanel:
        @staticmethod
        def fit(*a, **k):
            return "PANEL"

    rp.Panel = FakePanel
    monkeypatch.setitem(sys.modules, "rich.panel", rp)

    # Also ensure 'rich' package name exists
    monkeypatch.setitem(sys.modules, "rich", types.ModuleType("rich"))

    return importlib.import_module("questionary_extended.cli")


def _load_cli_with_package_stubs(monkeypatch):
    """Create a fake 'questionary_extended' package with lightweight submodules
    and load cli.py by filename so imports are deterministic and lightweight.
    """
    import pathlib
    import sys
    import types

    from tests.helpers.test_helpers import load_module_from_path

    root = pathlib.Path(__file__).resolve().parents[2] / "src" / "questionary_extended"
    cli_path = str(root / "cli.py")

    # Prepare a fake package module
    pkg = types.ModuleType("questionary_extended")
    pkg.__path__ = [str(root)]
    pkg.__version__ = "0.0-test"

    # Submodule: prompts (lightweight stubs used by cli)
    prompts = types.ModuleType("questionary_extended.prompts")

    class DummyProgress:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def step(self, *a, **k):
            return None

        def complete(self, *a, **k):
            return None

    prompts.ProgressTracker = DummyProgress
    prompts.color = lambda *a, **k: DummyPrompt(None)
    prompts.enhanced_text = lambda *a, **k: DummyPrompt(None)
    prompts.number = lambda *a, **k: DummyPrompt(None)
    prompts.rating = lambda *a, **k: DummyPrompt(None)
    prompts.tree_select = lambda *a, **k: DummyPrompt(None)
    prompts.date = lambda *a, **k: DummyPrompt(None)

    # Submodule: styles
    styles = types.ModuleType("questionary_extended.styles")

    class ThemeStub:
        def __init__(self, name):
            self.name = name

            class Palette:
                primary = "#000000"

            self.palette = Palette()

    styles.THEMES = {"dark": ThemeStub("Dark")}
    styles.get_theme_names = lambda: ["dark"]

    # Submodule: utils
    utils_stub = types.ModuleType("questionary_extended.utils")
    utils_stub.format_date = lambda d, fmt=None: "DATE"
    utils_stub.format_number = lambda n, **k: str(n)

    # Insert into sys.modules so relative imports find them
    sys.modules["questionary_extended"] = pkg
    sys.modules["questionary_extended.prompts"] = prompts
    sys.modules["questionary_extended.styles"] = styles
    sys.modules["questionary_extended.utils"] = utils_stub

    # Ensure lightweight external stubs are present
    _import_cli_with_stubs(monkeypatch)

    module = load_module_from_path("questionary_extended.cli", cli_path)
    # Make relative imports resolve to our fake package (helper already sets __package__)
    return module


class DummyPrompt:
    def __init__(self, result):
        self._result = result

    def ask(self):
        return self._result


def test_themes_lists_and_print(monkeypatch):
    cli = _load_cli_with_package_stubs(monkeypatch)

    printed = []

    def fake_print(*a, **k):
        printed.append(a)

    monkeypatch.setattr(cli.console, "print", fake_print)

    # Avoid rich.Table rendering (emoji handling) in tests by providing a lightweight stand-in
    class DummyTable:
        def __init__(self, *a, **k):
            self.rows = []

        def add_column(self, *a, **k):
            pass

        def add_row(self, *a, **k):
            self.rows.append(a)

    monkeypatch.setattr(cli, "Table", DummyTable)

    # Call the underlying callback directly to avoid Click argv parsing
    cli.themes.callback()

    assert printed, "themes() should call console.print at least once"


def test_quick_various_prompt_types(monkeypatch):
    cli = _load_cli_with_package_stubs(monkeypatch)

    # Prepare dummy factories for each prompt type
    monkeypatch.setattr(cli, "enhanced_text", lambda *a, **k: DummyPrompt("hello"))
    monkeypatch.setattr(cli, "number", lambda *a, **k: DummyPrompt("42"))
    monkeypatch.setattr(
        cli, "date_prompt", lambda *a, **k: DummyPrompt(date(2020, 1, 1))
    )
    monkeypatch.setattr(
        cli.questionary, "select", lambda *a, **k: DummyPrompt("Option 1")
    )
    monkeypatch.setattr(cli, "rating", lambda *a, **k: DummyPrompt(5))
    monkeypatch.setattr(cli, "color", lambda *a, **k: DummyPrompt("#ff0000"))

    output = []
    monkeypatch.setattr(cli.console, "print", lambda *a, **k: output.append(a))

    types_and_expect = [
        ("text", "hello"),
        ("number", "42"),
        ("date", date(2020, 1, 1)),
        ("select", "Option 1"),
        ("rating", 5),
        ("color", "#ff0000"),
    ]

    for t, _expected in types_and_expect:
        output.clear()
        # call the callback function to avoid Click parsing
        cli.quick.callback(t)

        # The command will always call console.print at least once
        assert output, f"quick({t}) should print output"


def test_main_error_handling(monkeypatch):
    cli = _load_cli_with_package_stubs(monkeypatch)

    # Replace the click group callable so main() raises and we hit the exception handler
    def raise_error():
        raise RuntimeError("boom")

    monkeypatch.setattr(cli, "cli", raise_error)

    printed = []
    monkeypatch.setattr(cli.console, "print", lambda *a, **k: printed.append(a))

    try:
        cli.main()
    except SystemExit as se:
        # main should exit with code 1 on unhandled exceptions
        assert se.code == 1

    assert any(
        "Error" in str(x) or "Operation cancelled" in str(x)
        for tup in printed
        for x in tup
    )
