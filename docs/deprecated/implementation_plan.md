# Implementation Plan: DI Interface

## File Changes Overview

### NEW FILES TO CREATE:

#### 1. `src/tui_engine/questionary_factory.py`
**Purpose**: Core DI system  
**Size**: ~50 lines  
**Dependencies**: typing, questionary  

```python
# Full implementation ready for Phase 2A
from typing import Optional, Callable, Any

QuestionaryFactory = Callable[[], Any]
QuestionaryModule = Any

class QuestionaryProvider:
    def __init__(self):
        self._factory: Optional[QuestionaryFactory] = None
        self._cached_questionary: Optional[QuestionaryModule] = None
    
    def set_factory(self, factory: QuestionaryFactory) -> None:
        self._factory = factory
        self._cached_questionary = None
    
    def get_questionary(self) -> QuestionaryModule:
        if self._factory is not None:
            if self._cached_questionary is None:
                self._cached_questionary = self._factory()
            return self._cached_questionary
        
        import questionary
        return questionary
    
    def clear_factory(self) -> None:
        self._factory = None
        self._cached_questionary = None

_provider = QuestionaryProvider()

def set_questionary_factory(factory: QuestionaryFactory) -> None:
    _provider.set_factory(factory)

def get_questionary() -> QuestionaryModule:
    return _provider.get_questionary()

def clear_questionary_factory() -> None:
    _provider.clear_factory()
```

#### 2. `tests/helpers/questionary_helpers.py`
**Purpose**: Clean test helpers  
**Size**: ~30 lines  
**Dependencies**: pytest, contextlib, unittest.mock  

```python
import pytest
from contextlib import contextmanager
from unittest.mock import MagicMock
from src.tui_engine.questionary_factory import set_questionary_factory, clear_questionary_factory

@contextmanager
def mock_questionary():
    mock = MagicMock()
    set_questionary_factory(lambda: mock)
    try:
        yield mock
    finally:
        clear_questionary_factory()

@pytest.fixture
def mock_questionary_fixture():
    mock = MagicMock()
    set_questionary_factory(lambda: mock)
    yield mock
    clear_questionary_factory()
```

### EXISTING FILES TO MODIFY:

#### 1. `src/tui_engine/component.py`
**Current**: 87 lines in `create_questionary_component()`  
**After**: ~15 lines in `create_questionary_component()`  
**Change Type**: Hybrid approach (new DI + fallback to old system)

```python
# BEFORE (lines 45-132):
def create_questionary_component(self, prompt: str, **kwargs) -> Any:
    questionary_module = None
    
    # Strategy 1: Runtime accessor
    if self._runtime and hasattr(self._runtime, 'get_questionary_module'):
        try:
            questionary_module = self._runtime.get_questionary_module()
            if questionary_module:
                logging.debug("Questionary module obtained from runtime.")
        except Exception as e:
            logging.debug(f"Failed to get questionary from runtime: {e}")
    
    # Strategy 2: sys.modules lookup
    if questionary_module is None:
        # ... 30+ more lines of complex logic
    
    # Strategy 3: globals() fallback
    # Strategy 4: direct import
    # ... more complex logic

# AFTER (Phase 2B implementation):
def create_questionary_component(self, prompt: str, **kwargs) -> Any:
    """Create questionary component using dependency injection."""
    try:
        # Primary: Use DI system
        from .questionary_factory import get_questionary
        questionary_module = get_questionary()
    except ImportError:
        # Fallback: Use existing complex resolution during transition
        questionary_module = self._legacy_questionary_resolution()
    
    component_type = kwargs.get('type', 'text')
    if hasattr(questionary_module, component_type):
        component_func = getattr(questionary_module, component_type)
        return component_func(prompt, **kwargs)
    
    raise ValueError(f"Unknown questionary component type: {component_type}")

def _legacy_questionary_resolution(self):
    """Legacy complex resolution - will be removed in Phase 4A."""
    # Move existing 87 lines here temporarily
    # ... existing complex logic
```

#### 2. `src/tui_engine/__init__.py`
**Purpose**: Export DI functions for public API  
**Addition**: ~3 lines

```python
# Add to existing exports:
from .questionary_factory import (
    set_questionary_factory, 
    get_questionary, 
    clear_questionary_factory
)
```

### TEST MIGRATION PLAN:

#### Priority 1: Core Unit Tests (5 files)
```
tests/test_component_and_prompts_wave1.py
tests/test_component_deep_wave1.py  
tests/test_component_and_bridge_errors.py
tests/test_cli_commands.py
tests/test_cli_integration.py
```

#### Priority 2: CLI Tests (8 files)
```
tests/test_cli_wave2.py
tests/test_cli_wave2_more.py
All test_cli_*.py files
```

#### Priority 3: Integration Tests (7+ files)  
```
All remaining test files that use create_questionary_component()
```

### PHASE-BY-PHASE IMPLEMENTATION:

#### Phase 2A: Implement DI System (Week 1)
**Goal**: Add DI system without breaking anything

1. **Create** `questionary_factory.py` (NEW)
2. **Create** `tests/helpers/questionary_helpers.py` (NEW)  
3. **Test** DI system works in isolation
4. **Verify** all existing tests still pass

**Success Criteria**: 
- DI system functional
- Zero test failures
- 79% coverage maintained

#### Phase 2B: Update Component Logic (Week 1-2)  
**Goal**: Use DI as primary, keep fallback

1. **Modify** `component.py` with hybrid approach
2. **Add** DI exports to `__init__.py`
3. **Test** new logic works
4. **Verify** all existing tests still pass

**Success Criteria**:
- Component uses DI when available
- Fallback to old system works
- Zero test failures

#### Phase 3A: Create New Test Infrastructure (Week 2)
**Goal**: Build new testing patterns

1. **Create** example tests using new helpers
2. **Document** migration patterns  
3. **Validate** new patterns work correctly
4. **Create** migration guide

**Success Criteria**:
- New test patterns documented
- Migration examples work
- Clear upgrade path defined

#### Phase 3B: Migrate Tests (Week 3-4)
**Goal**: Convert tests to use DI patterns

1. **Migrate** Priority 1 tests (5 files)
2. **Verify** functionality identical
3. **Migrate** Priority 2 tests (8 files)  
4. **Complete** remaining test migrations

**Success Criteria**:
- All tests use new DI patterns
- Coverage remains 79%+
- Test execution faster

#### Phase 4A: Remove Old System (Week 4-5)
**Goal**: Clean up legacy complexity

1. **Remove** complex fallback logic from `component.py`
2. **Delete** `_runtime.py` module
3. **Delete** old `conftest_questionary.py` infrastructure
4. **Update** documentation

**Success Criteria**:
- 80% code reduction achieved
- All tests pass with new system only
- Documentation updated

## Risk Assessment & Mitigation

### HIGH RISK: Breaking existing functionality
**Mitigation**: Hybrid approach allows rollback at any phase

### MEDIUM RISK: Test migration complexity  
**Mitigation**: Migrate incrementally, verify each step

### LOW RISK: Performance regression
**Mitigation**: DI system actually improves performance

## Validation Checklist

- [ ] All existing tests pass after each phase
- [ ] Coverage remains 79%+ throughout transition  
- [ ] New test patterns simpler than old patterns
- [ ] Documentation updated for new approach
- [ ] Performance equal or better than before
- [ ] Code complexity significantly reduced

This implementation plan provides clear, actionable steps to move from the complex import fallback system to clean dependency injection while maintaining full backward compatibility throughout the transition.