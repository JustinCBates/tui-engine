"""Core utilities testing - basic functionality (date, number, color, text operations)."""

import pytest
from datetime import date
from questionary_extended.utils import (
    format_date,
    parse_date,
    format_number,
    parse_number,
    parse_color,
    render_markdown,
    truncate_text,
    wrap_text,
    center_text,
)


class TestDateUtils:
    """Test date formatting and parsing utilities."""

    def test_format_date(self):
        d = date(2021, 12, 31)
        assert format_date(d) == "2021-12-31"

    def test_parse_date(self):
        d = parse_date("2021-12-31")
        assert d == date(2021, 12, 31)


class TestNumberUtils:
    """Test number formatting and parsing utilities."""

    def test_format_number_basic(self):
        assert format_number(123) == "123"
        assert format_number(1234, thousands_sep=True).startswith("1,234")
        assert format_number(12.3456, decimal_places=2) == "12.35"

    def test_format_number_percentage(self):
        result = format_number(0.5, percentage=True)
        assert result.endswith("%")
        assert "0.5" in result or "50" in result

    def test_format_number_currency(self):
        result = format_number(1000, currency="$")
        assert result.startswith("$")
        assert "1000" in result

    def test_parse_number_basic(self):
        assert parse_number("1,234") == 1234.0
        assert parse_number("42", allow_float=False) == 42
        assert abs(parse_number("12.34") - 12.34) < 1e-9

    def test_parse_number_percentage(self):
        assert parse_number("50%") == 50.0


class TestColorUtils:
    """Test color parsing utilities."""

    def test_parse_hex_color(self):
        color = parse_color("#ff0000")
        assert color.hex.lower() == "#ff0000"

    def test_parse_named_color(self):
        color = parse_color("blue")
        assert color.hex.lower() == "#0000ff"

    def test_parse_rgb_color(self):
        color = parse_color("rgb(0,128,255)")
        assert color.hex.startswith("#")

    def test_parse_color_no_hash(self):
        color = parse_color("00ff00")
        assert color.hex.lower() == "#00ff00"

    def test_parse_color_invalid(self):
        # The implementation returns a default color rather than raising
        color = parse_color("invalid_color")
        assert color.hex == "#000000"  # Default fallback


class TestTextUtils:
    """Test text manipulation utilities."""

    def test_render_markdown(self):
        result = render_markdown("**bold**")
        assert "bold" in result

    def test_truncate_text(self):
        result = truncate_text("hello world", 5)
        assert len(result) <= 8  # 5 chars + "..."
        assert result.startswith("he")

    def test_wrap_text(self):
        long_text = "This is a very long line of text that should be wrapped"
        result = wrap_text(long_text, width=20)
        # wrap_text returns a list, not a string
        assert isinstance(result, list)
        assert len(result) > 1
        assert all(len(line) <= 20 for line in result)

    def test_center_text(self):
        result = center_text("hello", width=11)
        assert len(result) == 11
        assert result.strip() == "hello"