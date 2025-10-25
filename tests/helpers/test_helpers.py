"""Test helpers and utilities for the test suite."""

import pytest
import os


def skip_if_coverage_excluded(func):
    """Skip test if coverage is excluded or module is not available."""
    try:
        # Check if we're running in a coverage context
        if os.environ.get('COVERAGE_PROCESS_START'):
            return pytest.mark.skip("Skipping test when coverage is active")(func)
        return func
    except Exception:
        return pytest.mark.skip("Coverage configuration not available")(func)


def mock_terminal_input(input_text: str):
    """Mock terminal input for testing interactive components."""
    # This is a placeholder for terminal input mocking
    # In actual implementation, this would mock the prompt_toolkit input
    pass


def assert_output_contains(output: str, expected: str):
    """Assert that output contains expected text."""
    assert expected in output, f"Expected '{expected}' in output: {output}"


def assert_no_errors_in_output(output: str):
    """Assert that output doesn't contain error indicators."""
    error_indicators = ["Error", "Exception", "Traceback", "ERROR"]
    for indicator in error_indicators:
        assert indicator not in output, f"Found error indicator '{indicator}' in output: {output}"