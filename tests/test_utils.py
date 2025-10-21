"""Tests for utilities module."""

from datetime import date

from questionary_extended.utils import (
    center_text,
    create_progress_bar,
    format_date,
    format_number,
    fuzzy_match,
    parse_color,
    parse_date,
    parse_number,
    render_markdown,
    truncate_text,
    validate_email,
    validate_url,
    wrap_text,
)


class TestDateUtils:
    """Test date utility functions."""

    def test_format_date(self):
        test_date = date(2023, 12, 25)
        assert format_date(test_date) == "2023-12-25"
        assert format_date(test_date, "%B %d, %Y") == "December 25, 2023"

    def test_parse_date(self):
        parsed = parse_date("2023-12-25")
        assert parsed == date(2023, 12, 25)

        parsed = parse_date("25/12/2023", "%d/%m/%Y")
        assert parsed == date(2023, 12, 25)


class TestNumberUtils:
    """Test number utility functions."""

    def test_format_number(self):
        assert format_number(1234) == "1234"
        assert format_number(1234.56, decimal_places=2) == "1234.56"
        assert format_number(1234, thousands_sep=True) == "1,234"
        assert format_number(50, percentage=True) == "50.0%"
        assert format_number(99.99, currency="$") == "$99.99"

    def test_parse_number(self):
        assert parse_number("42") == 42.0
        assert parse_number("42", allow_float=False) == 42
        assert parse_number("$1,234.56") == 1234.56
        assert parse_number("75%") == 75.0


class TestColorUtils:
    """Test color utility functions."""

    def test_parse_hex_color(self):
        color = parse_color("#ff0000")
        assert color.hex == "#ff0000"
        assert color.rgb == (255, 0, 0)

    def test_parse_named_color(self):
        color = parse_color("red")
        assert color.hex == "#ff0000"
        assert color.rgb == (255, 0, 0)

    def test_parse_rgb_color(self):
        color = parse_color("rgb(255, 0, 0)")
        assert color.hex == "#ff0000"
        assert color.rgb == (255, 0, 0)


class TestTextUtils:
    """Test text utility functions."""

    def test_render_markdown(self):
        text = "**bold** and *italic*"
        result = render_markdown(text)
        # Check that ANSI codes are added (simplified test)
        assert "\033[1m" in result  # Bold
        assert "\033[3m" in result  # Italic

    def test_truncate_text(self):
        text = "This is a long text"
        assert truncate_text(text, 10) == "This is..."
        assert truncate_text(text, 20) == text  # No truncation needed

    def test_wrap_text(self):
        text = "This is a long line that should be wrapped"
        lines = wrap_text(text, 10)
        assert len(lines) > 1
        assert all(len(line) <= 10 for line in lines)

    def test_center_text(self):
        result = center_text("hello", 10)
        assert result == "  hello   "
        assert len(result) == 10


class TestProgressUtils:
    """Test progress utility functions."""

    def test_create_progress_bar(self):
        bar = create_progress_bar(50, 100, width=10)
        assert "[" in bar
        assert "]" in bar
        assert "50/100" in bar
        assert "50.0%" in bar

    def test_create_progress_bar_complete(self):
        bar = create_progress_bar(100, 100, width=10)
        assert "100.0%" in bar


class TestFuzzyMatch:
    """Test fuzzy matching functionality."""

    def test_fuzzy_match_exact(self):
        choices = ["apple", "banana", "cherry"]
        matches = fuzzy_match("apple", choices)
        assert len(matches) > 0
        assert matches[0][0] == "apple"
        assert matches[0][1] == 1.0  # Exact match

    def test_fuzzy_match_partial(self):
        choices = ["application", "banana", "cherry"]
        matches = fuzzy_match("app", choices)
        assert len(matches) > 0
        # Should find "application"
        assert any("application" in match[0] for match in matches)

    def test_fuzzy_match_threshold(self):
        choices = ["apple", "banana", "cherry"]
        matches = fuzzy_match("xyz", choices, threshold=0.9)
        # Should find no matches with high threshold
        assert len(matches) == 0


class TestValidationUtils:
    """Test validation utility functions."""

    def test_validate_email(self):
        assert validate_email("user@example.com") is True
        assert validate_email("invalid-email") is False
        assert validate_email("user@") is False
        assert validate_email("@example.com") is False

    def test_validate_url(self):
        assert validate_url("https://example.com") is True
        assert validate_url("http://example.com") is True
        assert validate_url("not-a-url") is False
        assert validate_url("ftp://example.com") is False
