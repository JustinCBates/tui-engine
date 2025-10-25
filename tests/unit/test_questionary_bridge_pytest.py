import types
import pytest

from questionary_extended.integration.questionary_bridge import QuestionaryBridge
from questionary_extended.core.state import PageState


class StubPrompt:
    def __init__(self, answer=None, raise_on_ask=None):
        self._answer = answer
        self._raise_on_ask = raise_on_ask

    def ask(self):
        if self._raise_on_ask:
            raise self._raise_on_ask
        return self._answer


class FakeComponent:
    def __init__(self, name, comp):
        self.name = name
        self._comp = comp

    def create_questionary_component(self):
        return self._comp

    def is_visible(self, state):
        return True


def test_ask_component_happy_path(monkeypatch):
    state = PageState()
    bridge = QuestionaryBridge(state)

    # ensure questionary module exists (register a dummy module)
    import sys

    sys.modules["questionary"] = types.SimpleNamespace()

    prompt = StubPrompt(answer="ok")
    comp = FakeComponent("c1", prompt)

    res = bridge.ask_component(comp)
    assert res == "ok"
    assert state.get("c1") == "ok"


def test_ask_component_creation_failure_wrapped(monkeypatch):
    state = PageState()
    bridge = QuestionaryBridge(state)

    # set questionary available
    import sys

    sys.modules["questionary"] = types.SimpleNamespace()

    class BadComp:
        def create_questionary_component(self):
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        bridge.ask_component(BadComp())


def test_ask_component_ask_failure_wrapped(monkeypatch):
    state = PageState()
    bridge = QuestionaryBridge(state)
    import sys

    sys.modules["questionary"] = types.SimpleNamespace()

    # Simulate prompt.ask raising generic Exception
    prompt = StubPrompt(raise_on_ask=RuntimeError("ask fail"))
    comp = FakeComponent("c2", prompt)

    with pytest.raises(RuntimeError):
        bridge.ask_component(comp)


def test_run_walk_components_and_visibility_error(monkeypatch):
    state = PageState()
    bridge = QuestionaryBridge(state)
    import sys

    sys.modules["questionary"] = types.SimpleNamespace()

    # Component that raises in is_visible
    class BadVisible:
        def __init__(self):
            self.name = "bad"

        def is_visible(self, s):
            raise ValueError("bad visible")

        def create_questionary_component(self):
            return StubPrompt(answer="x")

    # Use a real Component instance and monkeypatch its methods so it's
    # yielded by _walk_components and its is_visible raises.
    from questionary_extended.core.component import Component

    comp = Component("bad", "text")

    # monkeypatch instance methods
    def bad_is_visible(s):
        raise ValueError("bad visible")

    comp.is_visible = bad_is_visible
    comp.create_questionary_component = lambda: StubPrompt(answer="x")

    bridge.run([comp])
    # Should have stored value despite visibility error defaulting to visible
    assert state.get("bad") == "x"
