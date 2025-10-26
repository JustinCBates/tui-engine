import pathlib
from types import SimpleNamespace


class DummyPrompt:
    def __init__(self, result=None, raise_on_ask=False):
        self._result = result
        self._raise = raise_on_ask

    def ask(self):
        if self._raise:
            raise RuntimeError("ask failed")
        return self._result


class PageStateStub:
    def __init__(self):
        self.store = {}

    def set(self, key, value):
        self.store[key] = value

    def get_all_state(self):
        return dict(self.store)

    def get(self, key, default=None):
        return self.store.get(key, default)


class ComponentStub:
    def __init__(
        self,
        name,
        prompt_result=None,
        create_raises=None,
        ask_raises=False,
        visible=True,
    ):
        self.name = name
        self._prompt = prompt_result
        self._create_raises = create_raises
        self._ask_raises = ask_raises
        self._visible = visible

    def create_questionary_component(self):
        if self._create_raises:
            raise self._create_raises
        return DummyPrompt(self._prompt, raise_on_ask=self._ask_raises)

    def is_visible(self, all_state):
        return self._visible


def load_bridge_module():
    root = (
        pathlib.Path(__file__).resolve().parents[2]
        / "src"
        / "questionary_extended"
        / "integration"
    )
    path = str(root / "questionary_bridge.py")
    from tests.helpers.test_helpers import load_module_from_path

    module = load_module_from_path(
        "questionary_extended.integration.questionary_bridge", path
    )
    return module


def test_ask_component_success():
    mod = load_bridge_module()
    state = PageStateStub()
    bridge = mod.QuestionaryBridge(state)
    comp = ComponentStub("field1", prompt_result="value1")

    res = bridge.ask_component(comp)
    assert res == "value1"
    assert state.store.get("field1") == "value1"


def test_ask_component_create_error():
    mod = load_bridge_module()
    state = PageStateStub()
    bridge = mod.QuestionaryBridge(state)
    comp = ComponentStub("f", create_raises=ValueError("create fail"))

    try:
        bridge.ask_component(comp)
        raise AssertionError("should have raised RuntimeError")
    except RuntimeError as e:
        assert (
            "prompt creation failed" in str(e)
            or "questionary not usable" in str(e)
            or "prompt creation" in str(e)
        )


def test_ask_component_ask_error():
    mod = load_bridge_module()
    state = PageStateStub()
    bridge = mod.QuestionaryBridge(state)
    comp = ComponentStub("f", prompt_result=None, ask_raises=True)

    try:
        bridge.ask_component(comp)
        raise AssertionError("should have raised RuntimeError")
    except RuntimeError as e:
        assert "prompt failed" in str(e)


def test_run_walk_components_and_visibility(monkeypatch):
    mod = load_bridge_module()
    # Make the module's type checks accept our stubs
    mod.Component = ComponentStub

    mod.Card = SimpleNamespace
    mod.Assembly = SimpleNamespace
    state = PageStateStub()
    bridge = mod.QuestionaryBridge(state)

    # Create mixed items: direct Component, Card with components, and Assembly-like container
    c1 = ComponentStub("one", prompt_result="v1", visible=True)
    c2 = ComponentStub("two", prompt_result="v2", visible=False)

    card = SimpleNamespace(components=[c2])
    assembly = SimpleNamespace(components=[card])

    asked = []

    def fake_ask_component(self, component):
        asked.append(component.name)
        return component.create_questionary_component().ask()

    monkeypatch.setattr(mod.QuestionaryBridge, "ask_component", fake_ask_component)

    bridge.run([c1, card, assembly])
    # only c1 should be asked (c2 is not visible)
    assert "one" in asked
    assert "two" not in asked


import pytest

from questionary_extended.core.component import Component
from questionary_extended.integration.questionary_bridge import QuestionaryBridge


class DummyState:
    def __init__(self):
        self._data = {}

    def set(self, key, value):
        self._data[key] = value

    def get_all_state(self):
        return dict(self._data)


class FakePrompt:
    def __init__(self, answer=None):
        self._answer = answer

    def ask(self):
        return self._answer


def test_ask_component_persists_answer(monkeypatch):
    state = DummyState()
    bridge = QuestionaryBridge(state)

    comp = Component("f", "text", message="x")

    # Monkeypatch Component.create_questionary_component to return our fake prompt
    monkeypatch.setattr(comp, "create_questionary_component", lambda: FakePrompt("ok"))

    ans = bridge.ask_component(comp)
    assert ans == "ok"
    assert state._data["f"] == "ok"


def test_run_walks_components_and_skips_invisible(monkeypatch):
    state = DummyState()
    bridge = QuestionaryBridge(state)

    c1 = Component("a", "text")
    c2 = Component("b", "text")

    # make c2 not visible
    c2.is_visible = lambda s: False

    monkeypatch.setattr(c1, "create_questionary_component", lambda: FakePrompt("A"))
    monkeypatch.setattr(c2, "create_questionary_component", lambda: FakePrompt("B"))

    bridge.run([c1, c2])

    # Only c1 was asked and stored
    assert state._data == {"a": "A"}


def test_ask_component_wraps_prompt_errors(monkeypatch):
    state = DummyState()
    bridge = QuestionaryBridge(state)

    comp = Component("g", "text")

    # Simulate create_questionary_component raising an arbitrary exception
    def raise_err():
        raise RuntimeError("boom")

    monkeypatch.setattr(comp, "create_questionary_component", raise_err)

    with pytest.raises(RuntimeError):
        bridge.ask_component(comp)
