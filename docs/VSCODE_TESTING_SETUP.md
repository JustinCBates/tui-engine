# VS Code Testing Setup Guide

**Status**: ✅ **TECHNICAL REFERENCE** - VS Code Developer Environment Setup  
**Date**: October 2025  
**Referenced From**: [docs/TESTING_ARCHITECTURE.md](docs/TESTING_ARCHITECTURE.md)

This guide explains how to set up your VS Code workspace to run tests exactly like bash commands in your Docker container.

## Quick Setup Summary

Your workspace is now configured with:

1. **Python Extension** - Installed and configured
2. **Coverage Gutters** - For viewing test coverage
3. **Test Discovery** - Auto-discovery of pytest tests
4. **PATH Configuration** - Ensures pytest and tools are available
5. **Test Tasks** - Pre-configured test running tasks

## VS Code Test Browser Usage

### Method 1: Using the Test Browser (Recommended)

1. **Open Test Explorer**:
   - Press `Ctrl+Shift+P` (Command Palette)
   - Type "Test: Focus on Test Explorer View"
   - Or click the Test icon in the sidebar

2. **Refresh Tests**:
   - Click the refresh button in Test Explorer
   - Or press `Ctrl+Shift+P` → "Test: Refresh Tests"

3. **Run Tests**:
   - **All Tests**: Click play button at top of Test Explorer
   - **Specific Test**: Click play button next to individual test
   - **Test File**: Click play button next to test file
   - **Test Class**: Click play button next to test class

### Method 2: Using Tasks (Alternative)

1. **Open Command Palette**: `Ctrl+Shift+P`
2. **Type**: "Tasks: Run Task"
3. **Select one of**:
   - "Run All Tests" (with coverage)
   - "Run Tests with Coverage"
   - "Quick Test (No Coverage)"
   - "Run Current Test File"

### Method 3: Using Terminal Commands

Your bash equivalent script is available:

```bash
# Discover all tests
./test_browser_equivalent.sh discover

# Run all tests with coverage (like VS Code Test Browser)
./test_browser_equivalent.sh all

# Run specific test file
./test_browser_equivalent.sh file tests/test_validators.py

# Quick tests without coverage
./test_browser_equivalent.sh quick tests/test_validators.py

# Run specific test
./test_browser_equivalent.sh specific "tests/test_validators.py::TestNumberValidator::test_valid_integer"
```

## What VS Code Test Browser Does (Behind the Scenes)

When you click "Run Tests" in VS Code Test Browser, it executes:

```bash
cd /home/vpsuser/projects/tui-engine
export PATH="/home/vpsuser/.local/bin:$PATH"
python3 -m pytest tests \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=json \
    --cov-fail-under=85 \
    --tb=short \
    -v
```

This is **exactly** what our bash script replicates.

## Configuration Files Created

- `.vscode/settings.json` - VS Code workspace settings
- `.vscode/tasks.json` - Predefined test tasks
- `.vscode/launch.json` - Debug configurations
- `tui-engine.code-workspace` - Workspace file
- `test_browser_equivalent.sh` - Bash equivalent script

## Test Coverage

After running tests with coverage:

1. **View HTML Report**: Open `htmlcov/index.html` in browser
2. **Coverage Gutters**: Shows coverage in VS Code editor
3. **JSON Report**: Available in `coverage.json`

## Troubleshooting

### Tests Not Discovered
1. Ensure Python extension is active
2. Check that `python.testing.pytestEnabled` is `true`
3. Refresh test discovery: `Ctrl+Shift+P` → "Test: Refresh Tests"

### PATH Issues
- Terminal should automatically include `/home/vpsuser/.local/bin`
- If pytest not found, run: `export PATH="/home/vpsuser/.local/bin:$PATH"`

### Coverage Not Working
- Ensure Coverage Gutters extension is installed
- Check that `coverage.json` is generated after test run
- Reload VS Code window if coverage doesn't appear

## Verification Commands

Test your setup:

```bash
# Verify pytest is available
which pytest

# Verify Python path
python3 -c "import sys; print(sys.path)"

# Test collection
python3 -m pytest tests --collect-only

# Quick test run
python3 -m pytest tests/test_validators.py -v
```

## VS Code Test Browser Features

- ✅ **Auto-discovery** of tests
- ✅ **Individual test execution**
- ✅ **Coverage integration**
- ✅ **Debugging support**
- ✅ **Test status indicators**
- ✅ **Parallel execution** (if configured)
- ✅ **Test filtering**

Your setup now provides the **exact same functionality** as running pytest commands in bash!