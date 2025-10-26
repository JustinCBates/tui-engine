"""
Test helpers for clean questionary dependency injection.

This module provides clean, simple testing patterns for questionary components,
replacing the complex mocking patterns with standard Python dependency injection.

Key features:
- Context manager for automatic cleanup
- Pytest fixtures for broader test scenarios  
- Pre-configured mock setups for common use cases
- Clear separation between test setup and test logic

Example usage:
    # Simple context manager
    with mock_questionary() as mock_q:
        mock_q.text.return_value = "test_result"
        # ... test code
    
    # Pytest fixture
    def test_something(mock_questionary_fixture):
        mock_questionary_fixture.select.return_value = "selected"
        # ... test code
"""

import pytest
from contextlib import contextmanager
from unittest.mock import MagicMock, Mock
from typing import Any, Dict, Optional, Iterator

from src.tui_engine.questionary_factory import (
    set_questionary_factory, 
    clear_questionary_factory,
    QuestionaryModule
)


@contextmanager
def mock_questionary(
    configured_methods: Optional[Dict[str, Any]] = None
) -> Iterator[MagicMock]:
    """
    Context manager for clean questionary mocking with automatic cleanup.
    
    This provides the cleanest way to mock questionary in tests. It automatically
    handles setup and cleanup, ensuring tests don't interfere with each other.
    
    Args:
        configured_methods: Optional dict of method_name -> return_value pairs
                          for pre-configuring common questionary methods
    
    Yields:
        MagicMock: A mock questionary module with configured methods
        
    Example:
        # Basic usage
        with mock_questionary() as mock_q:
            mock_q.text.return_value = "user_input"
            # ... test code using questionary
            
        # Pre-configured methods
        with mock_questionary({"text": "default_text", "confirm": True}) as mock_q:
            # mock_q.text() will return "default_text"
            # mock_q.confirm() will return True
    """
    mock = MagicMock()
    
    # Configure any specified methods
    if configured_methods:
        for method_name, return_value in configured_methods.items():
            # Create a mock that returns a questionary-like object with ask() method
            questionary_obj = Mock()
            questionary_obj.ask.return_value = return_value
            if hasattr(mock, method_name):
                getattr(mock, method_name).return_value = questionary_obj
            else:
                setattr(mock, method_name, Mock(return_value=questionary_obj))
    
    # Inject the mock
    set_questionary_factory(lambda: mock)
    
    try:
        yield mock
    finally:
        # Always clean up, even if test fails
        clear_questionary_factory()


@pytest.fixture
def mock_questionary_fixture() -> Iterator[MagicMock]:
    """
    Pytest fixture for questionary mocking.
    
    This provides a pytest fixture that can be used across multiple test methods
    or when you need the mock to persist across multiple operations in a test.
    
    Yields:
        MagicMock: A mock questionary module
        
    Example:
        def test_component_creation(mock_questionary_fixture):
            mock_questionary_fixture.text.return_value = "test_input"
            
            component = Component()
            result = component.create_questionary_component("prompt", type="text")
            
            assert result == "test_input"
            mock_questionary_fixture.text.assert_called_once()
    """
    mock = MagicMock()
    set_questionary_factory(lambda: mock)
    
    yield mock
    
    # Cleanup after test
    clear_questionary_factory()


@contextmanager
def mock_questionary_with_types(**type_configs: Any) -> Iterator[MagicMock]:
    """
    Context manager for mocking specific questionary component types.
    
    This is a convenience wrapper that pre-configures common questionary
    component types (text, select, confirm, etc.) with their return values.
    
    Args:
        **type_configs: Keyword arguments where keys are questionary component
                       types and values are their return values
    
    Yields:
        MagicMock: A mock questionary module with configured component types
        
    Example:
        with mock_questionary_with_types(
            text="user_name",
            select="option_1", 
            confirm=True
        ) as mock_q:
            # mock_q.text() returns "user_name"
            # mock_q.select() returns "option_1"  
            # mock_q.confirm() returns True
    """
    mock = MagicMock()
    
    # Configure each questionary component type
    for component_type, return_value in type_configs.items():
        # Create a mock that returns a questionary-like object with ask() method
        questionary_obj = Mock()
        questionary_obj.ask.return_value = return_value
        component_mock = Mock(return_value=questionary_obj)
        setattr(mock, component_type, component_mock)
    
    set_questionary_factory(lambda: mock)
    
    try:
        yield mock
    finally:
        clear_questionary_factory()


class QuestionaryTestHelper:
    """
    Advanced test helper class for complex questionary testing scenarios.
    
    This class provides more advanced testing capabilities for cases where
    you need fine-grained control over questionary behavior or need to
    simulate complex interaction patterns.
    """
    
    def __init__(self):
        self.mock = MagicMock()
        self._active = False
    
    def __enter__(self):
        """Enter context manager."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager with cleanup."""
        self.stop()
    
    def start(self) -> None:
        """Start using this helper's mock."""
        if self._active:
            raise RuntimeError("QuestionaryTestHelper is already active")
        
        set_questionary_factory(lambda: self.mock)
        self._active = True
    
    def stop(self) -> None:
        """Stop using this helper's mock and cleanup."""
        if self._active:
            clear_questionary_factory()
            self._active = False
    
    def configure_component(self, component_type: str, return_value: Any) -> Mock:
        """
        Configure a specific questionary component type.
        
        Args:
            component_type: The questionary component type (text, select, etc.)
            return_value: What the component should return when called
            
        Returns:
            Mock: The mock object for the component (for further configuration)
        """
        component_mock = Mock(return_value=return_value)
        component_mock._configured_by_helper = True  # Mark as configured
        setattr(self.mock, component_type, component_mock)
        return component_mock
    
    def simulate_user_input_sequence(self, inputs: Dict[str, Any]) -> None:
        """
        Simulate a sequence of user inputs for different component types.
        
        Args:
            inputs: Dict mapping component types to their simulated return values
        """
        for component_type, return_value in inputs.items():
            self.configure_component(component_type, return_value)
    
    def assert_component_called(self, component_type: str, *args, **kwargs) -> None:
        """
        Assert that a specific questionary component was called with expected args.
        
        Args:
            component_type: The questionary component type to check
            *args, **kwargs: Expected call arguments
        """
        # Check if component was explicitly configured by us
        configured_components = [name for name, obj in self.mock._mock_children.items() 
                               if hasattr(obj, '_configured_by_helper')]
        
        if component_type not in configured_components:
            raise AssertionError(f"Component type '{component_type}' was never configured")
        
        component_mock = getattr(self.mock, component_type)
        if args or kwargs:
            component_mock.assert_called_with(*args, **kwargs)
        else:
            component_mock.assert_called()
    
    def get_component_calls(self, component_type: str) -> list:
        """
        Get all calls made to a specific questionary component.
        
        Args:
            component_type: The questionary component type to check
            
        Returns:
            list: List of call objects for the component
        """
        if not hasattr(self.mock, component_type):
            return []
        
        component_mock = getattr(self.mock, component_type)
        return component_mock.call_args_list


# Convenience aliases for common patterns
simple_mock = mock_questionary
typed_mock = mock_questionary_with_types
advanced_mock = QuestionaryTestHelper


@contextmanager
def mock_cli_questionary(**sequential_configs: Any) -> Iterator[MagicMock]:
    """
    Context manager for mocking questionary at CLI module level.
    
    This is specifically designed for CLI tests that need to mock questionary
    imports at the module level, supporting sequential responses for complex
    interaction flows.
    
    Args:
        **sequential_configs: Keyword arguments where keys are questionary 
                             component types and values are lists of sequential
                             return values or single values
                             
    Yields:
        MagicMock: A mock questionary module with configured sequential responses
        
    Example:
        with mock_cli_questionary(
            confirm=[True, False],  # First confirm True, second False
            text=["field1", "Enter text"],  # Sequential text responses
            select="option1"  # Single select response
        ) as mock_q:
            # CLI code using questionary will get these responses
    """
    mock = MagicMock()
    
    def make_sequential_factory(values):
        """Create factory for sequential prompt responses."""
        if not isinstance(values, (list, tuple)):
            values = [values]
        it = iter(values)
        
        class FakePrompt:
            def ask(self):
                try:
                    return next(it)
                except StopIteration:
                    # Return the last value for any additional calls
                    return values[-1] if values else None
        
        return lambda *args, **kwargs: FakePrompt()
    
    # Configure each questionary component type
    for component_type, return_values in sequential_configs.items():
        setattr(mock, component_type, make_sequential_factory(return_values))
    
    # Set up the questionary factory for DI system compatibility
    set_questionary_factory(lambda: mock)
    
    try:
        yield mock
    finally:
        clear_questionary_factory()


__all__ = [
    'mock_questionary',
    'mock_questionary_fixture', 
    'mock_questionary_with_types',
    'mock_cli_questionary',
    'QuestionaryTestHelper',
    'simple_mock',
    'typed_mock', 
    'advanced_mock'
]