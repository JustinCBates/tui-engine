## Dependency Injection Refactoring Analysis 💉

### 🎯 **Current Architecture Issues**

The current system has several components that make refactoring challenging:

1. **Component Class** - Has complex `create_questionary_component()` method with 4-way resolution
2. **Convenience Functions** - `text()`, `select()` etc. that create Components
3. **Bridge Integration** - QuestionaryBridge calls `component.create_questionary_component()`
4. **Test Infrastructure** - 64+ tests using current mocking patterns

### 📝 **Proposed Dependency Injection Design**

#### **Option 1: Constructor Injection (Cleanest)**

```python
class Component:
    def __init__(self, name: str, component_type: str, questionary_factory=None, **kwargs):
        self.name = name
        self.component_type = component_type
        self.config = kwargs
        # Inject the dependency at construction time
        self._questionary_factory = questionary_factory or self._default_questionary_factory()
    
    def _default_questionary_factory(self):
        """Default factory for production use."""
        import questionary
        return questionary
    
    def create_questionary_component(self) -> Any:
        """Create questionary component using injected factory."""
        # Simple, clean - no complex resolution logic
        factory = self._questionary_factory
        component_func = getattr(factory, self.component_type)
        return component_func(**self.questionary_config)

# Convenience functions become:
def text(name: str, message: str = None, questionary_factory=None, **kwargs):
    return Component(name, "text", questionary_factory, message=message, **kwargs)

# Tests become:
def test_component():
    mock_questionary = Mock()
    component = Component("test", "text", questionary_factory=mock_questionary)
    # Simple, standard testing
```

#### **Option 2: Module-Level Injection (Less Invasive)**

```python
# Global dependency that can be overridden
_questionary_factory = None

def set_questionary_factory(factory):
    """Set global questionary factory for testing."""
    global _questionary_factory
    _questionary_factory = factory

def get_questionary_factory():
    """Get questionary factory."""
    if _questionary_factory is not None:
        return _questionary_factory
    import questionary
    return questionary

class Component:
    def create_questionary_component(self) -> Any:
        """Create questionary component using global factory."""
        factory = get_questionary_factory()
        component_func = getattr(factory, self.component_type)
        return component_func(**self.questionary_config)

# Tests become:
def test_component():
    mock_questionary = Mock()
    set_questionary_factory(mock_questionary)
    component = Component("test", "text")
    # Much simpler than current approach
```

#### **Option 3: Context Manager Pattern (Most Flexible)**

```python
from contextlib import contextmanager

class QuestionaryContext:
    def __init__(self):
        self._factory = None
    
    def set_factory(self, factory):
        self._factory = factory
    
    def get_factory(self):
        if self._factory is not None:
            return self._factory
        import questionary
        return questionary

# Global context
_questionary_context = QuestionaryContext()

@contextmanager
def questionary_factory(factory):
    """Context manager for temporarily overriding questionary factory."""
    old_factory = _questionary_context._factory
    _questionary_context.set_factory(factory)
    try:
        yield
    finally:
        _questionary_context.set_factory(old_factory)

class Component:
    def create_questionary_component(self) -> Any:
        factory = _questionary_context.get_factory()
        component_func = getattr(factory, self.component_type)
        return component_func(**self.questionary_config)

# Tests become:
def test_component():
    mock_questionary = Mock()
    with questionary_factory(mock_questionary):
        component = Component("test", "text")
        # Automatic cleanup, no global state pollution
```

### 📊 **Difficulty Analysis**

#### **Code Changes Required:**

| Component | Current Lines | Change Difficulty | Impact |
|-----------|---------------|------------------|--------|
| **Component.__init__** | 10 | ⭐ Easy | Add optional parameter |
| **Component.create_questionary_component** | 50 | ⭐⭐ Medium | Replace complex logic with simple call |
| **Convenience functions** (text, select, etc.) | 80 | ⭐ Easy | Add optional parameter |
| **QuestionaryBridge** | 10 | ⭐ Easy | No changes needed |
| **Tests** | 64+ files | ⭐⭐⭐ Hard | Update all test mocking |

#### **Test Migration Effort:**

**Current test pattern:**
```python
def test_something(monkeypatch):
    setup_questionary_mocks(monkeypatch, {"text": "answer"})
    # Test uses complex resolution system
```

**New test pattern (Option 1):**
```python
def test_something():
    mock_q = Mock()
    mock_q.text.return_value.ask.return_value = "answer"
    component = Component("test", "text", questionary_factory=mock_q)
```

**New test pattern (Option 2):**
```python
def test_something():
    mock_q = Mock()
    mock_q.text.return_value.ask.return_value = "answer"
    set_questionary_factory(mock_q)
    component = Component("test", "text")
```

### 🕐 **Estimated Effort**

#### **Option 1: Constructor Injection**
- **Core refactoring**: 4-6 hours
- **Test migration**: 20-30 hours
- **Total effort**: ~30-36 hours
- **Risk**: Medium (API changes)

#### **Option 2: Module-Level Injection**
- **Core refactoring**: 2-3 hours
- **Test migration**: 10-15 hours
- **Total effort**: ~12-18 hours  
- **Risk**: Low (minimal API changes)

#### **Option 3: Context Manager**
- **Core refactoring**: 3-4 hours
- **Test migration**: 15-20 hours
- **Total effort**: ~18-24 hours
- **Risk**: Low-Medium

### 🎯 **Recommended Approach: Option 2 (Module-Level)**

**Why Option 2 is best for this situation:**

✅ **Minimal disruption** - No changes to public API  
✅ **Easier test migration** - Can be done incrementally  
✅ **Backward compatible** - Existing code continues working  
✅ **Simpler than current system** - Much easier to understand  
✅ **Standard pattern** - Similar to how many Python libraries work  

### 🔧 **Implementation Plan**

#### **Phase 1: Add New System (2-3 hours)**
1. Add module-level factory functions
2. Update Component.create_questionary_component() to use factory
3. Keep old resolution logic as fallback initially
4. Verify existing tests still pass

#### **Phase 2: Migrate Tests Incrementally (10-15 hours)**
1. Update 5-10 tests at a time to use new pattern
2. Remove old mocking infrastructure gradually
3. Update documentation

#### **Phase 3: Remove Old System (1-2 hours)**
1. Remove complex resolution logic
2. Remove runtime module and old test infrastructure
3. Clean up documentation

### 📈 **Benefits of Refactoring**

**Developer Experience:**
- ✅ **Much simpler tests** - standard mocking patterns
- ✅ **Easier to understand** - clear dependency flow
- ✅ **Better performance** - no runtime resolution overhead
- ✅ **Standard Python patterns** - familiar to all developers

**Maintenance:**
- ✅ **Less code to maintain** - remove complex resolution logic
- ✅ **Easier debugging** - explicit dependencies
- ✅ **Better test reliability** - no complex import state management

**Coverage:**
- ✅ **Easier to achieve 100%** - simpler code paths
- ✅ **More meaningful tests** - test business logic, not infrastructure

### ✅ **Recommendation**

**Yes, dependency injection would be significantly easier to work with!**

The refactoring effort is moderate (12-18 hours) but would result in:
- **Much simpler codebase**
- **Standard testing patterns**  
- **Easier future maintenance**
- **Better developer experience**

The current complex system was a solution to specific problems, but dependency injection is a **cleaner, more maintainable approach** that follows Python best practices.

**The ROI is high** - moderate one-time effort for long-term simplicity and maintainability gains.