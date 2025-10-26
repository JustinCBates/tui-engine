from tests.helpers.questionary_helpers import mock_questionary_with_types
import types


def test_component_create_questionary_component_mappings():
    # Test questionary component type mappings using DI mock
    from questionary_extended.core.component import Component

    # Define expected values for each component type
    types_to_expected = {
        "text": "t",
        "select": "s",
        "confirm": True,
        "password": "p",
        "checkbox": ["a"],
        "autocomplete": "auto",
        "path": "C:/",
    }

    with mock_questionary_with_types(
        text="t",
        select="s", 
        confirm=True,
        password="p",
        checkbox=["a"],
        autocomplete="auto",
        path="C:/"
    ):
        for comp_type, expected in types_to_expected.items():
            c = Component(name=f"n_{comp_type}", component_type=comp_type, message="m")
            obj = c.create_questionary_component()
            assert hasattr(obj, "ask")
            assert obj.ask() == expected


def test_component_create_unsupported_type_raises():
    from questionary_extended.core.component import Component

    c = Component(name="bad", component_type="nope")
    try:
        c.create_questionary_component()
        raised = False
    except ValueError:
        raised = True

    assert raised


def test_questionary_bridge_handles_prompt_creation_and_ask_errors(monkeypatch):
    # Simulate prompt_toolkit NoConsoleScreenBufferError during creation and ask
    from questionary_extended.core.component import Component
    from questionary_extended.core.state import PageState
    from questionary_extended.integration.questionary_bridge import QuestionaryBridge

    ps = PageState()
    bridge = QuestionaryBridge(ps)

    comp = Component(name="f", component_type="text", message="m")

    class FakeConsoleError(Exception):
        pass

    # Ensure bridge import path will resolve to our FakeConsoleError class
    import sys

    fake_mod = types.SimpleNamespace(NoConsoleScreenBufferError=FakeConsoleError)
    sys.modules["prompt_toolkit.output.win32"] = fake_mod  # type: ignore

    # First: creation raises FakeConsoleError and bridge should wrap to RuntimeError
    def bad_factory(**k):
        raise FakeConsoleError("no console")

    # Monkeypatch component.create_questionary_component to raise
    monkeypatch.setattr(comp, "create_questionary_component", lambda: bad_factory())

    try:
        bridge.ask_component(comp)
        ok = False
    except RuntimeError:
        ok = True

    assert ok

    # Second: creation returns object whose ask() raises FakeConsoleError
    class BadPrompt:
        def ask(self):
            raise FakeConsoleError("ask failed")

    monkeypatch.setattr(comp, "create_questionary_component", lambda: BadPrompt())

    try:
        bridge.ask_component(comp)
        ok2 = False
    except RuntimeError:
        ok2 = True

    assert ok2
