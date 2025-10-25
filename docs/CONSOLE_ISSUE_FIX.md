# Console Issue Fix Guide

## Problem: Windows Console Buffer Errors in Questionary Tests

When running questionary-based tests on Windows, you may encounter:

```
prompt_toolkit.output.win32.NoConsoleScreenBufferError: No Windows console found. Are you running cmd.exe?
```

## Root Cause

The issue occurs because:

1. **questionary** imports **prompt_toolkit** which tries to access Windows console during **prompt creation** (not just during .ask())
2. **Component.create_questionary_component()** directly imports questionary, bypassing test mocks
3. Tests that only mock questionary in the bridge module miss the Component module import

## The Right Solution

### 1. Use Comprehensive Mocking

Mock questionary in **ALL** import locations:

```python
from tests.conftest_questionary import setup_questionary_mocks

def test_something(self, monkeypatch):
    # This fixes the console issue by mocking questionary everywhere
    setup_questionary_mocks(monkeypatch, {"text": "my_response"})

    component = Component(name="test", component_type="text")
    result = bridge.ask_component(component)  # No console errors!
```

### 2. Import Locations to Mock

The helper function mocks questionary in these critical locations:

- `questionary_extended.integration.questionary_bridge.questionary`
- `questionary_extended.core.component.questionary`

### 3. Pattern for All Tests

```python
"""Example test file using the correct pattern."""

import pytest
from questionary_extended.integration.questionary_bridge import QuestionaryBridge
from questionary_extended.core.component import Component
from tests.conftest_questionary import setup_questionary_mocks, DummyState

class TestMyFeature:
    def test_basic_interaction(self, monkeypatch):
        """Test basic questionary interaction."""
        state = DummyState()
        bridge = QuestionaryBridge(state)

        # Setup comprehensive mocks - this prevents console issues
        setup_questionary_mocks(monkeypatch, {
            "text": "user_input",
            "confirm": True,
            "select": "option1"
        })

        # Now create and use components safely
        component = Component(name="test", component_type="text", message="Enter value:")
        result = bridge.ask_component(component)

        assert result == "user_input"
        assert state.get("test") == "user_input"
```

## Summary: The Right Way to Fix Console Issues

### ✅ **The CORRECT Solution: Comprehensive Mocking**

```python
from tests.conftest_questionary import setup_questionary_mocks

def test_questionary_interaction(self, monkeypatch):
    setup_questionary_mocks(monkeypatch, {"text": "user_response"})
    # This fixes ALL console issues by mocking questionary in ALL import locations
```

### 🔧 **Key Technical Details**

The fix works because it addresses the **root cause**:

1. **questionary** imports **prompt_toolkit** which accesses Windows console during **prompt creation**
2. **Component.create_questionary_component()** creates a component_map accessing ALL prompt types
3. **Must mock questionary in BOTH modules**: bridge AND component
4. **Must provide ALL prompt types**: text, select, confirm, checkbox, password, autocomplete, path

### ❌ Don't: Mock only the bridge module

```python
# This DOESN'T work because Component imports questionary separately
monkeypatch.setattr("questionary_extended.integration.questionary_bridge.questionary", mock_questionary)
```

### ❌ Don't: Try to patch prompt_toolkit directly

```python
# This is fragile and breaks with prompt_toolkit updates
monkeypatch.setattr("prompt_toolkit.output.defaults.create_output", lambda: mock_output)
```

### ❌ Don't: Use environment variables or console redirection

```python
# These don't solve the core issue and add complexity
os.environ['PYTHONIOENCODING'] = 'utf-8'
```

### ❌ Don't: Provide incomplete mock questionary objects

```python
# This FAILS because Component.create_questionary_component() accesses all prompt types
mock_questionary = types.SimpleNamespace(text=lambda: MockPrompt())
# Missing: select, confirm, checkbox, password, autocomplete, path
```

## Custom Response Factories

For complex test scenarios, use a response factory:

```python
def test_dynamic_responses(self, monkeypatch):
    """Test with dynamic response generation."""

    def response_factory(prompt_type, args, kwargs):
        message = args[0] if args else ""
        if "name" in message.lower():
            return "John Doe"
        elif "age" in message.lower():
            return "25"
        return "default"

    setup_questionary_mocks(monkeypatch, response_factory)

    # Components will now get contextual responses
    name_comp = Component(name="name", component_type="text", message="Enter your name:")
    age_comp = Component(name="age", component_type="text", message="Enter your age:")

    assert bridge.ask_component(name_comp) == "John Doe"
    assert bridge.ask_component(age_comp) == "25"
```

## Testing Error Conditions

To test error handling, use the mock system:

```python
def test_questionary_unavailable(self, monkeypatch):
    """Test behavior when questionary is unavailable."""
    # Mock questionary as None to simulate missing dependency
    monkeypatch.setattr("questionary_extended.integration.questionary_bridge.questionary", None)

    component = Component(name="test", component_type="text")

    with pytest.raises(RuntimeError, match="questionary is not available"):
        bridge.ask_component(component)
```

## Performance Benefits

This approach also improves test performance:

- **No real console access**: Tests run faster without system calls
- **Deterministic responses**: No waiting for user input
- **Parallel execution**: Tests can run in parallel without console conflicts

## Integration with CI/CD

The fix ensures tests work reliably in:

- **GitHub Actions** (headless Linux/Windows environments)
- **Docker containers** (no console available)
- **VS Code Test Explorer** (integrated test runner)
- **pytest-xdist** (parallel test execution)

---

This is the definitive solution for Windows console issues in questionary tests. The `conftest_questionary.py` helper provides all necessary utilities to implement this pattern consistently across the test suite.
