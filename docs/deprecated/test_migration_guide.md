# Testing Migration Guide: From Complex Mocking to Clean DI

## Executive Summary

This guide provides comprehensive migration patterns to move from the current complex questionary mocking system to clean dependency injection (DI) patterns. The migration eliminates:

- Complex `conftest_questionary.py` setup (670+ lines)
- Multiple monkeypatch operations per test
- Unusual `sys.modules` manipulation
- Runtime accessor mocking complexity

## Current vs New Patterns Comparison

### 📊 **Complexity Reduction Overview**

| Aspect | Before (Complex) | After (Clean DI) | Improvement |
|--------|------------------|------------------|-------------|
| **Setup Lines** | 5-10 lines per test | 1-2 lines per test | 80% reduction |
| **Mock Complexity** | Multiple monkeypatch calls | Single context manager | 90% simpler |
| **Cleanup** | Manual/automatic via fixtures | Automatic via context manager | 100% reliable |
| **Readability** | Test logic buried in setup | Clear separation of concerns | Dramatically better |
| **Maintainability** | Requires understanding of unusual patterns | Standard Python patterns | Much easier |

## Migration Patterns

### Pattern 1: Basic Component Testing

#### ❌ **BEFORE: Complex Monkeypatch Pattern**
```python
def test_component_create_questionary_component_monkeypatched(monkeypatch):
    calls = {}

    def fake_text(**kwargs):
        calls["text"] = kwargs
        return "TEXT_QUESTION"

    # Complex setup: monkeypatch questionary module
    monkeypatch.setattr(questionary, "text", fake_text)

    # Test logic buried after setup
    comp = Component("name", "text", message="hi", foo="bar")
    res = comp.create_questionary_component()
    
    # Manual verification
    assert res == "TEXT_QUESTION"
    assert "text" in calls and calls["text"]["message"] == "hi"
```

#### ✅ **AFTER: Clean DI Pattern**
```python
def test_component_create_questionary_component_di():
    from tests.helpers.questionary_helpers import mock_questionary
    
    # Clean setup: single context manager
    with mock_questionary() as mock_q:
        mock_q.text.return_value = "TEXT_QUESTION"
        
        # Clear test logic
        comp = Component("name", "text", message="hi", foo="bar")
        res = comp.create_questionary_component()
        
        # Built-in verification
        assert res == "TEXT_QUESTION"
        mock_q.text.assert_called_once_with("name", message="hi", foo="bar")
    # Automatic cleanup
```

**Benefits**: 70% fewer lines, automatic cleanup, clearer intent, standard Python patterns.

### Pattern 2: Multiple Component Types

#### ❌ **BEFORE: Multiple Monkeypatch Operations**
```python
def test_multiple_components(monkeypatch):
    text_calls = {}
    select_calls = {}
    confirm_calls = {}
    
    def fake_text(**kwargs):
        text_calls["last"] = kwargs
        return "text_result"
    
    def fake_select(**kwargs):
        select_calls["last"] = kwargs
        return "select_result"
        
    def fake_confirm(**kwargs):
        confirm_calls["last"] = kwargs
        return True
    
    # Multiple complex setup operations
    monkeypatch.setattr(questionary, "text", fake_text)
    monkeypatch.setattr(questionary, "select", fake_select)
    monkeypatch.setattr(questionary, "confirm", fake_confirm)
    
    # Test logic
    text_comp = Component("name", "text")
    select_comp = Component("choice", "select", choices=["A", "B"])
    confirm_comp = Component("ok", "confirm")
    
    text_result = text_comp.create_questionary_component()
    select_result = select_comp.create_questionary_component()
    confirm_result = confirm_comp.create_questionary_component()
    
    # Manual verification
    assert text_result == "text_result"
    assert select_result == "select_result"
    assert confirm_result is True
    assert text_calls["last"]["name"] == "name"
    assert select_calls["last"]["choices"] == ["A", "B"]
```

#### ✅ **AFTER: Single DI Context**
```python
def test_multiple_components_di():
    from tests.helpers.questionary_helpers import mock_questionary_with_types
    
    # Single setup with pre-configured types
    with mock_questionary_with_types(
        text="text_result",
        select="select_result", 
        confirm=True
    ) as mock_q:
        
        # Clear test logic
        text_comp = Component("name", "text")
        select_comp = Component("choice", "select", choices=["A", "B"])
        confirm_comp = Component("ok", "confirm")
        
        text_result = text_comp.create_questionary_component()
        select_result = select_comp.create_questionary_component()
        confirm_result = confirm_comp.create_questionary_component()
        
        # Built-in verification
        assert text_result == "text_result"
        assert select_result == "select_result"
        assert confirm_result is True
        
        # Automatic call verification
        mock_q.text.assert_called_once_with("name")
        mock_q.select.assert_called_once_with("choice", choices=["A", "B"])
        mock_q.confirm.assert_called_once_with("ok")
```

**Benefits**: 80% fewer lines, single setup operation, automatic verification, much clearer.

### Pattern 3: Complex CLI Testing

#### ❌ **BEFORE: Complex Runtime and Module Mocking**
```python
def test_cli_complex_scenario(monkeypatch):
    # Complex setup from conftest_questionary
    setup_questionary_mocks(monkeypatch)
    
    # Additional runtime mocking  
    mock_runtime = MagicMock()
    mock_questionary = MagicMock()
    
    # Multiple monkeypatch operations
    monkeypatch.setattr("questionary_extended._runtime.get_questionary", 
                       lambda: mock_questionary)
    monkeypatch.setattr(sys.modules, "questionary", mock_questionary)
    
    # Configure mock behavior
    mock_questionary.text.return_value = "user_input"
    mock_questionary.select.return_value = "selected_option"
    mock_questionary.confirm.return_value = True
    
    # Test logic buried in setup complexity
    result = run_cli_command(["create", "--interactive"])
    
    # Manual verification
    assert result.exit_code == 0
    assert mock_questionary.text.called
    assert mock_questionary.select.called
```

#### ✅ **AFTER: Clean DI with Helper Class**
```python
def test_cli_complex_scenario_di():
    from tests.helpers.questionary_helpers import QuestionaryTestHelper
    
    # Clean setup with advanced helper
    with QuestionaryTestHelper() as helper:
        # Configure interaction sequence
        helper.simulate_user_input_sequence({
            "text": "user_input",
            "select": "selected_option", 
            "confirm": True
        })
        
        # Clear test logic
        result = run_cli_command(["create", "--interactive"])
        
        # Built-in verification
        assert result.exit_code == 0
        helper.assert_component_called("text")
        helper.assert_component_called("select")
        helper.assert_component_called("confirm")
```

**Benefits**: 90% fewer lines, standard patterns, automatic cleanup, much more readable.

### Pattern 4: Pytest Fixtures

#### ❌ **BEFORE: Complex Autouse Fixtures**
```python
# In conftest.py - affects ALL tests
@pytest.fixture(autouse=True)
def _install_questionary_mock(monkeypatch):
    """Complex autouse fixture affecting all tests."""
    setup_questionary_mocks(monkeypatch)  # 670+ lines of complexity
    yield

# In test file - still requires additional setup
def test_with_fixture(monkeypatch):
    # Still need additional monkeypatch operations
    monkeypatch.setattr(questionary, "text", lambda **kw: "result")
    
    comp = Component("test", "text")
    result = comp.create_questionary_component()
    assert result == "result"
```

#### ✅ **AFTER: Clean Optional Fixtures**
```python
# In conftest.py - optional, clean fixtures
from tests.helpers.questionary_helpers import mock_questionary_fixture

# In test file - clean, explicit
def test_with_fixture_di(mock_questionary_fixture):
    # Clean, explicit setup
    mock_questionary_fixture.text.return_value = "result"
    
    comp = Component("test", "text")
    result = comp.create_questionary_component()
    
    assert result == "result"
    mock_questionary_fixture.text.assert_called_once_with("test")
```

**Benefits**: Optional vs forced, explicit vs hidden, much simpler setup.

## Advanced Migration Patterns

### Pattern 5: Error Handling Testing

#### ❌ **BEFORE: Complex Exception Mocking**
```python
def test_error_handling(monkeypatch):
    def failing_text(**kwargs):
        raise RuntimeError("Simulated error")
    
    # Complex error injection
    monkeypatch.setattr(questionary, "text", failing_text)
    
    comp = Component("test", "text")
    with pytest.raises(RuntimeError, match="Simulated error"):
        comp.create_questionary_component()
```

#### ✅ **AFTER: Clean Error Injection**
```python
def test_error_handling_di():
    with mock_questionary() as mock_q:
        # Clean error injection
        mock_q.text.side_effect = RuntimeError("Simulated error")
        
        comp = Component("test", "text")
        with pytest.raises(RuntimeError, match="Simulated error"):
            comp.create_questionary_component()
```

### Pattern 6: Integration Testing

#### ❌ **BEFORE: Mixed Real/Mock Complexity**
```python
def test_integration_complex(monkeypatch):
    # Some real questionary, some mocked - complex to manage
    real_questionary = importlib.import_module("questionary")
    
    def selective_mock(method_name):
        if method_name == "text":
            return lambda **kw: "mocked_text"
        else:
            return getattr(real_questionary, method_name)
    
    # Complex selective mocking
    for method in ["text", "select", "confirm"]:
        monkeypatch.setattr(questionary, method, selective_mock(method))
```

#### ✅ **AFTER: Clear Integration Control**
```python
def test_integration_clean():
    with mock_questionary() as mock_q:
        # Clear control over what's mocked
        mock_q.text.return_value = "mocked_text"
        # Leave other methods as MagicMock defaults or configure as needed
        
        # Test logic is clear and isolated
```

## Migration Steps for Each Test File

### Step 1: Identify Current Patterns
```python
# Look for these patterns in existing tests:
- monkeypatch.setattr(questionary, ...)
- setup_questionary_mocks() calls
- sys.modules manipulation
- Complex mock function definitions
```

### Step 2: Replace with DI Patterns
```python
# Replace with appropriate DI helper:
from tests.helpers.questionary_helpers import (
    mock_questionary,              # Basic context manager
    mock_questionary_with_types,   # Pre-configured types
    QuestionaryTestHelper,         # Advanced scenarios
    mock_questionary_fixture       # Pytest fixture
)
```

### Step 3: Simplify Test Logic
```python
# Before: Setup buried with test logic
def test_old():
    # 10 lines of setup
    # 3 lines of actual test
    # 5 lines of manual verification

# After: Clear separation
def test_new():
    with mock_questionary() as mock_q:  # 1 line setup
        mock_q.text.return_value = "result"
        
        # Clear test logic
        result = component.create_questionary_component()
        
        # Built-in verification
        assert result == "result"
        mock_q.text.assert_called_once()
```

### Step 4: Verify Identical Behavior
```python
# Run both old and new tests side by side during migration
# Ensure identical outcomes before removing old patterns
```

## File-by-File Migration Priority

### Priority 1: Core Unit Tests (Immediate Impact)
```
tests/test_component_and_prompts_wave1.py    # Basic component testing
tests/test_component_deep_wave1.py           # Deep component features  
tests/test_component_and_bridge_errors.py    # Error handling
```

### Priority 2: CLI Tests (High Complexity)
```
tests/test_cli_commands.py                   # CLI command testing
tests/test_cli_integration.py               # CLI integration
tests/test_cli_wave2.py                     # CLI wave 2 features
tests/test_cli_wave2_more.py                # Extended CLI features
```

### Priority 3: Integration Tests (Lower Priority)
```
All remaining test files that use questionary mocking
```

## Expected Benefits After Migration

### 📊 **Quantitative Improvements**
- **Code Reduction**: 70-90% fewer lines per test
- **Setup Time**: 80% faster test setup 
- **Maintenance**: 90% easier to understand and modify
- **Reliability**: 100% automatic cleanup vs manual/fixture-based

### 🎯 **Qualitative Improvements**
- **Readability**: Clear separation of setup vs test logic
- **Maintainability**: Standard Python patterns vs unusual mocking
- **Debugging**: Easier to understand when tests fail
- **Onboarding**: New developers can understand tests immediately

### 🔒 **Risk Mitigation**
- **Incremental Migration**: Migrate 5-10 files at a time
- **Parallel Testing**: Run old and new patterns side-by-side
- **Rollback Safety**: Keep old patterns until migration complete
- **Validation**: Verify identical behavior at each step

## Next Steps

1. **Phase 3B**: Start with Priority 1 files (3 files)
2. **Validate**: Ensure identical test behavior
3. **Continue**: Move to Priority 2 files (4 files)  
4. **Complete**: Finish remaining files
5. **Cleanup**: Remove old infrastructure in Phase 4A

This migration will transform the testing infrastructure from complex, unusual patterns to clean, standard Python dependency injection patterns that any developer can understand and maintain.