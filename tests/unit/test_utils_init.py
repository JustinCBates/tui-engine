from datetime import date
from pathlib import Path

from tests.helpers.test_helpers import load_module_from_path

u = load_module_from_path(
    "questionary_extended.utils",
    Path("src/questionary_extended/utils/__init__.py").resolve(),
)


def test_format_and_parse_date_and_non_date():
    d = date(2025, 10, 22)
    assert u.format_date(d, "%Y-%m-%d") == "2025-10-22"
    assert u.parse_date("2025-10-22", "%Y-%m-%d") == d
    # Non-date input returns str
    assert u.format_date(123) == "123"


def test_format_number_behaviors():
    assert u.format_number(1234.567, decimal_places=2, thousands_sep=True) == "1,234.57"
    assert u.format_number(12.3, percentage=True) == "12.3%"
    assert u.format_number("not-a-number") == "not-a-number"
    assert u.format_number(1000, thousands_sep=True) == "1,000"
    assert u.format_number(1000, currency="$", thousands_sep=True) == "$1,000"


def test_parse_number_variants():
    assert u.parse_number("1,234.50") == 1234.5
    assert u.parse_number("50%") == 50.0
    assert u.parse_number(42) == 42
    assert u.parse_number("123", allow_float=False) == 123


def test_parse_color_variants_and_fallback():
    c1 = u.parse_color("#00ff00")
    assert c1.hex == "#00ff00" and c1.rgb == (0, 255, 0)

    c2 = u.parse_color("rgb(1,2,3)")
    assert c2.rgb == (1, 2, 3)

    c3 = u.parse_color("Red")
    assert c3.hex == "#ff0000"

    c4 = u.parse_color("notacolor")
    assert c4.hex == "#000000" and c4.rgb == (0, 0, 0)


def test_render_markdown_and_truncate_wrap_center():
    out = u.render_markdown("**bold** and *italic*")
    assert "\033[1m" in out and "\033[3m" in out

    s = "hello"
    assert u.truncate_text(s, 10) == s
    long = "a" * 10
    t = u.truncate_text(long, 5)
    assert t.endswith("...")

    wrapped = u.wrap_text("one two three", 5)
    assert isinstance(wrapped, list) and all(len(line) <= 5 for line in wrapped)

    centered = u.center_text("hi", 6)
    assert centered.strip() == "hi"


def test_create_progress_bar_and_fuzzy_match():
    bar = u.create_progress_bar(2, 4, width=10)
    assert "[" in bar and "/" in bar

    bar_zero = u.create_progress_bar(0, 0)
    assert "0/0" in bar_zero or "0/0" in bar_zero

    choices = ["apple", "application", "banana"]
    res = u.fuzzy_match("app", choices, threshold=0.5)
    assert any(r[0].startswith("app") for r in res)


def test_validate_email_and_url():
    assert u.validate_email("a@b.com")
    assert not u.validate_email("not-an-email")

    assert u.validate_url("http://example.com")
    assert u.validate_url("https://example.com/path")
    assert not u.validate_url("ftp://example.com")


def test_format_number_thousands_sep_for_float_and_parse_number_int_and_clamp():
    # thousands separator when value is float and decimal_places is None
    assert u.format_number(1234.5, thousands_sep=True) == "1,234.5"

    # parse_number with allow_float=False and integer-like float should return int
    assert u.parse_number("123.0", allow_float=False) == 123

    # parse_color rgb with out-of-range values should clamp via _clamp
    c = u.parse_color("rgb(300,5,10)")
    assert c.rgb == (255, 5, 10)


def test_parse_number_invalid_raises():
    import pytest

    with pytest.raises(ValueError):
        u.parse_number("not-a-number")
