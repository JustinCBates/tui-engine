# Phase 3B Migration Checklist

## Overview
This checklist provides step-by-step instructions for migrating test files from complex mocking patterns to clean DI patterns.

## Pre-Migration Setup

### ✅ Verify DI System Available
```bash
cd /home/vpsuser/projects/tui-engine
python -c "from src.tui_engine.questionary_factory import get_questionary; print('✓ DI system available')"
python -c "from tests.helpers.questionary_helpers import mock_questionary; print('✓ Test helpers available')"
```

### ✅ Backup Current Tests
```bash
# Create backup branch
git checkout -b backup-original-tests
git add -A && git commit -m "Backup: Original test patterns before DI migration"
git checkout feature/fundamental-extension-core
```

## File-by-File Migration Process

### Priority 1: Core Unit Tests (High Impact, Low Risk)

#### File 1: `tests/test_component_and_prompts_wave1.py`

**Current Patterns Found:**
- ✅ `monkeypatch.setattr(questionary, "text", fake_text)`
- ✅ Manual call verification via closure variables
- ✅ 5 test functions total

**Migration Steps:**
1. **Identify Functions to Migrate:**
   ```
   ✅ test_component_create_questionary_component_monkeypatched()
   ✅ test_component_unsupported_type_raises()
   ✅ test_prompts_text_integration()
   ✅ test_prompts_select_integration() 
   ✅ test_prompts_confirm_integration()
   ```

2. **Create New Versions:**
   ```python
   # Replace test_component_create_questionary_component_monkeypatched
   def test_component_create_questionary_component_di():
       with mock_questionary() as mock_q:
           mock_q.text.return_value = "TEXT_QUESTION"
           comp = Component("name", "text", message="hi", foo="bar")
           res = comp.create_questionary_component()
           assert res == "TEXT_QUESTION"
           mock_q.text.assert_called_once_with("name", message="hi", foo="bar")
   ```

3. **Validation:**
   ```bash
   # Run old tests
   pytest tests/test_component_and_prompts_wave1.py -v
   
   # Run new tests side-by-side
   pytest tests/test_component_and_prompts_wave1.py::test_component_create_questionary_component_di -v
   
   # Verify identical outcomes
   ```

4. **Replace Functions:**
   - Comment out old function
   - Uncomment new function
   - Update function name (remove _di suffix)
   - Run full test file

#### File 2: `tests/test_component_deep_wave1.py`

**Expected Patterns:**
- ✅ Complex component configuration testing
- ✅ Multiple questionary component types
- ✅ Error handling scenarios

**Migration Strategy:**
- Use `mock_questionary_with_types()` for multi-type tests
- Use `mock_questionary()` for single-type tests
- Use `.side_effect` for error testing

#### File 3: `tests/test_component_and_bridge_errors.py`

**Expected Patterns:**
- ✅ Error injection and handling
- ✅ Bridge component interactions
- ✅ Validation error testing

**Migration Strategy:**
- Use `mock_questionary()` with `.side_effect` for error injection
- Use `QuestionaryTestHelper` for complex error scenarios

### Priority 2: CLI Tests (High Complexity, High Impact)

#### File 4: `tests/test_cli_commands.py`

**Expected Patterns:**
- ✅ Complex CLI interaction sequences
- ✅ Multiple questionary component types
- ✅ `setup_questionary_mocks()` usage

**Migration Strategy:**
```python
# Replace complex CLI patterns with:
def test_cli_command_di():
    with mock_questionary_with_types(
        text="project_name",
        select="python",
        confirm=True
    ) as mock_q:
        result = run_cli_command(["create", "--interactive"])
        assert result.exit_code == 0
        mock_q.text.assert_called()
        mock_q.select.assert_called()
        mock_q.confirm.assert_called()
```

#### File 5: `tests/test_cli_integration.py`

**Expected Patterns:**
- ✅ End-to-end CLI workflows
- ✅ Multiple interaction sequences
- ✅ Complex state management

**Migration Strategy:**
- Use `QuestionaryTestHelper` for advanced interaction simulation
- Use `simulate_user_input_sequence()` for complex workflows

#### File 6: `tests/test_cli_wave2.py`

#### File 7: `tests/test_cli_wave2_more.py`

**Migration Strategy for CLI Tests:**
- Start with simpler CLI commands
- Use interaction simulation helpers
- Verify CLI output identical between old/new patterns

### Priority 3: Integration Tests (Lower Risk)

#### Remaining Files: All other test files using questionary mocking

**General Strategy:**
- Identify questionary usage patterns
- Apply appropriate helper based on complexity
- Verify identical behavior

## Migration Validation Process

### Step 1: Pre-Migration Test Run
```bash
# Record baseline test results
pytest tests/ --tb=short -q > pre_migration_results.txt
echo "Tests passing before migration: $(grep -c PASSED pre_migration_results.txt)"
```

### Step 2: File-by-File Validation
```bash
# For each file being migrated:
FILE="tests/test_component_and_prompts_wave1.py"

# Test old patterns
pytest $FILE -v > old_results.txt

# Test new patterns  
pytest $FILE -v > new_results.txt

# Compare results
diff old_results.txt new_results.txt
```

### Step 3: Full Suite Validation
```bash
# After completing each priority group:
pytest tests/ --tb=short -q > post_migration_results.txt
echo "Tests passing after migration: $(grep -c PASSED post_migration_results.txt)"

# Compare totals
diff pre_migration_results.txt post_migration_results.txt
```

## Common Migration Patterns

### Pattern 1: Simple Monkeypatch → Context Manager
```python
# Before
def test_old(monkeypatch):
    monkeypatch.setattr(questionary, "text", lambda **kw: "result")

# After  
def test_new():
    with mock_questionary() as mock_q:
        mock_q.text.return_value = "result"
```

### Pattern 2: Multiple Monkeypatch → Pre-configured Types
```python
# Before
def test_old(monkeypatch):
    monkeypatch.setattr(questionary, "text", lambda **kw: "text_result")
    monkeypatch.setattr(questionary, "select", lambda **kw: "select_result")

# After
def test_new():
    with mock_questionary_with_types(text="text_result", select="select_result"):
```

### Pattern 3: Complex Setup → Helper Class
```python
# Before
def test_old(monkeypatch):
    setup_questionary_mocks(monkeypatch)
    # ... complex additional setup

# After
def test_new():
    with QuestionaryTestHelper() as helper:
        helper.simulate_user_input_sequence({...})
```

## Rollback Strategy

### If Migration Issues Occur:
```bash
# Restore specific file
git checkout HEAD -- tests/problematic_file.py

# Restore all files in priority group
git checkout HEAD -- tests/test_component_*.py

# Full rollback to pre-migration state
git checkout backup-original-tests -- tests/
```

## Success Criteria

### Per-File Success:
- ✅ All tests pass with identical outcomes
- ✅ Test execution time equal or faster
- ✅ Code reduced by 40-50%
- ✅ No complex monkeypatch operations remaining

### Priority Group Success:
- ✅ Full test suite passes
- ✅ Coverage maintained or improved
- ✅ No test pollution between tests

### Overall Migration Success:
- ✅ All 20+ test files migrated
- ✅ 670+ lines of `conftest_questionary.py` no longer needed
- ✅ Standard Python testing patterns throughout
- ✅ Easier onboarding for new developers

## Timeline

### Week 1: Priority 1 (3 files)
- Day 1-2: `test_component_and_prompts_wave1.py`
- Day 3-4: `test_component_deep_wave1.py`  
- Day 5: `test_component_and_bridge_errors.py`

### Week 2: Priority 2 (4 files)
- Day 1-2: `test_cli_commands.py`
- Day 3: `test_cli_integration.py`
- Day 4: `test_cli_wave2.py`
- Day 5: `test_cli_wave2_more.py`

### Week 3: Priority 3 (Remaining files)
- Complete all remaining test files
- Final validation and cleanup

## Phase 3B Completion Criteria

✅ **All test files migrated to DI patterns**
✅ **Zero usage of complex mocking patterns**  
✅ **Full test suite passes with identical behavior**
✅ **Code complexity significantly reduced**
✅ **Ready for Phase 4A: Remove old infrastructure**

This checklist provides the systematic approach to migrate all test files from complex patterns to clean DI patterns while maintaining reliability and identical test behavior.