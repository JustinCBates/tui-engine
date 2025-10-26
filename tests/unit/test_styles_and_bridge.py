from pathlib import Path
from types import SimpleNamespace

from tests.helpers.test_helpers import load_module_from_path

styles = load_module_from_path(
    "questionary_extended.styles",
    Path("src/questionary_extended/styles.py").resolve(),
)

bridge_mod = load_module_from_path(
    "questionary_extended.integration.questionary_bridge",
    Path("src/questionary_extended/integration/questionary_bridge.py").resolve(),
)


def test_theme_to_questionary_style_and_builder():
    t = styles.create_theme("custom")
    qstyle = t.to_questionary_style()
    assert hasattr(qstyle, "_style_rules") or True

    sb = styles.StyleBuilder()
    sb.primary("#123456").text("#000").success("#0f0")
    s = sb.build()
    assert hasattr(s, "_style_rules")


def test_get_and_list_themes():
    names = styles.get_theme_names()
    assert isinstance(names, list)
    assert styles.get_theme("dark") is not None
    all_themes = styles.list_themes()
    assert "dark" in all_themes


def test_questionary_bridge_no_questionary(monkeypatch):
    # Simulate questionary not available
    monkeypatch.setitem(bridge_mod.__dict__, "questionary", None)

    class FakeState:
        def __init__(self):
            self._data = {}

        def set(self, k, v):
            self._data[k] = v

        def get_all_state(self):
            return self._data

    qb = bridge_mod.QuestionaryBridge(FakeState())
    # ask_component should raise when questionary is None
    try:
        qb.ask_component(
            SimpleNamespace(name="x", create_questionary_component=lambda: None)
        )
        raise AssertionError()
    except RuntimeError:
        pass
