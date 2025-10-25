"""Questionary Bridge core testing - basic functionality and integration."""

import types
import pytest
from unittest.mock import MagicMock, patch

from questionary_extended.integration.questionary_bridge import QuestionaryBridge
from questionary_extended.core.component import Component
from questionary_extended.core.state import PageState
from .conftest_questionary import setup_questionary_mocks, DummyState, FakePrompt


class TestQuestionaryBridgeCore:
    """Test basic QuestionaryBridge functionality."""

    def test_ask_component_persists_answer(self, monkeypatch):
        """Test that component answers are persisted to state."""
        state = DummyState()
        bridge = QuestionaryBridge(state)

        # Setup comprehensive mocks to avoid console issues
        setup_questionary_mocks(monkeypatch, {"text": "user_answer"})

        # Create a component with a known ID
        component = Component(name="test_comp", component_type="text")

        # Ask the component
        result = bridge.ask_component(component)

        # Should return the answer and persist it
        assert result == "user_answer"
        assert state.get_all_state()["test_comp"] == "user_answer"

    def test_ask_component_with_different_prompt_types(self, monkeypatch):
        """Test asking components with different prompt types."""
        state = DummyState()
        bridge = QuestionaryBridge(state)

        # Setup mocks with specific responses for each prompt type
        mock_responses = {
            "text": "text_answer",
            "select": "select_answer", 
            "confirm": True,
            "checkbox": ["option1", "option2"]
        }
        setup_questionary_mocks(monkeypatch, mock_responses)

        # Test different component types
        text_comp = Component(name="text_comp", component_type="text")
        select_comp = Component(name="select_comp", component_type="select")
        confirm_comp = Component(name="confirm_comp", component_type="confirm")
        checkbox_comp = Component(name="checkbox_comp", component_type="checkbox")

        # Test each type
        assert bridge.ask_component(text_comp) == "text_answer"
        assert bridge.ask_component(select_comp) == "select_answer"
        assert bridge.ask_component(confirm_comp) is True
        assert bridge.ask_component(checkbox_comp) == ["option1", "option2"]

    def test_ask_component_with_message(self, monkeypatch):
        """Test that component messages are passed through correctly."""
        state = DummyState()
        bridge = QuestionaryBridge(state)

        captured_message = None
        
        def capture_text_call(message, **kwargs):
            nonlocal captured_message
            captured_message = message
            return FakePrompt("answer")

        # Use the canonical test helper so the runtime accessor is set and
        # module internals are synchronized. Then override the text factory
        # to capture the passed message.
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.text = capture_text_call
        # Ensure internal modules reference our mock as well (defensive)
        monkeypatch.setattr("questionary_extended.integration.questionary_bridge.questionary", mock_q)
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        component = Component(name="test", component_type="text", message="What is your name?")
        bridge.ask_component(component)

        assert captured_message == "What is your name?"

    def test_bridge_state_integration(self):
        """Test bridge integration with PageState."""
        state = PageState()
        bridge = QuestionaryBridge(state)
        
        # Should be able to create bridge with PageState
        assert bridge is not None
        assert bridge.state is state


class TestQuestionaryBridgeWalking:
    """Test bridge walking/traversal functionality."""

    def test_walk_components_basic(self, monkeypatch):
        """Test walking through multiple components."""
        state = DummyState()
        bridge = QuestionaryBridge(state)

        # Mock questionary to return sequential answers
        answers = ["answer1", "answer2", "answer3"]
        answer_iter = iter(answers)
        
        def make_prompt(*args, **kwargs):
            return FakePrompt(next(answer_iter))

        # Use the canonical helper so the runtime accessor is set and
        # synchronized across internals; then set the text factory to our
        # sequential prompt generator.
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.text = make_prompt
        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr("questionary_extended.integration.questionary_bridge.questionary", mock_q)
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        # Create components to walk (add required message parameter)
        components = [
            Component(name="comp1", component_type="text", message="Question 1"),
            Component(name="comp2", component_type="text", message="Question 2"),
            Component(name="comp3", component_type="text", message="Question 3")
        ]

        # Walk through components
        results = []
        for comp in components:
            result = bridge.ask_component(comp)
            results.append(result)

        assert results == ["answer1", "answer2", "answer3"]
        
        # All answers should be persisted
        final_state = state.get_all_state()
        assert final_state["comp1"] == "answer1"
        assert final_state["comp2"] == "answer2"
        assert final_state["comp3"] == "answer3"

    def test_run_workflow_pattern(self, monkeypatch):
        """Test running a workflow of components."""
        state = DummyState()
        bridge = QuestionaryBridge(state)

        # Mock questionary responses
        responses = {"name": "John", "age": "25", "confirm": True}
        
        def make_prompt_factory(prompt_type):
            def prompt_func(*args, **kwargs):
                if prompt_type == "text":
                    # Return appropriate response based on message
                    message = ""
                    if args:
                        message = args[0]
                    elif 'message' in kwargs:
                        message = kwargs['message']
                    
                    if "name" in message.lower():
                        return FakePrompt("John")
                    elif "age" in message.lower():
                        return FakePrompt("25")
                elif prompt_type == "confirm":
                    return FakePrompt(True)
                return FakePrompt("default")
            return prompt_func

        # Use the canonical helper so the runtime accessor is set and
        # synchronized across internals. Wire up the factories created by
        # make_prompt_factory to the runtime mock.
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.text = make_prompt_factory("text")
        mock_q.confirm = make_prompt_factory("confirm")
        mock_q.select = lambda *a, **k: FakePrompt("default_select")
        mock_q.password = lambda *a, **k: FakePrompt("default_password")
        mock_q.checkbox = lambda *a, **k: FakePrompt(["default_checkbox"])
        mock_q.autocomplete = lambda *a, **k: FakePrompt("default_autocomplete")
        mock_q.path = lambda *a, **k: FakePrompt("default_path")

        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr("questionary_extended.integration.questionary_bridge.questionary", mock_q)
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        # Simulate workflow
        name_comp = Component(name="name", component_type="text", message="What's your name?")
        age_comp = Component(name="age", component_type="text", message="What's your age?")
        confirm_comp = Component(name="confirm", component_type="confirm", message="Is this correct?")

        workflow = [name_comp, age_comp, confirm_comp]
        
        results = []
        for comp in workflow:
            result = bridge.ask_component(comp)
            results.append(result)

        assert results == ["John", "25", True]


class TestQuestionaryBridgeOptions:
    """Test bridge handling of component options and parameters."""

    def test_component_with_choices(self, monkeypatch):
        """Test component with predefined choices."""
        state = DummyState()
        bridge = QuestionaryBridge(state)

        captured_choices = None
        
        def capture_select_call(message, choices=None, **kwargs):
            nonlocal captured_choices
            captured_choices = choices
            return FakePrompt("choice1")

        # Use the canonical helper so runtime accessor and module internals
        # are synchronized; then override the select factory to capture
        # the choices passed in.
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.select = capture_select_call
        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr("questionary_extended.integration.questionary_bridge.questionary", mock_q)
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        component = Component(
            name="select_test",
            component_type="select",
            message="Choose one:",
            choices=["choice1", "choice2", "choice3"]
        )
        
        result = bridge.ask_component(component)
        
        assert result == "choice1"
        assert captured_choices == ["choice1", "choice2", "choice3"]

    def test_component_with_default_value(self, monkeypatch):
        """Test component with default value."""
        state = DummyState()
        bridge = QuestionaryBridge(state)

        captured_default = None
        
        def capture_text_call(message, default=None, **kwargs):
            nonlocal captured_default
            captured_default = default
            return FakePrompt("user_input")

        # Use the canonical helper to install a stable questionary mock and
        # then override the text factory to capture the default kwarg.
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.text = capture_text_call
        mock_q.select = lambda *a, **k: FakePrompt("default_select")
        mock_q.confirm = lambda *a, **k: FakePrompt(True)
        mock_q.password = lambda *a, **k: FakePrompt("default_password")
        mock_q.checkbox = lambda *a, **k: FakePrompt(["default_checkbox"])
        mock_q.autocomplete = lambda *a, **k: FakePrompt("default_autocomplete")
        mock_q.path = lambda *a, **k: FakePrompt("default_path")

        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr("questionary_extended.integration.questionary_bridge.questionary", mock_q)
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        component = Component(
            name="default_test",
            component_type="text",
            message="Enter value:",
            default="default_value"
        )
        
        bridge.ask_component(component)
        
        assert captured_default == "default_value"

    def test_component_with_validation(self, monkeypatch):
        """Test component with validation function."""
        state = DummyState()
        bridge = QuestionaryBridge(state)

        captured_validate = None
        
        def capture_text_call(message, validate=None, **kwargs):
            nonlocal captured_validate
            captured_validate = validate
            return FakePrompt("valid_input")

        # Use the canonical helper to install a stable questionary mock and
        # then override the text factory to capture the validate kwarg.
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.text = capture_text_call
        mock_q.select = lambda *a, **k: FakePrompt("default_select")
        mock_q.confirm = lambda *a, **k: FakePrompt(True)
        mock_q.password = lambda *a, **k: FakePrompt("default_password")
        mock_q.checkbox = lambda *a, **k: FakePrompt(["default_checkbox"])
        mock_q.autocomplete = lambda *a, **k: FakePrompt("default_autocomplete")
        mock_q.path = lambda *a, **k: FakePrompt("default_path")

        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr("questionary_extended.integration.questionary_bridge.questionary", mock_q)
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        def validator(text):
            return len(text) > 0

        component = Component(
            name="validate_test",
            component_type="text",
            message="Enter value:",
            validate=validator
        )
        
        bridge.ask_component(component)
        
        # Should pass validator function through
        assert captured_validate is validator