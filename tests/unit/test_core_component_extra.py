from pathlib import Path
from tests.helpers.test_helpers import load_module_from_path
import importlib

# Load core component module with centralized helper to ensure __package__ is set
comp_mod = load_module_from_path(
    "questionary_extended.core.component",
    Path("src/questionary_extended/core/component.py").resolve(),
)


def test_component_init_and_config_filtering():
    c = comp_mod.Component("my_name", "text", when="x", enhanced_validation=True, foo=1)
    assert c.name == "my_name"
    assert c.when_condition == "x"
    # 'when' and 'enhanced_validation' should be removed from questionary_config
    assert "when" not in c.questionary_config
    assert "enhanced_validation" not in c.questionary_config
    assert c.questionary_config.get("foo") == 1


def test_add_validator_and_visibility():
    c = comp_mod.Component("n", "text")
    assert c.is_visible({}) is True
    c.add_validator(lambda v: True)
    assert len(c.validators) == 1


def test_create_questionary_component_calls_mapped_factory(monkeypatch):
    called = {}

    def fake_text(**kwargs):
        called.update(kwargs)
        return "created"

    monkeypatch.setattr(comp_mod.questionary, "text", fake_text)

    c = comp_mod.Component("n", "text", message="m")
    res = c.create_questionary_component()
    assert res == "created"
    assert called.get("message") == "m"


def test_create_questionary_component_unsupported():
    c = comp_mod.Component("n", "unsupported")
    try:
        c.create_questionary_component()
        assert False, "Expected ValueError for unsupported type"
    except ValueError as e:
        assert "Unsupported component type" in str(e)


def test_wrapper_default_messages():
    # Reload to avoid any prior test-side patches altering module-level
    # convenience functions; the helper ensures import-time state is reset.
    importlib.reload(comp_mod)
    t = comp_mod.text("my_field")
    assert isinstance(t, comp_mod.Component)
    assert "My Field" in t.questionary_config.get("message") or "my field" in t.questionary_config.get("message").lower()

    s = comp_mod.select("opt")
    assert s.questionary_config.get("choices") == []

    cb = comp_mod.checkbox("cb")
    assert cb.questionary_config.get("choices") == []

    p = comp_mod.password("pwd")
    assert isinstance(p, comp_mod.Component)
