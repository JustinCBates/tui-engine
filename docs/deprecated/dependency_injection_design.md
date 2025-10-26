# Dependency Injection Interface Design

## Executive Summary
Design for clean DI interface to replace the 87-line complex import fallback system in `component.py` with a simple, testable, and maintainable solution.

## Current Problem Analysis
- **Complexity**: 87 lines of fallback logic with 4 resolution strategies
- **Testing**: Unusual mocking patterns across 20+ test files
- **Maintainability**: Non-standard Python testing approaches
- **Performance**: Multiple fallback attempts on every component creation

## DI Design Decision: Module-Level Factory Pattern

### Why Module-Level Factory?
1. **Backward Compatibility**: Existing code continues to work unchanged
2. **Simple Testing**: Standard dependency injection patterns
3. **Performance**: Single factory lookup vs 4-step fallback
4. **Maintainability**: Clear separation of concerns

### Core API Design

```python
# src/tui_engine/questionary_factory.py
from typing import Optional, Callable, Any
import questionary

# Type aliases for clarity
QuestionaryFactory = Callable[[], Any]
QuestionaryModule = Any

class QuestionaryProvider:
    """Central provider for questionary dependencies with DI support."""
    
    def __init__(self):
        self._factory: Optional[QuestionaryFactory] = None
        self._cached_questionary: Optional[QuestionaryModule] = None
    
    def set_factory(self, factory: QuestionaryFactory) -> None:
        """Set custom questionary factory (primarily for testing)."""
        self._factory = factory
        self._cached_questionary = None  # Clear cache
    
    def get_questionary(self) -> QuestionaryModule:
        """Get questionary module via factory or default import."""
        if self._factory is not None:
            if self._cached_questionary is None:
                self._cached_questionary = self._factory()
            return self._cached_questionary
        
        # Default behavior - simple import
        import questionary
        return questionary
    
    def clear_factory(self) -> None:
        """Reset to default questionary import."""
        self._factory = None
        self._cached_questionary = None

# Global provider instance
_provider = QuestionaryProvider()

# Public API functions
def set_questionary_factory(factory: QuestionaryFactory) -> None:
    """Set custom questionary factory for dependency injection."""
    _provider.set_factory(factory)

def get_questionary() -> QuestionaryModule:
    """Get questionary module (injected or default)."""
    return _provider.get_questionary()

def clear_questionary_factory() -> None:
    """Reset to default questionary behavior."""
    _provider.clear_factory()
```

## Integration with Component Class

### Before (87 lines of complexity):
```python
def create_questionary_component(self, prompt: str, **kwargs) -> Any:
    # 87 lines of complex fallback logic...
    questionary_module = None
    
    # Strategy 1: Runtime accessor
    if hasattr(self._runtime, 'get_questionary_module'):
        # ... complex logic
    
    # Strategy 2: sys.modules lookup
    if questionary_module is None:
        # ... more complex logic
    
    # Strategy 3: globals() fallback
    # Strategy 4: direct import
    # ... etc
```

### After (Simple DI approach):
```python
def create_questionary_component(self, prompt: str, **kwargs) -> Any:
    """Create questionary component using dependency injection."""
    from .questionary_factory import get_questionary
    
    questionary_module = get_questionary()
    
    component_type = kwargs.get('type', 'text')
    if hasattr(questionary_module, component_type):
        component_func = getattr(questionary_module, component_type)
        return component_func(prompt, **kwargs)
    
    raise ValueError(f"Unknown questionary component type: {component_type}")
```

## Testing Patterns

### Before (Complex mocking):
```python
def test_complex_component():
    # Complex setup with monkeypatch
    mock_questionary = MagicMock()
    monkeypatch.setattr(sys.modules, 'questionary', mock_questionary)
    # ... more complex setup
```

### After (Simple DI):
```python
def test_simple_component():
    # Clean dependency injection
    mock_questionary = MagicMock()
    set_questionary_factory(lambda: mock_questionary)
    
    # Test logic
    component = Component()
    result = component.create_questionary_component("test")
    
    # Cleanup
    clear_questionary_factory()
```

### Enhanced Test Helper:
```python
# tests/questionary_helpers.py
import pytest
from contextlib import contextmanager
from unittest.mock import MagicMock
from src.tui_engine.questionary_factory import set_questionary_factory, clear_questionary_factory

@contextmanager
def mock_questionary(**method_configs):
    """Context manager for clean questionary mocking."""
    mock = MagicMock()
    
    # Configure specific methods if provided
    for method_name, return_value in method_configs.items():
        getattr(mock, method_name).return_value = return_value
    
    set_questionary_factory(lambda: mock)
    try:
        yield mock
    finally:
        clear_questionary_factory()

# Usage:
def test_with_helper():
    with mock_questionary(text=MagicMock()) as mock_q:
        # Test code using injected questionary
        component = Component()
        result = component.create_questionary_component("test", type="text")
        mock_q.text.assert_called_once()
```

## Migration Strategy

### Phase 1: Add DI System (Non-Breaking)
1. Create `questionary_factory.py` module
2. Add DI logic to `create_questionary_component()` as primary path
3. Keep existing fallback system as secondary path
4. All existing tests continue to work

### Phase 2: Migrate Tests
1. Create new test helpers using DI patterns
2. Migrate tests incrementally (5-10 files at a time)
3. Run both old and new patterns in parallel during transition

### Phase 3: Remove Old System
1. Remove complex fallback logic after all tests migrated
2. Remove `_runtime.py` and old conftest infrastructure
3. Update documentation

## Benefits Analysis

### Code Reduction:
- **Before**: 87 lines of complex resolution logic
- **After**: ~15 lines of simple DI logic
- **Reduction**: ~80% code reduction in core component

### Test Simplification:
- **Before**: Complex monkeypatch patterns across 20+ files
- **After**: Simple context manager patterns
- **Improvement**: Standard Python testing practices

### Performance:
- **Before**: 4-step fallback resolution on every component creation
- **After**: Single factory lookup (with caching)
- **Improvement**: Faster component creation, especially in test scenarios

### Maintainability:
- **Before**: Non-standard mocking requiring deep understanding
- **After**: Standard DI patterns familiar to all Python developers
- **Improvement**: Lower barrier to entry for contributors

## Risk Mitigation

### Backward Compatibility:
- Existing code works unchanged during transition
- Gradual migration allows for rollback at any step
- New system tested alongside old system

### Test Coverage:
- Current 79% coverage maintained throughout transition
- New patterns validated before old patterns removed
- Comprehensive test migration validation

### Documentation:
- Clear migration guides for each phase
- Before/after examples for all patterns
- Updated testing documentation

## Implementation Timeline

1. **Week 1**: Implement `questionary_factory.py` and basic DI system
2. **Week 2**: Update `Component` class with hybrid approach
3. **Week 3**: Create new test helpers and migrate 50% of tests
4. **Week 4**: Complete test migration and remove old system
5. **Week 5**: Documentation update and final validation

This design provides a clean, maintainable solution that eliminates the unusual mocking complexity while maintaining full backward compatibility during the transition.