# DI Interface Usage Examples

## Complete Working Examples

### 1. Basic Component Usage (Production)

```python
# Production code - no changes needed
from src.tui_engine.component import Component

component = Component()
result = component.create_questionary_component(
    "What's your name?", 
    type="text"
)
# Uses default questionary import via DI system
```

### 2. Simple Test with DI

```python
# tests/test_component_simple.py
from unittest.mock import MagicMock
from src.tui_engine.component import Component
from src.tui_engine.questionary_factory import set_questionary_factory, clear_questionary_factory

def test_component_with_di():
    # Setup: Create mock questionary
    mock_questionary = MagicMock()
    mock_text_component = MagicMock()
    mock_questionary.text = MagicMock(return_value=mock_text_component)
    
    # Inject dependency
    set_questionary_factory(lambda: mock_questionary)
    
    try:
        # Test
        component = Component()
        result = component.create_questionary_component("test prompt", type="text")
        
        # Verify
        assert result == mock_text_component
        mock_questionary.text.assert_called_once_with("test prompt", type="text")
    finally:
        # Cleanup
        clear_questionary_factory()
```

### 3. Context Manager Test Helper

```python
# tests/questionary_helpers.py
import pytest
from contextlib import contextmanager
from unittest.mock import MagicMock
from src.tui_engine.questionary_factory import set_questionary_factory, clear_questionary_factory

@contextmanager
def mock_questionary():
    """Context manager for clean questionary mocking."""
    mock = MagicMock()
    set_questionary_factory(lambda: mock)
    try:
        yield mock
    finally:
        clear_questionary_factory()

# Usage in tests:
def test_with_context_manager():
    with mock_questionary() as mock_q:
        mock_q.select.return_value = MagicMock()
        
        component = Component()
        result = component.create_questionary_component(
            "Choose option:", 
            type="select",
            choices=["A", "B", "C"]
        )
        
        mock_q.select.assert_called_once_with(
            "Choose option:",
            type="select", 
            choices=["A", "B", "C"]
        )
```

### 4. Pytest Fixture Approach

```python
# tests/conftest.py
import pytest
from unittest.mock import MagicMock
from src.tui_engine.questionary_factory import set_questionary_factory, clear_questionary_factory

@pytest.fixture
def mock_questionary():
    """Pytest fixture for questionary mocking."""
    mock = MagicMock()
    set_questionary_factory(lambda: mock)
    yield mock
    clear_questionary_factory()

# Usage:
def test_with_fixture(mock_questionary):
    mock_questionary.confirm.return_value = MagicMock()
    
    component = Component()
    result = component.create_questionary_component("Continue?", type="confirm")
    
    mock_questionary.confirm.assert_called_once()
```

### 5. Advanced Test Scenario

```python
# tests/test_component_advanced.py
def test_multiple_component_types():
    """Test that demonstrates clean testing of multiple questionary types."""
    with mock_questionary() as mock_q:
        # Setup different component types
        mock_q.text.return_value = "text_result"
        mock_q.select.return_value = "select_result"
        mock_q.confirm.return_value = True
        
        component = Component()
        
        # Test text component
        text_result = component.create_questionary_component("Name?", type="text")
        assert text_result == "text_result"
        
        # Test select component
        select_result = component.create_questionary_component(
            "Choose:", 
            type="select", 
            choices=["A", "B"]
        )
        assert select_result == "select_result"
        
        # Test confirm component
        confirm_result = component.create_questionary_component("OK?", type="confirm")
        assert confirm_result is True
        
        # Verify all calls made correctly
        mock_q.text.assert_called_with("Name?", type="text")
        mock_q.select.assert_called_with("Choose:", type="select", choices=["A", "B"])
        mock_q.confirm.assert_called_with("OK?", type="confirm")
```

## Migration Examples

### Before (Current Complex Pattern):

```python
# Current test pattern - COMPLEX
def test_current_complex():
    mock_questionary = MagicMock()
    
    # Complex setup with multiple monkeypatch operations
    monkeypatch.setattr(sys.modules, 'questionary', mock_questionary)
    monkeypatch.setattr('questionary.text', mock_questionary.text)
    
    # Setup runtime mocking
    mock_runtime = MagicMock()
    mock_runtime.get_questionary_module.return_value = mock_questionary
    
    # More complex setup...
    setup_questionary_mocks(monkeypatch, mock_questionary)
    
    # Test logic buried in setup complexity
    component = Component()
    component._runtime = mock_runtime
    result = component.create_questionary_component("test")
    
    # Complex verification
```

### After (Simple DI Pattern):

```python
# New test pattern - SIMPLE
def test_new_simple():
    with mock_questionary() as mock_q:
        mock_q.text.return_value = "expected_result"
        
        component = Component()
        result = component.create_questionary_component("test", type="text")
        
        assert result == "expected_result"
        mock_q.text.assert_called_once_with("test", type="text")
```

## Error Handling Examples

### DI Error Scenarios:

```python
def test_invalid_component_type():
    """Test error handling with DI."""
    with mock_questionary() as mock_q:
        # Don't setup the requested component type
        component = Component()
        
        with pytest.raises(ValueError, match="Unknown questionary component type: invalid"):
            component.create_questionary_component("test", type="invalid")

def test_factory_exception():
    """Test handling of factory exceptions."""
    def failing_factory():
        raise ImportError("Mock import failure")
    
    set_questionary_factory(failing_factory)
    
    try:
        component = Component()
        with pytest.raises(ImportError):
            component.create_questionary_component("test")
    finally:
        clear_questionary_factory()
```

## Integration Test Examples

### Real Questionary Integration:

```python
def test_real_questionary_integration():
    """Test with real questionary module to ensure compatibility."""
    # No DI setup - uses default real questionary
    
    component = Component()
    
    # This would work with real questionary in interactive environment
    # For automated tests, we'd mock the actual interaction
    import questionary
    original_text = questionary.text
    
    try:
        # Mock just the interactive part
        questionary.text = MagicMock(return_value="mocked_interaction")
        
        result = component.create_questionary_component("test", type="text")
        assert result == "mocked_interaction"
        
    finally:
        questionary.text = original_text
```

## Performance Comparison

### Before (Multiple Fallbacks):
```python
# Each component creation does:
# 1. Check runtime accessor
# 2. Check sys.modules
# 3. Check globals()
# 4. Direct import
# = 4 operations per component
```

### After (Single Factory Lookup):
```python
# Each component creation does:
# 1. Factory lookup (cached)
# = 1 operation per component
```

This design provides clear, simple patterns that any Python developer can understand and maintain, eliminating the unusual complexity of the current system.