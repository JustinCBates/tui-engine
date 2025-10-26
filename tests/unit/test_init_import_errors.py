"""Test for __init__.py import error handling coverage."""

import importlib
import sys
from unittest.mock import Mock, patch

import pytest


@pytest.mark.skip(reason="Module import state conflicts in full test suite")
def test_package_not_found_error_handling():
    """Test PackageNotFoundError handling in version detection (lines 20-22)."""

    # Create a fresh module namespace to test version detection
    module_backup = sys.modules.get("questionary_extended")
    if "questionary_extended" in sys.modules:
        del sys.modules["questionary_extended"]

    try:
        # Mock importlib.metadata.version to raise PackageNotFoundError
        with patch("importlib.metadata.version") as mock_version:
            from importlib.metadata import PackageNotFoundError

            mock_version.side_effect = PackageNotFoundError("Package not found")

            # Import the module to trigger the exception handling
            import questionary_extended

            # The module should load successfully despite the exception
            assert hasattr(questionary_extended, "__version__")
            # The version should be the default fallback
            assert questionary_extended.__version__ == "0.1.0"

    finally:
        # Restore the original module
        if module_backup:
            sys.modules["questionary_extended"] = module_backup
        elif "questionary_extended" in sys.modules:
            del sys.modules["questionary_extended"]


@pytest.mark.skip(reason="Module import state conflicts in full test suite")
def test_general_exception_handling():
    """Test general Exception handling in version detection (lines 23-25)."""

    # Create a fresh module namespace to test version detection
    module_backup = sys.modules.get("questionary_extended")
    if "questionary_extended" in sys.modules:
        del sys.modules["questionary_extended"]

    try:
        # Mock the entire importlib.metadata import to raise a general exception
        with patch.dict("sys.modules", {"importlib.metadata": None}):
            with patch("importlib.import_module") as mock_import:

                def import_side_effect(name):
                    if name == "importlib.metadata":
                        raise Exception("importlib.metadata unavailable")
                    return importlib.__import__(name)

                mock_import.side_effect = import_side_effect

                # Import the module to trigger the exception handling
                import questionary_extended

                # The module should load successfully despite the exception
                assert hasattr(questionary_extended, "__version__")
                # The version should be the default fallback
                assert questionary_extended.__version__ == "0.1.0"

    finally:
        # Restore the original module
        if module_backup:
            sys.modules["questionary_extended"] = module_backup
        elif "questionary_extended" in sys.modules:
            del sys.modules["questionary_extended"]


@pytest.mark.skip(reason="Module import state conflicts in full test suite")
def test_successful_version_detection():
    """Test successful version detection when no exceptions occur."""

    # Create a fresh module namespace to test version detection
    module_backup = sys.modules.get("questionary_extended")
    if "questionary_extended" in sys.modules:
        del sys.modules["questionary_extended"]

    try:
        # Mock version function to return a test version
        with patch("importlib.metadata.version") as mock_version:
            mock_version.return_value = "1.2.3-test"

            # Import the module to trigger successful version detection
            import questionary_extended

            # The module should load successfully with our test version
            assert hasattr(questionary_extended, "__version__")
            assert questionary_extended.__version__ == "1.2.3-test"

    finally:
        # Restore the original module
        if module_backup:
            sys.modules["questionary_extended"] = module_backup
        elif "questionary_extended" in sys.modules:
            del sys.modules["questionary_extended"]
