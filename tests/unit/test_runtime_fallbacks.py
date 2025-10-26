"""Test for _runtime.py fallback import logic coverage."""

import importlib
import sys
from unittest.mock import Mock, patch

import pytest


def test_runtime_sys_modules_fallback():
    """Test sys.modules fallback when _QUESTIONARY is None (lines 53-56)."""

    # Import the module to test
    from src.questionary_extended import _runtime

    # Clear the cached questionary to force fallback logic
    original_questionary = _runtime._QUESTIONARY
    _runtime._QUESTIONARY = None

    try:
        # Mock sys.modules to return a questionary module
        mock_questionary = Mock()
        with patch.dict("sys.modules", {"questionary": mock_questionary}):
            result = _runtime.get_questionary()

            # Should return the mocked questionary from sys.modules
            assert result is mock_questionary
            # Should cache it
            assert _runtime._QUESTIONARY is mock_questionary

    finally:
        # Restore original state
        _runtime._QUESTIONARY = original_questionary


def test_runtime_import_module_fallback():
    """Test importlib.import_module fallback when sys.modules has no questionary (lines 57-61)."""

    from src.questionary_extended import _runtime

    # Clear the cached questionary to force fallback logic
    original_questionary = _runtime._QUESTIONARY
    _runtime._QUESTIONARY = None

    try:
        # Mock sys.modules to return None (no questionary in sys.modules)
        with patch.dict("sys.modules", {}, clear=False):
            # Remove questionary from sys.modules if it exists
            if "questionary" in sys.modules:
                del sys.modules["questionary"]

            # Mock importlib.import_module to return a questionary module
            mock_questionary = Mock()
            with patch(
                "importlib.import_module", return_value=mock_questionary
            ) as mock_import:
                result = _runtime.get_questionary()

                # Should call import_module with "questionary"
                mock_import.assert_called_once_with("questionary")
                # Should return the imported module
                assert result is mock_questionary
                # Should cache it
                assert _runtime._QUESTIONARY is mock_questionary

    finally:
        # Restore original state
        _runtime._QUESTIONARY = original_questionary


def test_runtime_import_exception_fallback():
    """Test exception handling in import_module fallback (lines 62)."""

    from src.questionary_extended import _runtime

    # Clear the cached questionary to force fallback logic
    original_questionary = _runtime._QUESTIONARY
    _runtime._QUESTIONARY = None

    try:
        # Mock sys.modules to return None (no questionary in sys.modules)
        with patch.dict("sys.modules", {}, clear=False):
            # Remove questionary from sys.modules if it exists
            if "questionary" in sys.modules:
                del sys.modules["questionary"]

            # Mock importlib.import_module to raise an exception
            with patch(
                "importlib.import_module",
                side_effect=ImportError("questionary not found"),
            ):
                result = _runtime.get_questionary()

                # Should return None when import fails
                assert result is None
                # Should not cache anything
                assert _runtime._QUESTIONARY is None

    finally:
        # Restore original state
        _runtime._QUESTIONARY = original_questionary


def test_runtime_cached_questionary():
    """Test that cached questionary is returned when available (lines 49-50)."""

    from src.questionary_extended import _runtime

    # Set up a cached questionary
    original_questionary = _runtime._QUESTIONARY
    mock_cached = Mock()
    _runtime._QUESTIONARY = mock_cached

    try:
        result = _runtime.get_questionary()

        # Should return the cached version
        assert result is mock_cached

    finally:
        # Restore original state
        _runtime._QUESTIONARY = original_questionary
