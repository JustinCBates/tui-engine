import importlib
import sys
import types

from questionary_extended.core.component import Component


def _ensure_fake_questionary():
    if "questionary" not in sys.modules:
        q = types.ModuleType("questionary")

        def _factory(**kwargs):
            return None

        for name in (
            "text",
            "select",
            "confirm",
            "password",
            "checkbox",
            "autocomplete",
            "path",
        ):
            setattr(q, name, _factory)

        sys.modules["questionary"] = q


def _reload_bridge():
    _ensure_fake_questionary()
    import questionary_extended.integration.questionary_bridge as bridge_module

    importlib.reload(bridge_module)
    return bridge_module


def test_walk_components_and_run_calls_ask(monkeypatch):
    bridge_module = _reload_bridge()

    # Create simple tree: card contains comp1 and nested assembly which contains comp2
    comp1 = Component("c1", "text")
    comp2 = Component("c2", "text")

    # Card and Assembly accept a 'parent' argument but it's not used at runtime here
    from questionary_extended.core.assembly import Assembly
    from questionary_extended.core.card import Card

    card = Card("CardTitle", parent=None)
    sub_asm = Assembly("sub", parent=None)
    sub_asm.components.append(comp2)
    card.components.append(comp1)
    card.components.append(sub_asm)

    # root list also includes a top-level component
    top = Component("top", "text")

    from questionary_extended.core.state import PageState

    bridge = bridge_module.QuestionaryBridge(state=PageState())

    called = []

    def fake_ask(c):
        called.append(c.name)

    monkeypatch.setattr(bridge, "ask_component", fake_ask)

    # Walk should yield comp1, comp2, and top (order depends on traversal)
    found = list(bridge._walk_components([card, top]))
    names = {c.name for c in found}
    assert "c1" in names and "c2" in names and "top" in names

    # Run should call our fake_ask for each visible component
    bridge.run([card, top])
    assert set(called) == names


def test_run_visibility_exception_defaults_visible(monkeypatch):
    bridge_module = _reload_bridge()

    class BadVisible(Component):
        def is_visible(self, state):
            raise RuntimeError("bad")

    bad = BadVisible("bad", "text")

    from questionary_extended.core.state import PageState

    bridge = bridge_module.QuestionaryBridge(state=PageState())

    called = []

    def fake_ask(c):
        called.append(c.name)

    monkeypatch.setattr(bridge, "ask_component", fake_ask)

    bridge.run([bad])
    # even though is_visible raised, run should treat it as visible and call ask
    assert called == ["bad"]


def test_run_skips_not_visible(monkeypatch):
    bridge_module = _reload_bridge()

    class Hidden(Component):
        def is_visible(self, state):
            return False

    hidden = Hidden("hid", "text")

    from questionary_extended.core.state import PageState

    bridge = bridge_module.QuestionaryBridge(state=PageState())

    called = []

    def fake_ask(c):
        called.append(c.name)

    monkeypatch.setattr(bridge, "ask_component", fake_ask)

    bridge.run([hidden])
    assert called == []


def test_walk_components_assembly_nested(monkeypatch):
    """Exercise the Assembly branch in _walk_components: Assembly -> Assembly -> Component"""
    bridge_module = _reload_bridge()

    from questionary_extended.core.assembly import Assembly
    from questionary_extended.core.component import Component

    outer = Assembly("outer", parent=None)
    inner = Assembly("inner", parent=None)
    comp = Component("deep", "text")
    inner.components.append(comp)
    outer.components.append(inner)

    # Confirm _walk_components yields the deep component
    from questionary_extended.core.state import PageState

    bridge = bridge_module.QuestionaryBridge(state=PageState())
    found = list(bridge._walk_components([outer]))
    names = {c.name for c in found}
    assert "deep" in names


def test_walk_components_direct_assembly_component():
    """Assembly contains a Component directly; _walk_components should yield it."""
    bridge_module = _reload_bridge()

    from questionary_extended.core.assembly import Assembly
    from questionary_extended.core.component import Component
    from questionary_extended.core.state import PageState

    asm = Assembly("asm", parent=None)
    comp = Component("direct", "text")
    asm.components.append(comp)

    bridge = bridge_module.QuestionaryBridge(state=PageState())
    found = list(bridge._walk_components([asm]))
    names = {c.name for c in found}
    assert "direct" in names


def test_walk_components_unknown_ignored():
    bridge_module = _reload_bridge()

    from questionary_extended.core.state import PageState

    bridge = bridge_module.QuestionaryBridge(state=PageState())

    # Pass an unknown object type; _walk_components should ignore it
    unknown = object()
    found = list(bridge._walk_components([unknown]))
    assert found == []


def test_walk_components_assembly_with_nested_container():
    bridge_module = _reload_bridge()

    from questionary_extended.core.assembly import Assembly
    from questionary_extended.core.component import Component
    from questionary_extended.core.state import PageState

    # Create a custom container (not an Assembly/Component) that exposes .components
    class Container:
        def __init__(self, comps):
            self.components = comps

    inner_comp = Component("inner", "text")
    container = Container([inner_comp])
    asm = Assembly("a", parent=None)
    asm.components.append(container)

    bridge = bridge_module.QuestionaryBridge(state=PageState())
    found = list(bridge._walk_components([asm]))
    names = {c.name for c in found}
    assert "inner" in names
