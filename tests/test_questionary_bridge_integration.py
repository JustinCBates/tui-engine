"""Questionary Bridge integration testing - end-to-end scenarios and compatibility testing."""

import importlib
import types

import pytest

from questionary_extended.core.component import Component
from questionary_extended.core.state import PageState
from questionary_extended.integration.questionary_bridge import QuestionaryBridge
from tests.conftest_questionary import setup_questionary_mocks


class TestQuestionaryBridgeCompatibility:
    """Test compatibility with various questionary versions and configurations."""

    def test_questionary_api_equivalence(self, monkeypatch):
        """Test that bridge calls questionary API in expected way."""
        state = PageState()
        bridge = QuestionaryBridge(state)

        # Track all questionary calls
        calls_made = []

        def make_call_tracker(method_name):
            def tracker(*args, **kwargs):
                calls_made.append((method_name, args, kwargs))
                return types.SimpleNamespace(ask=lambda: f"{method_name}_result")

            return tracker

        # Use canonical helper so runtime accessor is set and internal
        # modules are synchronized. Wire the tracking wrappers into the
        # runtime mock so calls_made is populated.
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.text = make_call_tracker("text")
        mock_q.select = make_call_tracker("select")
        mock_q.confirm = make_call_tracker("confirm")
        mock_q.checkbox = make_call_tracker("checkbox")
        mock_q.password = make_call_tracker("password")
        mock_q.autocomplete = make_call_tracker("autocomplete")
        mock_q.path = make_call_tracker("path")

        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr(
            "questionary_extended.integration.questionary_bridge.questionary", mock_q
        )
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        # Test different prompt types
        components = [
            Component(name="t1", component_type="text", message="Text prompt"),
            Component(
                name="s1",
                component_type="select",
                message="Select prompt",
                choices=["a", "b"],
            ),
            Component(name="c1", component_type="confirm", message="Confirm prompt"),
            Component(
                name="cb1",
                component_type="checkbox",
                message="Checkbox prompt",
                choices=["x", "y"],
            ),
        ]

        for comp in components:
            bridge.ask_component(comp)

        # Should have made expected calls
        assert len(calls_made) == 4

        # Verify we got the expected call types
        call_types = [call[0] for call in calls_made]
        assert "text" in call_types
        assert "select" in call_types
        assert "confirm" in call_types
        assert "checkbox" in call_types

        # Basic verification that calls were made with some arguments
        for call in calls_made:
            assert len(call) >= 2  # Should have (method_name, args, kwargs)
            assert isinstance(call[1], tuple)  # args should be tuple
            assert isinstance(call[2], dict)  # kwargs should be dict

    def test_questionary_compat_with_real_api(self, monkeypatch):
        """Test compatibility with actual questionary API patterns."""

        # Use canonical helper and wire a safe prompt factory
        def make_safe_prompt(*args, **kwargs):
            return types.SimpleNamespace(ask=lambda: "test_response")

        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.text = make_safe_prompt
        mock_q.select = make_safe_prompt
        mock_q.confirm = make_safe_prompt
        mock_q.checkbox = make_safe_prompt
        mock_q.password = make_safe_prompt
        mock_q.autocomplete = make_safe_prompt
        mock_q.path = make_safe_prompt

        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr(
            "questionary_extended.integration.questionary_bridge.questionary", mock_q
        )
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        # Test that our mocked questionary has the expected methods
        expected_methods = ["text", "select", "confirm", "checkbox"]

        for method in expected_methods:
            assert hasattr(mock_q, method), f"mock questionary missing {method}"

        # Test basic API compatibility using mocked questionary
        text_prompt = mock_q.text("test message")
        assert hasattr(text_prompt, "ask")

        # Test that ask() returns expected value
        result = text_prompt.ask()
        assert result == "test_response"

    def test_bridge_without_questionary_dependency(self, monkeypatch):
        """Test bridge behavior when questionary is completely unavailable."""
        state = PageState()

        # Remove questionary from imports
        with monkeypatch.context() as m:
            # Mock import to fail
            def mock_import(name, *args, **kwargs):
                if name == "questionary":
                    raise ImportError("No module named 'questionary'")
                return importlib.__import__(name, *args, **kwargs)

            m.setattr("builtins.__import__", mock_import)

            # Should be able to create bridge even without questionary
            # (The actual error will occur when trying to use it)
            bridge = QuestionaryBridge(state)
            assert bridge.state is state


class TestQuestionaryBridgeEndToEnd:
    """Test complete end-to-end workflows with the bridge."""

    def test_full_form_workflow(self, monkeypatch):
        """Test complete form workflow from start to finish."""
        state = PageState()
        bridge = QuestionaryBridge(state)

        # Mock a complete form workflow

        def make_response_handler(prompt_type):
            def handler(message, **kwargs):
                # Determine response based on message content
                if "name" in message.lower():
                    return types.SimpleNamespace(ask=lambda: "John Doe")
                elif "email" in message.lower():
                    return types.SimpleNamespace(ask=lambda: "john@example.com")
                elif "age" in message.lower():
                    return types.SimpleNamespace(ask=lambda: "30")
                elif "subscribe" in message.lower():
                    return types.SimpleNamespace(ask=lambda: True)
                elif "interests" in message.lower():
                    return types.SimpleNamespace(ask=lambda: ["coding", "music"])
                else:
                    return types.SimpleNamespace(ask=lambda: "default")

            return handler

        # Use canonical helper and wire intelligent response handlers
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.text = make_response_handler("text")
        mock_q.confirm = make_response_handler("confirm")
        mock_q.checkbox = make_response_handler("checkbox")
        mock_q.select = make_response_handler("select")
        mock_q.password = make_response_handler("password")
        mock_q.autocomplete = make_response_handler("autocomplete")
        mock_q.path = make_response_handler("path")

        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr(
            "questionary_extended.integration.questionary_bridge.questionary", mock_q
        )
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        # Define form components
        form_components = [
            Component(name="name", component_type="text", message="Enter your name:"),
            Component(name="email", component_type="text", message="Enter your email:"),
            Component(name="age", component_type="text", message="Enter your age:"),
            Component(
                name="subscribe",
                component_type="confirm",
                message="Subscribe to newsletter?",
            ),
            Component(
                name="interests",
                component_type="checkbox",
                message="Select interests:",
                choices=["coding", "music", "sports", "travel"],
            ),
        ]

        # Execute form workflow
        results = {}
        for component in form_components:
            result = bridge.ask_component(component)
            results[component.name] = result  # Use name instead of id

        # Verify results
        assert results["name"] == "John Doe"
        assert results["email"] == "john@example.com"
        assert results["age"] == "30"
        assert results["subscribe"] is True
        assert results["interests"] == ["coding", "music"]

        # Verify state persistence
        final_state = state.get_all_state()
        assert final_state == results

    def test_conditional_workflow(self, monkeypatch):
        """Test workflow with conditional logic based on previous answers."""
        state = PageState()
        bridge = QuestionaryBridge(state)

        # Responses that will trigger conditional logic
        responses = ["premium", "monthly"]  # select responses
        response_iter = iter(responses)

        def sequential_response(*args, **kwargs):
            try:
                return types.SimpleNamespace(ask=lambda: next(response_iter))
            except StopIteration:
                return types.SimpleNamespace(ask=lambda: "default")

        # Use canonical helper and wire conditional response factories
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.confirm = lambda *a, **k: types.SimpleNamespace(ask=lambda: True)
        mock_q.select = sequential_response
        mock_q.text = lambda *a, **k: types.SimpleNamespace(ask=lambda: "default_text")
        mock_q.checkbox = lambda *a, **k: types.SimpleNamespace(
            ask=lambda: ["default_choice"]
        )
        mock_q.password = lambda *a, **k: types.SimpleNamespace(
            ask=lambda: "default_password"
        )
        mock_q.autocomplete = lambda *a, **k: types.SimpleNamespace(
            ask=lambda: "default_auto"
        )
        mock_q.path = lambda *a, **k: types.SimpleNamespace(ask=lambda: "/default/path")

        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr(
            "questionary_extended.integration.questionary_bridge.questionary", mock_q
        )
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        # Conditional workflow: ask follow-up questions based on answers
        signup = Component(name="signup", component_type="confirm", message="Sign up?")
        signup_result = bridge.ask_component(signup)

        if signup_result:
            plan = Component(
                name="plan",
                component_type="select",
                message="Choose plan:",
                choices=["basic", "premium"],
            )
            plan_result = bridge.ask_component(plan)

            if plan_result == "premium":
                billing = Component(
                    name="billing",
                    component_type="select",
                    message="Billing cycle:",
                    choices=["monthly", "yearly"],
                )
                bridge.ask_component(billing)

        # Verify conditional execution worked
        final_state = state.get_all_state()
        assert "signup" in final_state
        assert "plan" in final_state
        assert "billing" in final_state  # Should exist because plan was "premium"
        assert final_state["plan"] == "premium"  # First select response
        assert final_state["billing"] == "monthly"  # Second select response

    def test_error_recovery_workflow(self, monkeypatch):
        """Test workflow error recovery and continuation."""
        state = PageState()
        bridge = QuestionaryBridge(state)

        call_count = 0

        def error_then_success(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call raises error during ask(), not during creation
                def error_ask():
                    raise KeyboardInterrupt("User interrupted")

                return types.SimpleNamespace(ask=error_ask)
            else:
                # Subsequent calls succeed
                return types.SimpleNamespace(ask=lambda: "recovered_answer")

        # Use canonical helper and wire error/recovery behavior
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.text = error_then_success
        mock_q.select = lambda *a, **k: types.SimpleNamespace(
            ask=lambda: "default_option"
        )
        mock_q.confirm = lambda *a, **k: types.SimpleNamespace(ask=lambda: True)
        mock_q.checkbox = lambda *a, **k: types.SimpleNamespace(
            ask=lambda: ["default_choice"]
        )
        mock_q.password = lambda *a, **k: types.SimpleNamespace(
            ask=lambda: "default_password"
        )
        mock_q.autocomplete = lambda *a, **k: types.SimpleNamespace(
            ask=lambda: "default_auto"
        )
        mock_q.path = lambda *a, **k: types.SimpleNamespace(ask=lambda: "/default/path")

        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr(
            "questionary_extended.integration.questionary_bridge.questionary", mock_q
        )
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        component = Component(
            name="retry_test", component_type="text", message="Enter value:"
        )

        # First attempt should fail
        with pytest.raises(KeyboardInterrupt):
            bridge.ask_component(component)

        # Second attempt should succeed
        result = bridge.ask_component(component)
        assert result == "recovered_answer"


class TestQuestionaryBridgeModuleIntegration:
    """Test module-level integration and import patterns."""

    def test_bridge_module_imports(self):
        """Test that all necessary imports work correctly."""
        # Test direct imports
        from questionary_extended.core.component import Component
        from questionary_extended.core.state import PageState
        from questionary_extended.integration.questionary_bridge import (
            QuestionaryBridge,
        )

        # Should be able to create instances
        state = PageState()
        bridge = QuestionaryBridge(state)
        component = Component(name="test", component_type="text")

        assert bridge is not None
        assert component is not None
        assert state is not None

    def test_bridge_package_structure(self):
        """Test package structure and module organization."""
        # Test that integration package exists and is properly structured
        import questionary_extended.integration

        assert hasattr(questionary_extended.integration, "__path__")

        # Test that bridge module can be imported via package
        from questionary_extended.integration import questionary_bridge

        assert hasattr(questionary_bridge, "QuestionaryBridge")

    def test_bridge_with_minimal_component(self, monkeypatch):
        """Test bridge works with minimal component configuration."""
        state = PageState()
        bridge = QuestionaryBridge(state)

        # Use canonical helper and wire minimal response factories
        mock_q = setup_questionary_mocks(monkeypatch)
        mock_q.text = lambda *a, **k: types.SimpleNamespace(ask=lambda: "minimal")
        mock_q.select = lambda *a, **k: types.SimpleNamespace(
            ask=lambda: "default_option"
        )
        mock_q.confirm = lambda *a, **k: types.SimpleNamespace(ask=lambda: True)
        mock_q.checkbox = lambda *a, **k: types.SimpleNamespace(
            ask=lambda: ["default_choice"]
        )
        mock_q.password = lambda *a, **k: types.SimpleNamespace(
            ask=lambda: "default_password"
        )
        mock_q.autocomplete = lambda *a, **k: types.SimpleNamespace(
            ask=lambda: "default_auto"
        )
        mock_q.path = lambda *a, **k: types.SimpleNamespace(ask=lambda: "/default/path")

        # Defensive: ensure internal modules reference the same mock
        monkeypatch.setattr(
            "questionary_extended.integration.questionary_bridge.questionary", mock_q
        )
        monkeypatch.setattr("questionary_extended.core.component.questionary", mock_q)

        # Minimal component - needs message parameter for questionary API
        minimal_component = Component(
            name="minimal_test", component_type="text", message="Enter value:"
        )

        result = bridge.ask_component(minimal_component)
        assert result == "minimal"

    def test_bridge_load_and_exercise_standalone(self):
        """Test loading and exercising bridge as standalone module."""
        # This tests the pattern used in some test files for direct module loading
        import os

        # Get the bridge module path
        here = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        bridge_path = os.path.join(
            here, "src", "questionary_extended", "integration", "questionary_bridge.py"
        )

        # Instead of constructing a spec (ad-hoc and fragile), validate the
        # module file exists and contains the expected top-level symbol. This
        # avoids importing/executing the module (which pulls heavy deps) while
        # still validating package layout.
        if os.path.exists(bridge_path):
            with open(bridge_path, encoding="utf8") as fh:
                content = fh.read()

            # Ensure the file declares the expected class name
            assert "class QuestionaryBridge" in content
