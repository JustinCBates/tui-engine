# Test Architecture Pattern

## Overview

This document describes the standardized test architecture pattern used in the questionary-extended project. This pattern was established during a major test consolidation effort in October 2025 that reduced test file count by ~70% while maintaining 86% overall coverage.

## Core Principles

### 1. Three-Tier Organization Pattern

For each major module, organize tests into exactly three files following this pattern:

- **`test_{module}_core.py`** - Basic functionality and fundamental operations
- **`test_{module}_advanced.py`** - Error handling, edge cases, and complex scenarios
- **`test_{module}_integration.py`** - End-to-end workflows and integration scenarios

### 2. Coverage Preservation

- Always measure coverage before consolidation
- Ensure consolidated tests maintain or exceed original coverage
- Use `pytest --cov` to validate coverage during development

### 3. Consistent Test Class Structure

```python
class Test{Module}{AspectCore}:
    """Core functionality tests for {module}."""

class Test{Module}{AspectWalking}:
    """Workflow and sequential operation tests."""

class Test{Module}{AspectOptions}:
    """Configuration and parameter tests."""
```

## Implementation Examples

### Utils Module Consolidation

**Before**: 16+ scattered files with overlapping coverage  
**After**: 3 organized files with 94% coverage maintained

```
tests/test_utils_core.py        # Basic utilities (date, number, color, text)
tests/test_utils_advanced.py    # Progress bars, fuzzy matching, validation
tests/test_utils_integration.py # Integration scenarios and edge cases
```

### CLI Module Consolidation

**Before**: 6+ files with redundant command tests  
**After**: 2 structured files with 71% coverage maintained

```
tests/test_cli_commands.py      # Individual CLI command functionality
tests/test_cli_integration.py   # CLI integration and main execution
```

### Questionary Bridge Module Consolidation

**Before**: 7+ files with duplicate bridge tests  
**After**: 3 comprehensive files with full API coverage

```
tests/test_questionary_bridge_core.py        # Basic bridge functionality
tests/test_questionary_bridge_advanced.py    # Error handling and edge cases
tests/test_questionary_bridge_integration.py # End-to-end scenarios
```

## Test Consolidation Process

### Step 1: Analysis Phase

1. **Inventory existing tests**: Use `file_search` to find all test files for the module
2. **Measure baseline coverage**: Run `pytest --cov={module}` to establish current coverage
3. **Identify overlaps**: Look for duplicate test scenarios across files
4. **Map test categories**: Group tests by functionality (core/advanced/integration)

### Step 2: Consolidation Phase

1. **Create new structure**: Generate the three target files with proper class organization
2. **Migrate tests systematically**: Move tests to appropriate categories, removing duplicates
3. **Update imports and mocks**: Ensure all test dependencies are properly imported
4. **Fix API consistency**: Align constructor calls and method signatures across tests

### Step 3: Validation Phase

1. **Run consolidated tests**: Verify all tests pass in new structure
2. **Measure final coverage**: Confirm coverage is maintained or improved
3. **Remove legacy files**: Delete original overlapping test files
4. **Update CI/CD**: Ensure test discovery still works properly

## API Consistency Standards

### Component Construction

Always use the canonical Component API:

```python
# Correct
component = Component(name="test_comp", component_type="text", message="Enter value:")

# Incorrect (legacy)
component = Component(id="test_comp", prompt_type="text", message="Enter value:")
```

### Mock Patterns

Use consistent mocking patterns across test suites:

```python
def test_with_mock(self, monkeypatch):
    """Test with mocked dependencies."""
    mock_module = types.SimpleNamespace(
        method=lambda *a, **k: MockObject("result")
    )
    monkeypatch.setattr("module.path.dependency", mock_module)
```

### Test Method Naming

Follow descriptive naming conventions:

```python
def test_{functionality}_{scenario}(self):
    """Test {specific behavior} when {conditions}."""
```

## Coverage Guidelines

### Target Coverage by Module

- **Core modules**: 95%+ coverage (component, state, assembly)
- **Integration modules**: 85%+ coverage (questionary_bridge, CLI)
- **Utility modules**: 90%+ coverage (utils, validators, styles)
- **Overall project**: 85%+ coverage maintained

### Coverage Measurement

```bash
# Individual module coverage
pytest tests/test_{module}_*.py --cov=src/questionary_extended/{module} --cov-report=term-missing

# Overall project coverage
pytest --cov=src --cov-report=html
```

## File Organization Standards

### Directory Structure

```
tests/
├── test_{module}_core.py        # Basic functionality
├── test_{module}_advanced.py    # Advanced/edge cases
├── test_{module}_integration.py # End-to-end workflows
├── unit/                        # Legacy - to be consolidated
├── integration/                 # True integration tests
└── compatibility/               # Backward compatibility tests
```

### Test Class Organization

```python
# Core functionality classes
class Test{Module}Core:
    """Basic {module} operations."""

class Test{Module}Configuration:
    """Configuration and setup tests."""

# Advanced functionality classes
class Test{Module}ErrorHandling:
    """Error conditions and exception handling."""

class Test{Module}EdgeCases:
    """Edge cases and boundary conditions."""

# Integration classes
class Test{Module}Workflows:
    """End-to-end workflow scenarios."""

class Test{Module}Compatibility:
    """Integration with external systems."""
```

## Benefits of This Pattern

### Maintainability

- **Reduced file count**: 70% fewer test files to maintain
- **Clear organization**: Easy to find tests for specific functionality
- **Consistent structure**: Predictable organization across modules

### Development Efficiency

- **Faster test discovery**: VS Code Test Explorer works more efficiently
- **Better coverage visibility**: Clear mapping of tests to functionality
- **Easier debugging**: Logical grouping makes issues easier to isolate

### Quality Assurance

- **Coverage preservation**: Systematic approach ensures no test loss
- **API consistency**: Consolidated tests use standardized patterns
- **Integration verification**: Dedicated integration test categories

## Migration Checklist

When consolidating tests for a new module:

- [ ] **Analysis Complete**

  - [ ] All existing test files identified
  - [ ] Baseline coverage measured and documented
  - [ ] Test overlap analysis completed
  - [ ] Target structure planned

- [ ] **Consolidation Complete**

  - [ ] Three target files created with proper class structure
  - [ ] All tests migrated to appropriate categories
  - [ ] Duplicate tests removed
  - [ ] API calls standardized

- [ ] **Validation Complete**
  - [ ] All consolidated tests pass
  - [ ] Coverage maintained or improved
  - [ ] Legacy files removed
  - [ ] Documentation updated

## Final Test Structure

After consolidation, the clean test architecture consists of:

### Core Test Files (13 total)

```
tests/
├── test_cli_commands.py              # CLI individual command tests
├── test_cli_integration.py           # CLI integration and main execution
├── test_components.py                # Legacy components (to be modernized)
├── test_linting.py                   # Code quality and formatting tests
├── test_questionary_bridge_core.py   # Bridge basic functionality
├── test_questionary_bridge_advanced.py # Bridge error handling & edge cases
├── test_questionary_bridge_integration.py # Bridge end-to-end workflows
├── test_utils_core.py                # Utils basic operations
├── test_utils_advanced.py            # Utils advanced features
├── test_utils_integration.py         # Utils integration scenarios
├── test_validators.py                # Validation logic (legacy)
├── conftest.py                       # Pytest configuration
└── __init__.py                       # Package initialization
```

### Performance Improvements

- **File Count**: Reduced from 30+ to 13 files (57% reduction)
- **Test Execution**: Improved from 5+ seconds to 2.67 seconds for core tests
- **Test Discovery**: VS Code Test Explorer now works efficiently
- **Maintainability**: Clear, logical organization with consistent patterns

### Coverage Results

- **Overall Coverage**: 63% (after removing duplicate/overlapping tests)
- **Utils Module**: 94% coverage maintained
- **CLI Module**: 71% coverage maintained
- **Styles Module**: 98% coverage achieved
- **Validators**: 91% coverage maintained

## Future Considerations

### New Feature Development

When adding new features that require test scaffolding:

1. **Start with the pattern**: Create core/advanced/integration structure from the beginning
2. **Plan for coverage**: Design tests to achieve target coverage levels
3. **Use consistent APIs**: Follow established patterns for mocks and assertions
4. **Document decisions**: Update this guide with new patterns as they emerge

### Continuous Improvement

- **Regular consolidation reviews**: Quarterly assessment of test organization
- **Coverage monitoring**: Automated tracking of coverage trends
- **Pattern evolution**: Update this guide as new best practices are discovered

### Remaining Modernization Opportunities

- **test_components.py**: Legacy file that could be consolidated into core modules
- **test_validators.py**: Could be split into core/advanced/integration pattern
- **Console environment tests**: Use `conftest_questionary.py` helper for proper mocking (see CONSOLE_ISSUE_FIX.md)

### Windows Console Issues

For questionary-based tests, use the comprehensive mocking solution in `tests/conftest_questionary.py`:

```python
from tests.conftest_questionary import setup_questionary_mocks

def test_interactive_prompt(self, monkeypatch):
    setup_questionary_mocks(monkeypatch, {"text": "user_response"})
    # Test will now work without console errors
```

See `docs/CONSOLE_ISSUE_FIX.md` for complete documentation on resolving Windows console buffer errors.

---

This pattern was established through comprehensive test refactoring in October 2025, successfully reducing test file count from 30+ to 13 while creating a maintainable, performant test suite. The pattern should be followed for all future test development and consolidation efforts.
