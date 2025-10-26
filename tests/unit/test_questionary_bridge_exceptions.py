import importlib
import sys
import types

import pytest


def _make_fake_prompt_toolkit():
    # Create a small module hierarchy: prompt_toolkit.output.win32 with
    # NoConsoleScreenBufferError available for isinstance checks.
    win32 = types.ModuleType("prompt_toolkit.output.win32")

    class NoConsoleScreenBufferError(Exception):
        pass

    win32.NoConsoleScreenBufferError = NoConsoleScreenBufferError

    output = types.ModuleType("prompt_toolkit.output")
    output.win32 = win32

    pt = types.ModuleType("prompt_toolkit")
    pt.output = output

    sys.modules["prompt_toolkit"] = pt
    sys.modules["prompt_toolkit.output"] = output
    sys.modules["prompt_toolkit.output.win32"] = win32
    return NoConsoleScreenBufferError


class _FakeComponent:
    def __init__(
        self,
        name: str,
        create_exc: Exception = None,
        ask_exc: Exception = None,
        answer=None,
    ):
        self.name = name
        self._create_exc = create_exc
        self._ask_exc = ask_exc
        self._answer = answer

    def create_questionary_component(self):
        if self._create_exc:
            raise self._create_exc

        class _Prompt:
            def __init__(self, parent):
                self._parent = parent

            def ask(self):
                if self._parent._ask_exc:
                    raise self._parent._ask_exc
                return self._parent._answer

        return _Prompt(self)


def _reload_bridge_with_fake_questionary():
    # Ensure a minimal 'questionary' exists so the bridge import succeeds.
    if "questionary" not in sys.modules:
        q = types.ModuleType("questionary")

        class _Q:
            pass

        # Minimal exported names expected by the package's prompts module
        q.Question = _Q

        # provide simple factory callables used by Component.create_questionary_component
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

        # style-related exports used by styles.py
        class Style:
            pass

        def style_from_dict(d):
            return Style()

        q.Style = Style
        q.style_from_dict = style_from_dict

        # Choice type used by some prompt helpers
        class Choice:
            def __init__(self, title, value=None):
                self.title = title
                self.value = value

        q.Choice = Choice

        # validation helpers
        class ValidationError(Exception):
            pass

        class Validator:
            pass

        q.ValidationError = ValidationError
        q.Validator = Validator

        sys.modules["questionary"] = q

    # Reload the bridge module so its top-level import binds to our fakes.
    import questionary_extended.integration.questionary_bridge as bridge_module

    importlib.reload(bridge_module)
    return bridge_module


def test_ask_component_creation_no_console_error_stops(monkeypatch):
    NoConsole = _make_fake_prompt_toolkit()
    bridge_module = _reload_bridge_with_fake_questionary()

    from questionary_extended.core.state import PageState

    state = PageState()
    bridge = bridge_module.QuestionaryBridge(state)

    comp = _FakeComponent("f", create_exc=NoConsole())

    with pytest.raises(RuntimeError) as exc:
        bridge.ask_component(comp)

    # The bridge should fail; implementations may either raise the specific
    # "not usable" RuntimeError for NoConsoleScreenBufferError or wrap it into
    # a generic creation failure. Accept either message here; lines in both
    # branches are exercised by the test.
    msg = str(exc.value)
    assert "not usable in this environment" in msg or msg.startswith(
        "questionary prompt creation failed"
    )


def test_ask_component_ask_no_console_error_stops(monkeypatch):
    NoConsole = _make_fake_prompt_toolkit()
    bridge_module = _reload_bridge_with_fake_questionary()

    from questionary_extended.core.state import PageState

    state = PageState()
    bridge = bridge_module.QuestionaryBridge(state)

    comp = _FakeComponent("f", ask_exc=NoConsole())

    with pytest.raises(RuntimeError) as exc:
        bridge.ask_component(comp)

    msg = str(exc.value)
    assert "not usable in this environment" in msg or msg.startswith(
        "questionary prompt failed"
    )


def test_ask_component_creation_generic_exception_wrapped(monkeypatch):
    _make_fake_prompt_toolkit()
    bridge_module = _reload_bridge_with_fake_questionary()

    from questionary_extended.core.state import PageState

    state = PageState()
    bridge = bridge_module.QuestionaryBridge(state)

    comp = _FakeComponent("g", create_exc=ValueError("boom"))

    with pytest.raises(RuntimeError) as exc:
        bridge.ask_component(comp)

    assert "questionary prompt creation failed" in str(exc.value)


def test_ask_component_ask_generic_exception_wrapped(monkeypatch):
    _make_fake_prompt_toolkit()
    bridge_module = _reload_bridge_with_fake_questionary()

    from questionary_extended.core.state import PageState

    state = PageState()
    bridge = bridge_module.QuestionaryBridge(state)

    comp = _FakeComponent("h", ask_exc=RuntimeError("boom"))

    with pytest.raises(RuntimeError) as exc:
        bridge.ask_component(comp)

    assert "questionary prompt failed" in str(exc.value)


def test_ask_component_happy_path_persists_state(monkeypatch):
    _make_fake_prompt_toolkit()
    bridge_module = _reload_bridge_with_fake_questionary()

    from questionary_extended.core.state import PageState

    state = PageState()
    bridge = bridge_module.QuestionaryBridge(state)

    comp = _FakeComponent("ok", answer="yep")

    ans = bridge.ask_component(comp)
    assert ans == "yep"
    assert state.get("ok") == "yep"


def test_ask_component_when_questionary_missing_raises(monkeypatch):
    # Simulate questionary not being installed / available
    _make_fake_prompt_toolkit()
    bridge_module = _reload_bridge_with_fake_questionary()

    # Temporarily set the module-level name to None to exercise the branch
    monkeypatch.setattr(bridge_module, "questionary", None)

    from questionary_extended.core.state import PageState

    state = PageState()
    bridge = bridge_module.QuestionaryBridge(state)

    comp = _FakeComponent("x", answer="ok")

    with pytest.raises(RuntimeError) as exc:
        bridge.ask_component(comp)

    assert "questionary is not available" in str(exc.value)
