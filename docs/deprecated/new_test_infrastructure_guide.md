# New Test Infrastructure Documentation

## Overview

This document describes the new simplified test infrastructure using dependency injection (DI) patterns to replace the complex questionary mocking system.

## Test Helper Reference

### Core Helpers

#### 1. `mock_questionary()` - Basic Context Manager

**Purpose**: Simple, clean mocking for most test scenarios.

```python
from tests.helpers.questionary_helpers import mock_questionary

def test_basic_component():
    with mock_questionary() as mock_q:
        # Configure mock behavior
        mock_q.text.return_value = "user_input"
        
        # Test logic
        component = Component("name", "text")
        result = component.create_questionary_component()
        
        # Verify results
        assert result == "user_input"
        mock_q.text.assert_called_once_with("name")
```

**When to use**: 
- Basic component testing
- Single component type tests
- Simple mock configuration needs

#### 2. `mock_questionary_with_types()` - Pre-configured Types

**Purpose**: Convenient setup for tests using multiple questionary component types.

```python
from tests.helpers.questionary_helpers import mock_questionary_with_types

def test_multiple_components():
    with mock_questionary_with_types(
        text="user_name",
        select="option_1",
        confirm=True
    ) as mock_q:
        # All types pre-configured
        text_comp = Component("name", "text")
        select_comp = Component("choice", "select", choices=["A", "B"])
        confirm_comp = Component("ok", "confirm")
        
        # Test logic
        name_result = text_comp.create_questionary_component()
        choice_result = select_comp.create_questionary_component()
        ok_result = confirm_comp.create_questionary_component()
        
        # Verify
        assert name_result == "user_name"
        assert choice_result == "option_1"
        assert ok_result is True
```

**When to use**:
- CLI tests with multiple interaction types
- Integration tests
- Tests with predictable interaction sequences

#### 3. `QuestionaryTestHelper` - Advanced Scenarios

**Purpose**: Full control for complex testing scenarios.

```python
from tests.helpers.questionary_helpers import QuestionaryTestHelper

def test_complex_interaction():
    with QuestionaryTestHelper() as helper:
        # Advanced configuration
        text_mock = helper.configure_component("text", "user_input")
        helper.configure_component("confirm", True)
        
        # Simulate user interaction sequence
        helper.simulate_user_input_sequence({
            "text": "project_name",
            "select": "python",
            "confirm": True
        })
        
        # Test logic
        result = run_complex_workflow()
        
        # Advanced verification
        helper.assert_component_called("text")
        calls = helper.get_component_calls("text")
        assert len(calls) == 1
```

**When to use**:
- Complex CLI workflows
- Multi-step interactions
- Advanced call verification needs
- Custom interaction patterns

#### 4. `mock_questionary_fixture` - Pytest Fixture

**Purpose**: Pytest fixture for tests that need questionary mocking across multiple operations.

```python
def test_with_fixture(mock_questionary_fixture):
    # Configure fixture
    mock_questionary_fixture.text.return_value = "result"
    mock_questionary_fixture.confirm.return_value = True
    
    # Test multiple operations
    comp1 = Component("input", "text")
    comp2 = Component("proceed", "confirm")
    
    result1 = comp1.create_questionary_component()
    result2 = comp2.create_questionary_component()
    
    # Verify
    assert result1 == "result"
    assert result2 is True
    mock_questionary_fixture.text.assert_called_once()
    mock_questionary_fixture.confirm.assert_called_once()
```

**When to use**:
- Tests with multiple component operations
- When you need the mock to persist across test methods
- Integration with existing pytest fixture patterns

## Migration Workflow

### Step 1: Identify Current Pattern

Look for these patterns in existing tests:
```python
# Complex patterns to replace:
monkeypatch.setattr(questionary, "text", fake_function)
setup_questionary_mocks(monkeypatch)
sys.modules["questionary"] = mock_questionary
```

### Step 2: Choose Appropriate Helper

| Current Pattern | Recommended Helper | Reason |
|----------------|-------------------|---------|
| Single `monkeypatch.setattr()` | `mock_questionary()` | Simple 1:1 replacement |
| Multiple `monkeypatch.setattr()` | `mock_questionary_with_types()` | Pre-configure all types |
| Complex CLI interactions | `QuestionaryTestHelper` | Advanced control needed |
| Existing pytest fixture usage | `mock_questionary_fixture` | Maintain fixture pattern |

### Step 3: Transform Test

#### Before:
```python
def test_old_pattern(monkeypatch):
    def fake_text(**kwargs):
        return "mocked_result"
    
    monkeypatch.setattr(questionary, "text", fake_text)
    
    comp = Component("test", "text")
    result = comp.create_questionary_component()
    assert result == "mocked_result"
```

#### After:
```python
def test_new_pattern():
    with mock_questionary() as mock_q:
        mock_q.text.return_value = "mocked_result"
        
        comp = Component("test", "text")
        result = comp.create_questionary_component()
        assert result == "mocked_result"
        mock_q.text.assert_called_once_with("test")
```

### Step 4: Verify Identical Behavior

Run both old and new tests to ensure identical outcomes:
```bash
# Run old test
pytest tests/test_file.py::test_old_pattern -v

# Run new test  
pytest tests/test_file.py::test_new_pattern -v

# Verify same results
```

## Error Handling Patterns

### Testing Error Scenarios

```python
def test_component_error():
    with mock_questionary() as mock_q:
        # Configure error
        mock_q.text.side_effect = RuntimeError("Test error")
        
        comp = Component("test", "text")
        with pytest.raises(RuntimeError, match="Test error"):
            comp.create_questionary_component()
```

### Testing Validation Errors

```python
def test_validation_error():
    with mock_questionary() as mock_q:
        # Configure validation failure
        from questionary_extended.validators import ValidationError
        mock_q.text.side_effect = ValidationError("Invalid input")
        
        comp = Component("test", "text")
        with pytest.raises(ValidationError):
            comp.create_questionary_component()
```

## Performance Testing

### Testing Component Creation Performance

```python
def test_component_performance():
    import time
    
    with mock_questionary() as mock_q:
        mock_q.text.return_value = "fast_result"
        
        comp = Component("test", "text")
        
        # Measure performance
        start = time.time()
        for _ in range(100):
            result = comp.create_questionary_component()
        duration = time.time() - start
        
        # Verify performance (DI should be fast)
        assert duration < 0.1  # Very fast with DI
        assert result == "fast_result"
```

## Integration Testing

### Testing with Real Questionary

```python
def test_real_questionary_integration():
    # No DI setup - uses real questionary
    comp = Component("test", "text", default="default_value")
    
    # In interactive environment, this would prompt user
    # In automated tests, mock just the interactive part
    import questionary
    original_text = questionary.text
    
    try:
        questionary.text = lambda **kw: "real_interaction_result"
        result = comp.create_questionary_component()
        assert result == "real_interaction_result"
    finally:
        questionary.text = original_text
```

### Testing DI System Availability

```python
def test_di_system_fallback():
    # Test that component falls back to legacy when DI unavailable
    from src.tui_engine.questionary_factory import clear_questionary_factory
    
    # Ensure DI is cleared
    clear_questionary_factory()
    
    comp = Component("test", "text")
    
    # Should fall back to legacy system
    try:
        result = comp.create_questionary_component()
        # If it succeeds, legacy system worked
        assert result is not None
    except (ImportError, ValueError):
        # Expected when questionary not available in test environment
        pass
```

## Debugging Tips

### Common Issues and Solutions

#### Issue: Mock not being used
```python
# Problem: DI not working
def test_debug_di():
    with mock_questionary() as mock_q:
        mock_q.text.return_value = "expected"
        
        # Debug: Check if DI is active
        from src.tui_engine.questionary_factory import is_questionary_factory_set
        assert is_questionary_factory_set()  # Should be True
        
        comp = Component("test", "text")
        result = comp.create_questionary_component()
        assert result == "expected"
```

#### Issue: Wrong call arguments
```python
# Problem: Assert called with wrong args
def test_debug_calls():
    with mock_questionary() as mock_q:
        mock_q.text.return_value = "result"
        
        comp = Component("test", "text", message="prompt")
        result = comp.create_questionary_component()
        
        # Debug: Check actual calls
        print(f"Actual calls: {mock_q.text.call_args_list}")
        
        # Verify with correct args
        mock_q.text.assert_called_once_with("test", message="prompt")
```

#### Issue: Context manager cleanup
```python
# Problem: Tests interfering with each other
def test_debug_cleanup():
    from src.tui_engine.questionary_factory import is_questionary_factory_set
    
    # Should be False at start
    assert not is_questionary_factory_set()
    
    with mock_questionary() as mock_q:
        # Should be True inside context
        assert is_questionary_factory_set()
    
    # Should be False after context
    assert not is_questionary_factory_set()
```

## Best Practices

### 1. Use Appropriate Helper
- Simple tests → `mock_questionary()`
- Multiple types → `mock_questionary_with_types()`
- Complex scenarios → `QuestionaryTestHelper`

### 2. Keep Setup Minimal
```python
# Good: Minimal setup
with mock_questionary() as mock_q:
    mock_q.text.return_value = "result"
    # test logic

# Avoid: Over-configuration
with mock_questionary() as mock_q:
    mock_q.text.return_value = "result"
    mock_q.select.return_value = "option"  # Not needed if not testing select
    # test logic
```

### 3. Use Built-in Verification
```python
# Good: Use built-in assert methods
mock_q.text.assert_called_once_with("expected_arg")

# Avoid: Manual verification
assert mock_q.text.called
assert mock_q.text.call_args[0][0] == "expected_arg"
```

### 4. Clear Test Intent
```python
# Good: Clear test structure
def test_clear_intent():
    with mock_questionary() as mock_q:
        # Setup
        mock_q.text.return_value = "user_input"
        
        # Action
        result = component.create_questionary_component()
        
        # Verification
        assert result == "user_input"
        mock_q.text.assert_called_once()

# Avoid: Mixed concerns
def test_unclear():
    with mock_questionary() as mock_q:
        mock_q.text.return_value = "user_input"
        result = component.create_questionary_component()
        assert result == "user_input"
        # Setup, action, verification all mixed together
```

This new test infrastructure provides clean, maintainable, and standard Python patterns that replace the complex questionary mocking system with significant improvements in readability, maintainability, and reliability.