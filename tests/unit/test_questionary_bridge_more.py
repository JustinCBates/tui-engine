import types
import sys

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


def _inject_no_console_error_class():
    # Create fake prompt_toolkit.output.win32 module with the desired exception
    pkg = types.ModuleType("prompt_toolkit")
    out = types.ModuleType("prompt_toolkit.output")
    win32 = types.ModuleType("prompt_toolkit.output.win32")

    class NoConsoleScreenBufferError(Exception):
        pass

    win32.NoConsoleScreenBufferError = NoConsoleScreenBufferError
    sys.modules["prompt_toolkit"] = pkg
    sys.modules["prompt_toolkit.output"] = out
    sys.modules["prompt_toolkit.output.win32"] = win32
    # Ensure package attributes exist so 'from prompt_toolkit.output.win32 import ...'
    # will be able to access the submodules via package attributes, matching real package behavior.
    pkg.output = out
    out.win32 = win32
    return NoConsoleScreenBufferError


def test_creation_raises_no_console_error(monkeypatch):
    state = PageState()
    bridge = QuestionaryBridge(state)

    # ensure questionary appears available
    import questionary_extended.integration.questionary_bridge as qb

    monkeypatch.setattr(qb, "questionary", types.SimpleNamespace(), raising=False)

    NoConsole = _inject_no_console_error_class()

    class BadCreate:
        def create_questionary_component(self):
            raise NoConsole("no console")

    with pytest.raises(RuntimeError) as exc:
        bridge.ask_component(BadCreate())

    err = str(exc.value)
    assert ("questionary not usable" in err) or ("questionary prompt creation failed" in err)


def test_ask_raises_no_console_error(monkeypatch):
    state = PageState()
    bridge = QuestionaryBridge(state)

    import questionary_extended.integration.questionary_bridge as qb

    monkeypatch.setattr(qb, "questionary", types.SimpleNamespace(), raising=False)

    NoConsole = _inject_no_console_error_class()

    class P:
        def ask(self):
            raise NoConsole("ask failure")

    class C:
        name = "x"

        def create_questionary_component(self):
            return P()

    with pytest.raises(RuntimeError) as exc:
        bridge.ask_component(C())

    err = str(exc.value)
    assert ("questionary not usable" in err) or ("questionary prompt failed" in err)


def test_walk_components_card_else(monkeypatch):
    # Ensure the bridge uses a dummy questionary so ask_component can run
    import questionary_extended.integration.questionary_bridge as qb

    monkeypatch.setattr(qb, "questionary", types.SimpleNamespace(), raising=False)

    from questionary_extended.core.component import Component
    from questionary_extended.core.page import Page

    page = Page("p")
    card = page.card("c")

    c = Component("z", "text")
    c.create_questionary_component = lambda: StubPrompt(answer="ok")

    # Create a non-Component object that still has a components attribute
    class Holder:
        def __init__(self, components):
            self.components = components

    holder = Holder([c])
    # Put holder into the card components to trigger the Card else -> recursion
    card.components = [holder]

    bridge = QuestionaryBridge(page.state)
    bridge.run([card])
    assert page.state.get("z") == "ok"
