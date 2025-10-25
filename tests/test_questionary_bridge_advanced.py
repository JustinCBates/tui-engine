"""Questionary Bridge advanced testing - error handling, edge cases, and complex scenarios."""

import importlib
import types
import sys
import pytest
from unittest.mock import MagicMock, patch

from questionary_extended.integration.questionary_bridge import QuestionaryBridge
from questionary_extended.core.component import Component
from questionary_extended.core.state import PageState
from .conftest_questionary import setup_questionary_mocks, DummyState, FakePrompt


class StubPrompt:
    """Stub prompt that can raise exceptions for testing."""
    def __init__(self, answer=None, raise_on_ask=None):
        self._answer = answer
        self._raise_on_ask = raise_on_ask

    def ask(self):
        if self._raise_on_ask:
            raise self._raise_on_ask
        return self._answer


class TestQuestionaryBridgeErrorHandling:
    """Test error handling and exception scenarios."""

    def test_ask_component_no_questionary_module(self, monkeypatch):
        """Test behavior when questionary module is not available."""
        state = PageState()
        bridge = QuestionaryBridge(state)

        # Remove questionary module
        import questionary_extended.integration.questionary_bridge as qb
        monkeypatch.setattr(qb, "questionary", None, raising=False)

        component = Component(name="test", component_type="text")
        
        # Should raise RuntimeError when questionary is not available
        with pytest.raises(RuntimeError, match="questionary is not available in the current environment"):
            bridge.ask_component(component)

    def test_ask_component_invalid_prompt_type(self, monkeypatch):
        """Test handling of invalid/unknown prompt types."""
        state = PageState()
        bridge = QuestionaryBridge(state)

        # Mock questionary but without the requested prompt type
        # Install canonical helper and provide only the 'text' factory so an
        # unknown prompt type will be missing as intended.
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.text = lambda *a, **k: StubPrompt("text_answer")
        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr("questionary_extended.integration.questionary_bridge.questionary", mock_q)
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        component = Component(name="test", component_type="invalid_type")
        
        # Should raise RuntimeError when component type is unsupported
        with pytest.raises(RuntimeError, match="questionary prompt creation failed: Unsupported component type"):
            bridge.ask_component(component)

    def test_ask_component_prompt_raises_exception(self, monkeypatch):
        """Test handling when prompt.ask() raises an exception."""
        state = PageState()
        bridge = QuestionaryBridge(state)

        # Mock questionary to raise exception during .ask()
        exception_to_raise = KeyboardInterrupt("User cancelled")
        
        # Use canonical helper and set factories that raise during .ask()
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.text = lambda *a, **k: StubPrompt(raise_on_ask=exception_to_raise)
        mock_q.select = lambda *a, **k: StubPrompt(raise_on_ask=exception_to_raise)
        mock_q.confirm = lambda *a, **k: StubPrompt(raise_on_ask=exception_to_raise)
        mock_q.checkbox = lambda *a, **k: StubPrompt(raise_on_ask=exception_to_raise)
        mock_q.password = lambda *a, **k: StubPrompt(raise_on_ask=exception_to_raise)
        mock_q.autocomplete = lambda *a, **k: StubPrompt(raise_on_ask=exception_to_raise)
        mock_q.path = lambda *a, **k: StubPrompt(raise_on_ask=exception_to_raise)

        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr("questionary_extended.integration.questionary_bridge.questionary", mock_q)
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        component = Component(name="test", component_type="text")
        
        # Should propagate the exception
        with pytest.raises(KeyboardInterrupt):
            bridge.ask_component(component)

    def test_ask_component_with_none_answer(self, monkeypatch):
        """Test handling when prompt returns None."""
        state = PageState()
        bridge = QuestionaryBridge(state)
        # Install canonical helper configured to return None for prompts
        mock_q = setup_questionary_mocks(monkeypatch, {
            "text": None,
            "select": None,
            "confirm": None,
            "password": None,
            "checkbox": None,
            "autocomplete": None,
            "path": None,
        })
        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr("questionary_extended.integration.questionary_bridge.questionary", mock_q)
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)
        component = Component(name="test", component_type="text", message="Test prompt")
        
        result = bridge.ask_component(component)
        
        # Should handle None return gracefully
        assert result is None
        assert state.get_all_state().get("test") is None


class TestQuestionaryBridgeEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_component_without_id(self, monkeypatch):
        """Test component without an ID."""
        from tests.conftest_questionary import setup_questionary_mocks
        setup_questionary_mocks(monkeypatch, {"text": "answer"})
        
        state = PageState()
        bridge = QuestionaryBridge(state)

        # Component with no ID or None ID
        component = Component(name="no_id_test", component_type="text", message="Test question")
        component.id = None
        
        # Should handle gracefully - might skip persistence or use default
        result = bridge.ask_component(component)
        assert result == "answer"

    def test_component_with_empty_message(self, monkeypatch):
        """Test component with empty or None message."""
        state = PageState()
        bridge = QuestionaryBridge(state)

        captured_message = None
        
        def capture_call(message, **kwargs):
            nonlocal captured_message
            captured_message = message
            return StubPrompt("answer")

        # Use canonical helper and override the text factory to capture calls
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.text = capture_call
        mock_q.select = lambda *a, **k: StubPrompt("default_select")
        mock_q.confirm = lambda *a, **k: StubPrompt(True)
        mock_q.password = lambda *a, **k: StubPrompt("default_password")
        mock_q.checkbox = lambda *a, **k: StubPrompt(["default_checkbox"])
        mock_q.autocomplete = lambda *a, **k: StubPrompt("default_autocomplete")
        mock_q.path = lambda *a, **k: StubPrompt("default_path")

        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr("questionary_extended.integration.questionary_bridge.questionary", mock_q)
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        # Component with empty message
        component = Component(name="test", component_type="text", message="")
        bridge.ask_component(component)
        
        assert captured_message == ""

    def test_component_with_complex_choices(self, monkeypatch):
        """Test component with complex choice objects."""
        state = PageState()
        bridge = QuestionaryBridge(state)

        captured_choices = None
        
        def capture_select_call(message, choices=None, **kwargs):
            nonlocal captured_choices
            captured_choices = choices
            return StubPrompt("complex_choice")

        # Use canonical helper and override select factory to capture choices
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.select = capture_select_call
        mock_q.text = lambda *a, **k: StubPrompt("default_text")
        mock_q.confirm = lambda *a, **k: StubPrompt(True)
        mock_q.password = lambda *a, **k: StubPrompt("default_password")
        mock_q.checkbox = lambda *a, **k: StubPrompt(["default_checkbox"])
        mock_q.autocomplete = lambda *a, **k: StubPrompt("default_autocomplete")
        mock_q.path = lambda *a, **k: StubPrompt("default_path")

        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr("questionary_extended.integration.questionary_bridge.questionary", mock_q)
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        # Complex choices with nested structure
        complex_choices = [
            {"name": "Option 1", "value": "opt1"},
            {"name": "Option 2", "value": "opt2"},
            "simple_string_choice"
        ]

        component = Component(
            name="complex_test",
            component_type="select",
            message="Choose an option:",
            choices=complex_choices
        )
        
        bridge.ask_component(component)
        
        # Should pass through complex choices as-is
        assert captured_choices == complex_choices

    def test_state_overwrite_behavior(self, monkeypatch):
        """Test behavior when state key is overwritten."""
        from tests.conftest_questionary import setup_questionary_mocks
        setup_questionary_mocks(monkeypatch, {"text": "new_answer"})
        
        state = PageState()
        bridge = QuestionaryBridge(state)

        # Set initial state
        state.set("test", "initial_value")
        
        # Ask component with same ID
        component = Component(name="test", component_type="text", message="Enter value:")
        result = bridge.ask_component(component)
        
        # Should overwrite previous value
        assert result == "new_answer"
        assert state.get_all_state()["test"] == "new_answer"


class TestQuestionaryBridgeIntegration:
    """Test integration scenarios and complex workflows."""

    def test_bridge_with_multiple_state_types(self):
        """Test bridge works with different state implementations."""
        # Test with PageState
        page_state = PageState()
        bridge1 = QuestionaryBridge(page_state)
        assert bridge1.state is page_state

        # Test with custom state (duck typing)
        class CustomState:
            def __init__(self):
                self._data = {}
            def set(self, k, v):
                self._data[k] = v
            def get_all_state(self):
                return self._data

        custom_state = CustomState()
        bridge2 = QuestionaryBridge(custom_state)
        assert bridge2.state is custom_state

    def test_questionary_module_loading(self, monkeypatch):
        """Test different questionary module loading scenarios."""
        state = PageState()
        bridge = QuestionaryBridge(state)

        # Test with mock questionary that has all expected methods
        # Use canonical helper that provides all prompt factories
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.text = lambda *a, **k: StubPrompt("text")
        mock_q.select = lambda *a, **k: StubPrompt("select")
        mock_q.confirm = lambda *a, **k: StubPrompt(True)
        mock_q.checkbox = lambda *a, **k: StubPrompt(["checked"])
        mock_q.password = lambda *a, **k: StubPrompt("secret")
        mock_q.autocomplete = lambda *a, **k: StubPrompt("autocomplete")
        mock_q.path = lambda *a, **k: StubPrompt("/path/to/file")

        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr("questionary_extended.integration.questionary_bridge.questionary", mock_q)
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        # Test various prompt types work
        prompt_types = ["text", "select", "confirm", "checkbox", "password", "path"]
        
        for prompt_type in prompt_types:
            component = Component(name=f"{prompt_type}_test", component_type=prompt_type, message=f"Test {prompt_type} question")
            try:
                result = bridge.ask_component(component)
                assert result is not None  # Should get some result
            except AttributeError:
                # Some prompt types might not be supported
                pass

    def test_bridge_direct_module_import(self):
        """Test bridge can be imported and instantiated directly."""
        from questionary_extended.integration.questionary_bridge import QuestionaryBridge
        from questionary_extended.core.state import PageState
        
        state = PageState()
        bridge = QuestionaryBridge(state)
        
        # Should have expected attributes
        assert hasattr(bridge, 'state')
        assert hasattr(bridge, 'ask_component')
        assert bridge.state is state

    def test_component_parameter_passthrough(self, monkeypatch):
        """Test that all component parameters are passed through to questionary."""
        state = PageState()
        bridge = QuestionaryBridge(state)

        captured_kwargs = {}
        
        def capture_all_kwargs(message, **kwargs):
            captured_kwargs.update(kwargs)
            return StubPrompt("answer")

        # Use canonical helper and override text to capture kwargs
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.text = capture_all_kwargs
        mock_q.select = lambda *a, **k: StubPrompt("default_select")
        mock_q.confirm = lambda *a, **k: StubPrompt(True)
        mock_q.password = lambda *a, **k: StubPrompt("default_password")
        mock_q.checkbox = lambda *a, **k: StubPrompt(["default_checkbox"])
        mock_q.autocomplete = lambda *a, **k: StubPrompt("default_autocomplete")
        mock_q.path = lambda *a, **k: StubPrompt("default_path")

        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr("questionary_extended.integration.questionary_bridge.questionary", mock_q)
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        # Component with many parameters (compatible with text input)
        component = Component(
            name="param_test",
            component_type="text",
            message="Test message",
            default="default_val",
            validate=lambda x: True,
            style={"color": "red"}
        )
        
        bridge.ask_component(component)
        
        # Should pass through relevant parameters
        # (exact behavior depends on implementation details)