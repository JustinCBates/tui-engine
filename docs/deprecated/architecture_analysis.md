# Phase 1A: Current Architecture Analysis 🔍

## Component Class Structure Analysis

### 📋 **Component Class Core**
- **Location**: `src/questionary_extended/core/component.py`
- **Main Method**: `create_questionary_component()` (87 lines of complex resolution logic!)
- **Constructor**: Simple `__init__(name, component_type, **kwargs)`
- **Dependencies**: Imports `importlib`, `sys`, accesses `globals()`, imports `_runtime`

### 🏗️ **Component Instantiation Patterns**

#### **1. Direct Component Construction (12 locations)**
```python
# Via convenience functions in component.py
Component(name, "text", message=message, **kwargs)          # text()
Component(name, "select", message=message, choices=choices) # select() 
Component(name, "confirm", message=message, **kwargs)       # confirm()
Component(name, "password", message=message, **kwargs)      # password()
Component(name, "checkbox", message=message, choices=choices) # checkbox()
Component(name, "autocomplete", message=message, choices=choices) # autocomplete()
Component(name, "path", message=message, **kwargs)          # path()
```

#### **2. Indirect Component Creation (4 locations)**
```python
# Card and Assembly classes import component functions
from .component import text as _text_component      # card.py, assembly.py
from .component import select as _select_component  # card.py, assembly.py

comp = _text_component(name, **kwargs)    # Creates Component internally
comp = _select_component(name, choices=choices, **kwargs)
```

#### **3. Component Usage (Primary Consumer)**
```python
# QuestionaryBridge is the main consumer
def ask_component(self, component: Component) -> Any:
    prompt = component.create_questionary_component()  # THE BOTTLENECK!
```

### 🕸️ **Complex Resolution Flow Analysis**

The `create_questionary_component()` method has **4 resolution strategies** with **multiple fallbacks**:

#### **Strategy 1: Runtime Accessor**
```python
try:
    _rt = importlib.import_module("questionary_extended._runtime")
    q = _rt.get_questionary()
except Exception:
    q = None
```

#### **Strategy 2: sys.modules Fallback**
```python
try:
    if q is None:
        q_sys = sys.modules.get("questionary")
        if q_sys is not None:
            q = q_sys
except Exception:
    pass
```

#### **Strategy 3: globals() Fallback**
```python
try:
    if q is None:
        m_q = globals().get("questionary", None)
        if m_q is not None:
            q = m_q
except Exception:
    pass
```

#### **Strategy 4: Direct Import Fallback**
```python
if q is None:
    try:
        q = importlib.import_module("questionary")
    except Exception:
        raise ImportError("...")
```

#### **Then: Candidate Selection Logic (30+ lines)**
```python
# Builds candidates list from all resolution strategies
candidates = []
# Multiple try/except blocks to extract attributes
# Complex _is_valid_factory() validation
# Priority selection logic
# Final component_func(**self.questionary_config) call
```

### 📊 **Impact Scope Analysis**

#### **Files That Will Need Updates:**

| File | Current Usage | Impact Level |
|------|---------------|--------------|
| `core/component.py` | **87-line resolution method** | 🔴 HIGH - Core refactoring |
| `integration/questionary_bridge.py` | Calls `component.create_questionary_component()` | 🟡 LOW - No changes needed |
| `core/card.py` | Imports component functions | 🟡 LOW - No API changes |
| `core/assembly.py` | Imports component functions | 🟡 LOW - No API changes |
| `core/__init__.py` | Exports component functions | 🟡 LOW - No API changes |

#### **Test Files That Use create_questionary_component() (20+ files):**
- `test_component_deep_wave1.py` - 3 calls
- `test_component_and_prompts_wave1.py` - 2 calls  
- `test_component_more_wave1.py` - 3 calls
- `test_coverage_improvement.py` - 2 calls
- `test_core_component.py` - 4 calls
- `test_core_component_extra.py` - 2 calls
- And 14+ more test files...

### 🎯 **Dependency Injection Target Areas**

#### **Primary Target: Component.create_questionary_component()**
- **Current**: 87 lines of complex resolution
- **Target**: 5-10 lines of simple factory usage
- **Benefits**: 90% complexity reduction

#### **Secondary Target: Test Infrastructure**
- **Current**: Complex `setup_questionary_mocks()` system
- **Target**: Simple `set_questionary_factory(mock)` calls
- **Benefits**: Standard testing patterns

#### **Tertiary Target: Runtime Module**
- **Current**: `_runtime.py` with its own resolution logic
- **Target**: Remove entirely or simplify drastically
- **Benefits**: Less infrastructure to maintain

### 🔧 **Proposed DI Interface Design**

Based on the analysis, here's the optimal approach:

#### **Module-Level Factory Pattern**
```python
# Global factory that can be overridden
_questionary_factory = None

def set_questionary_factory(factory):
    """Set questionary factory for dependency injection."""
    global _questionary_factory
    _questionary_factory = factory

def get_questionary_factory():
    """Get current questionary factory."""
    if _questionary_factory is not None:
        return _questionary_factory
    # Default: import real questionary
    import questionary
    return questionary

class Component:
    def create_questionary_component(self) -> Any:
        """Create questionary component using injected factory."""
        factory = get_questionary_factory()
        
        # Validate component type
        supported = {"text", "select", "confirm", "password", "checkbox", "autocomplete", "path"}
        if self.component_type not in supported:
            raise ValueError(f"Unsupported component type: {self.component_type}")
        
        # Get component function and call it
        component_func = getattr(factory, self.component_type)
        return component_func(**self.questionary_config)
```

### ✅ **Key Insights from Analysis**

1. **Single Bottleneck**: All complexity is in `Component.create_questionary_component()`
2. **Wide Usage**: 20+ test files directly call this method  
3. **Clean Boundaries**: QuestionaryBridge and other consumers don't need changes
4. **Testable Design**: Module-level DI provides clean testing interface
5. **Backward Compatible**: Can implement alongside existing system

### 📈 **Expected Transformation**

| Metric | Current | After DI | Improvement |
|--------|---------|----------|-------------|
| **Resolution Lines** | 87 lines | 8 lines | 90% reduction |
| **Exception Handling** | 6 try/except blocks | 0-1 blocks | Massive simplification |
| **Test Complexity** | Complex mock setup | `set_factory(mock)` | Standard patterns |
| **Import Dependencies** | `importlib`, `sys`, `globals()` | None | Cleaner dependencies |
| **Runtime Overhead** | 4 resolution attempts per call | 1 factory lookup | Better performance |

### 🎯 **Next Phase Ready**
**Phase 1A Complete!** ✅

The architecture analysis reveals that dependency injection will provide massive simplification with minimal API disruption. The single `create_questionary_component()` method contains 90% of the complexity that can be eliminated.

**Ready for Phase 1B: Design DI Interface** 🚀