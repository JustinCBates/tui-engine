"""Integration testing for utilities - complex scenarios, edge cases, error handling."""

import pytest
import importlib.util
import os
import sys
from tests.helpers.test_helpers import load_module_from_path, _find_repo_root
from datetime import date
from questionary_extended.utils import (
    format_date, parse_date,
    format_number, parse_number,
    parse_color,
    render_markdown, truncate_text, wrap_text, center_text,
    create_progress_bar, fuzzy_match,
    validate_email, validate_url,
)


class TestIntegrationScenarios:
    """Test complex integration scenarios combining multiple utilities."""

    def test_number_format_parse_roundtrip(self):
        """Test that formatting and parsing numbers is consistent."""
        original = 1234.56
        formatted = format_number(original, decimal_places=2, thousands_sep=True)
        parsed = parse_number(formatted)
        assert abs(parsed - original) < 0.01

    def test_date_format_parse_roundtrip(self):
        """Test that formatting and parsing dates is consistent."""
        original = date(2023, 6, 15)
        formatted = format_date(original)
        parsed = parse_date(formatted)
        assert parsed == original

    def test_color_and_text_integration(self):
        """Test color parsing with text utilities."""
        color = parse_color("#ff0000")
        text = f"Color: {color.hex}"
        truncated = truncate_text(text, 12)
        assert color.hex in text
        assert len(truncated) <= 15  # 12 + "..."

    def test_progress_and_text_integration(self):
        """Test progress bar with text formatting."""
        progress = create_progress_bar(7, 10, width=20)
        wrapped = wrap_text(f"Task progress: {progress}", width=50)
        assert any("7" in line for line in wrapped)
        assert any("10" in line for line in wrapped)

    def test_fuzzy_match_with_validation(self):
        """Test fuzzy matching with email validation."""
        emails = ["user@example.com", "admin@test.org", "support@help.net"]
        matches = fuzzy_match("user", emails, threshold=0.3)
        
        # Validate that matched emails are actually valid
        for match, score in matches:
            if validate_email(match):
                assert "@" in match


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_inputs(self):
        """Test utilities with empty or minimal inputs."""
        assert truncate_text("", 5) == ""
        assert wrap_text("", width=10) == []  # Returns empty list
        assert center_text("", width=5) == "     "

    def test_extreme_values(self):
        """Test utilities with extreme values."""
        # Very large number
        large_num = format_number(999999999999, thousands_sep=True)
        assert "," in large_num
        
        # Very small progress
        tiny_progress = create_progress_bar(1, 1000000, width=20)
        assert isinstance(tiny_progress, str)

    def test_malformed_inputs(self):
        """Test error handling for malformed inputs."""
        with pytest.raises((ValueError, TypeError)):
            parse_number("not_a_number")
        
        with pytest.raises((ValueError, TypeError)):
            parse_date("not_a_date")
        
        # Color parsing returns default instead of raising
        result = parse_color("not_a_color")
        assert result.hex == "#000000"  # Default fallback

    def test_unicode_handling(self):
        """Test utilities with Unicode text."""
        unicode_text = "Hello 世界 🌍"
        truncated = truncate_text(unicode_text, 8)
        wrapped = wrap_text(unicode_text, width=10)
        centered = center_text("🔥", width=5)
        
        assert isinstance(truncated, str)
        assert isinstance(wrapped, list)  # wrap_text returns list
        assert isinstance(centered, str)

    def test_boundary_conditions(self):
        """Test boundary conditions."""
        # Zero width
        assert truncate_text("hello", 0) == "..."
        
        # Exact width match
        result = truncate_text("hello", 5)
        assert result == "hello"
        
        # Progress at boundaries  
        zero_progress = create_progress_bar(0, 100, width=10)
        full_progress = create_progress_bar(100, 100, width=10)
        assert isinstance(zero_progress, str)
        assert isinstance(full_progress, str)


class TestModuleIntegration:
    """Test module-level integration and imports."""

    def test_all_functions_importable(self):
        """Test that all expected functions are available."""
        from questionary_extended.utils import (
            format_date, parse_date,
            format_number, parse_number,
            parse_color,
            render_markdown, truncate_text, wrap_text, center_text,
            create_progress_bar, fuzzy_match,
            validate_email, validate_url,
        )
        
        # Ensure all functions are callable
        functions = [
            format_date, parse_date, format_number, parse_number,
            parse_color, render_markdown, truncate_text, wrap_text,
            center_text, create_progress_bar, fuzzy_match,
            validate_email, validate_url
        ]
        
        for func in functions:
            assert callable(func)

    def test_utils_module_standalone_load(self):
        """Test loading utils module independently."""
        # This tests the same pattern used in some existing test files
        here = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        src = os.path.join(here, "src", "questionary_extended")
        utils_path = os.path.join(src, "utils.py")
        
        if os.path.exists(utils_path):
            # Use centralized helper to load the file as a standalone module
            utils_module = load_module_from_path("questionary_extended._file_utils", utils_path)

            # Test a few key functions exist
            assert hasattr(utils_module, 'format_number')
            assert hasattr(utils_module, 'parse_color')
            assert hasattr(utils_module, 'fuzzy_match')