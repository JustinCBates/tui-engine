# questionary-extended Architecture Design

**Status**: ✅ **DESIGN COMPLETE** - Ready for Implementation  
**Date**: October 2025  
**Version**: 1.0 Design Specification

## Overview

The **questionary-extended** library extends the popular `questionary` CLI prompt library with sophisticated multi-page, multi-component TUI capabilities while maintaining 100% backward compatibility. This design enables everything from simple forms to complex configuration wizards with conditional logic, cross-field validation, and dynamic interfaces.

## Core Design Principles

1. **Zero-Impact Compatibility**: Existing `questionary` code continues to work unchanged
2. **Graduated Complexity**: Simple cases remain simple, complex cases become possible
3. **Event-Driven Architecture**: Reactive components with real-time feedback
4. **Hierarchical Organization**: Page → Card/Assembly → Component structure
5. **Developer Experience**: Smart APIs with fluent method chaining

## Component Architecture

### Hierarchy Overview

```
Page (Top-level container)
├── Card (Visual grouping)
│   ├── Component (questionary elements)
│   └── Assembly (Interactive component groups)
│       └── Component (nested elements)
├── Assembly (Direct page assemblies)
│   └── Component (questionary elements)
└── Component (Direct page components)
```

### Core Components

#### 1. Page

- **Purpose**: Top-level container for entire user interaction flow
- **Features**: Progress tracking, headers/footers, scrolling management
- **State**: Page-scoped state management with assembly namespacing
- **Navigation**: Smart pagination, responsive layout

#### 2. Card

- **Purpose**: Visual grouping of related components
- **Features**: Multiple styling options, dynamic show/hide, responsive layouts
- **Styles**: `minimal` (default), `bordered`, `highlighted`, `collapsible`
- **Layout**: Vertical flow with optional horizontal grouping

#### 3. Assembly

- **Purpose**: Interactive component groups with conditional logic
- **Features**: Event-driven interactions, cross-field validation, state management
- **Events**: `.on_change()`, `.on_validate()`, `.on_complete()`
- **Reusability**: Template-based assemblies for common patterns

#### 4. Component

- **Purpose**: Individual questionary elements (text, select, confirm, etc.)
- **Compatibility**: All existing questionary components supported
- **Enhancement**: Extended with conditional display, validation, styling

## Design Decisions

### 1. ✅ Component Communication

**Decision**: Page-scoped state with Assembly namespacing  
**Implementation**:

- State keys: `{assembly_name}.{field_name}` (e.g., `os.linux_family`, `web.framework`)
- Cross-boundary access: `assembly.get_related_value("other_assembly.field")`
- Local access: `assembly.get_value("local_field")`
- **Risk**: Moderate refactoring risk, mitigated by abstraction layer

### 2. ✅ Visual Design System

**Decision**: Zero-impact backward compatibility with opt-in enhancements  
**Implementation**:

- `import questionary` remains unchanged
- `import questionary_extended as qe` for new features
- New components default to questionary visual style
- Enhanced styling requires explicit opt-in
- **Risk**: Low - no impact on existing code

### 3. ✅ Method Chaining Patterns

**Decision**: Smart context-aware chaining with escape hatches  
**Implementation**:

- Page methods return Page objects
- Card methods return Card objects
- Escape hatches: `.parent()`, `.get_card()`, `.get_assembly()`
- **Risk**: Low - clear fallback to explicit navigation

### 4. ✅ Questionary Integration Strategy

**Decision**: Coexistence model with one-way state flow  
**Implementation**:

- `questionary.form()` unchanged, completes before qe Assemblies
- `qe.Page()` as enhanced alternative
- One-way state flow: questionary → qe only
- Flat result dictionary for backward compatibility
- **Risk**: Low - no interleaving, clear separation

### 5. ✅ Simplest Assembly Example

**Decision**: Event-driven Assembly with hooks and composability  
**Implementation**:

```python
app_config = qe.Assembly("app_config")
  .select("app_type", ["web", "api", "cli"])
  .on_change("app_type", lambda value, assembly:
      assembly.show_components(["framework"]) if value == "web"
      else assembly.hide_components(["framework"])
  )
  .select("framework", ["flask", "django"], when="app_type == 'web'")
```

- **Risk**: Low - clear event model with manageable complexity

### 6. ✅ Error Handling Strategy

**Decision**: Multi-layer validation with graceful degradation  
**Implementation**:

- **Layer 1**: Component-level immediate feedback (questionary-compatible validators)
- **Layer 2**: Assembly-level cross-field validation
- **Layer 3**: Page-level comprehensive validation
- **Missing References**: Graceful degradation with warnings
- **Error Mode**: Collect-and-report with rich debugging context
- **Risk**: Medium - complex system, mitigated by layered approach

### 7. ✅ Page Design & Layout

**Decision**: Vertical flow with smart spacing and dynamic content  
**Implementation**:

- Automatic 1-line spacing between cards/components
- No extra spacing within cards
- Auto-scrolling via questionary's built-in system
- Smart pagination at card boundaries
- Dynamic show/hide with reactive updates
- Optional headers/footers/progress bars
- **Risk**: Low - builds on questionary's proven layout system

### 8. ✅ Card Structure & Behavior

**Decision**: Multiple visual styles with responsive layouts  
**Implementation**:

- Visual styles: `minimal`, `bordered`, `highlighted`, `collapsible`
- Dynamic show/hide with smooth transitions
- Horizontal grouping with responsive fallback to vertical
- Overflow scrolling within card boundaries
- **Risk**: Medium - responsive behavior complexity, mitigated by graceful degradation

### 9. ✅ Assembly Interaction Logic

**Decision**: Four interaction types with reusable templates  
**Implementation**:

- **Decision Trees**: Simple conditional logic with `when` conditions
- **Dependent Dropdowns**: Cascading selections with dynamic options
- **Cross-Field Validation**: Complex validation requiring field coordination
- **Conditional Logic**: Dynamic component visibility and behavior
- **Update Timing**: Real-time (`on_change`) vs event-triggered (`on_complete`)
- **Reusability**: Template functions returning configured assemblies
- **Risk**: Medium - complexity managed by clear interaction patterns

## API Design Examples

### Basic Usage (Questionary Compatible)

```python
import questionary_extended as qe

# Simple form - similar to questionary.form()
result = qe.Page("Configuration")
  .text("app_name")
  .select("app_type", ["web", "api", "cli"])
  .run()

print(result)  # {"app_name": "MyApp", "app_type": "web"}
```

### Enhanced Multi-Page Wizard

```python
# Complex configuration wizard
config_page = qe.Page("Application Setup")
  .progress_bar(current=1, total=3)

  .card("Application Settings")
    .text("app_name", validator=qe.validators.required)
    .select("app_type", ["web", "api", "worker"])

  .assembly("web_config")
    .select("framework", ["flask", "django", "fastapi"], when="app_type == 'web'")
    .text("port", when="app_type == 'web'", default="8000")
    .on_change("framework", lambda value, assembly:
        assembly.show_card("advanced_web") if value == "django"
        else assembly.hide_card("advanced_web")
    )

  .card("advanced_web", style="collapsible")
    .text("django_secret_key", when="web_config.framework == 'django'")
    .checkbox("debug_mode", when="web_config.framework == 'django'")

result = config_page.run()
```

### Assembly Reusability

```python
def database_assembly():
    return qe.Assembly("database")
      .select("db_type", ["postgresql", "mysql", "sqlite"])
      .text("host", when="db_type != 'sqlite'", default="localhost")
      .text("port", when="db_type != 'sqlite'")
      .on_validate(lambda assembly: validate_db_connection(assembly.get_values()))

# Reuse across pages
setup_page.add_assembly(database_assembly())
review_page.add_assembly(database_assembly().readonly())
```

## Implementation Considerations

### Backward Compatibility Strategy

1. **Import Isolation**: `questionary` imports unchanged
2. **Namespace Separation**: `questionary_extended` as separate module
3. **Result Format**: Maintain flat dictionary structure
4. **Component Behavior**: questionary components work identically

### Performance Considerations

1. **Lazy Loading**: Components created only when accessed
2. **Event Debouncing**: Real-time updates with configurable delays
3. **Memory Management**: Efficient state storage and cleanup
4. **Rendering Optimization**: Incremental updates, not full re-renders

### Testing Strategy

1. **Compatibility Tests**: Ensure questionary behavior unchanged
2. **Integration Tests**: Multi-component interaction scenarios
3. **Visual Tests**: Layout and styling verification
4. **Performance Tests**: Large form handling and responsiveness

## Migration Path

### For Existing Questionary Users

1. **Phase 1**: No changes required - existing code works
2. **Phase 2**: Optional enhancement - add `questionary_extended` import
3. **Phase 3**: Gradual adoption - migrate complex forms to Pages/Cards/Assemblies
4. **Phase 4**: Advanced features - leverage full event-driven capabilities

### Migration Examples

```python
# Before: questionary.form()
result = questionary.form(
    app_name=questionary.text("Application name"),
    app_type=questionary.select("Type", ["web", "api"])
).ask()

# After: Enhanced with conditional logic
result = qe.Page("Configuration")
  .text("app_name")
  .select("app_type", ["web", "api"])
  .text("port", when="app_type == 'web'", default="8000")
  .run()
```

## Risk Assessment

| Component               | Risk Level | Mitigation Strategy                        |
| ----------------------- | ---------- | ------------------------------------------ |
| Component Communication | Medium     | Abstraction layer with clear APIs          |
| Visual Design System    | Low        | Opt-in enhancements, no breaking changes   |
| Method Chaining         | Low        | Escape hatches for complex navigation      |
| Questionary Integration | Low        | Clear separation, no interleaving          |
| Assembly Events         | Low        | Well-defined event model                   |
| Error Handling          | Medium     | Layered approach with graceful degradation |
| Page Layout             | Low        | Build on questionary's proven system       |
| Card Behavior           | Medium     | Responsive design with fallbacks           |
| Assembly Logic          | Medium     | Clear interaction patterns, template reuse |

## Success Criteria

1. **✅ Backward Compatibility**: 100% of existing questionary code works unchanged
2. **✅ Enhanced Capabilities**: Complex multi-page wizards with conditional logic
3. **✅ Developer Experience**: Intuitive APIs with smart defaults
4. **✅ Performance**: Responsive interactions even with complex forms
5. **✅ Maintainability**: Clear architecture with separated concerns
6. **✅ Extensibility**: Easy to add new component types and interaction patterns

---

**Next Phase**: [Implementation Plan](implementation-plan.md) - Detailed development roadmap and milestone breakdown.
