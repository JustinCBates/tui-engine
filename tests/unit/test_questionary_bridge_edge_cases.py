import sys
import types

import pytest

from questionary_extended.core.state import PageState
from questionary_extended.integration.questionary_bridge import QuestionaryBridge


class StubPrompt:
    def __init__(self, answer=None, raise_on_ask=None):
        self._answer = answer
        self._raise_on_ask = raise_on_ask

    def ask(self):
        if self._raise_on_ask:
            raise self._raise_on_ask
        return self._answer


def test_ask_component_no_questionary_module(monkeypatch):
    state = PageState()
    bridge = QuestionaryBridge(state)

    # Mock _resolve_questionary to return None to simulate questionary not available
    # This approach works even with the autouse fixture that installs questionary mocks
    monkeypatch.setattr(bridge, "_resolve_questionary", lambda: None)

    class C:
        name = "c"

        def create_questionary_component(self):
            return StubPrompt(answer="v")

    with pytest.raises(RuntimeError):
        bridge.ask_component(C())


def test_ask_component_prompt_toolkit_wrapped(monkeypatch):
    # Simulate prompt_toolkit NoConsoleScreenBufferError during creation and ask
    state = PageState()
    bridge = QuestionaryBridge(state)

    # register a dummy questionary module to pass the initial availability check
    sys.modules["questionary"] = types.SimpleNamespace()

    class FakeErr(Exception):
        pass

    class BadCreate:
        def create_questionary_component(self):
            # raise an exception that will not map to prompt_toolkit on import
            raise FakeErr("creation failed")

    with pytest.raises(RuntimeError):
        bridge.ask_component(BadCreate())


def test_walk_components_nested(monkeypatch):
    state = PageState()
    bridge = QuestionaryBridge(state)
    # ensure the bridge's module-level `questionary` variable is set so
    # ask_component doesn't raise on availability check
    import questionary_extended.integration.questionary_bridge as qb

    monkeypatch.setattr(qb, "questionary", types.SimpleNamespace(), raising=False)

    from questionary_extended.core.component import Component

    # Use real Page/Card/Assembly objects so isinstance checks in
    # QuestionaryBridge._walk_components succeed.
    from questionary_extended.core.page import Page

    page = Page("p")
    card = page.card("group")
    assembly = page.assembly("asm")

    c1 = Component("a", "text")
    c1.create_questionary_component = lambda: StubPrompt(answer="1")
    c2 = Component("b", "text")
    c2.create_questionary_component = lambda: StubPrompt(answer="2")

    # nest components
    card.components = [c1, assembly]
    assembly.components = [c2]

    bridge.run([card])
    assert state.get("a") == "1"
    assert state.get("b") == "2"
