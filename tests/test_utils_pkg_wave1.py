from questionary_extended.utils import (
    format_number,
    parse_number,
    parse_color,
    create_progress_bar,
    fuzzy_match,
    validate_email,
    validate_url,
)


def test_format_number_pkg_variants():
    assert format_number(1000, decimal_places=2, thousands_sep=True) == "1,000.00"
    assert format_number("abc") == "abc"
    assert format_number(0.5, percentage=True).endswith("%")


def test_parse_number_pkg_and_percent_and_currency():
    assert parse_number("$1,234.00") == 1234.0
    assert parse_number("50%") == 50.0
    assert parse_number(123) == 123


def test_parse_color_pkg_and_progress_and_fuzzy():
    c = parse_color("#00ff00")
    assert c.hex == "#00ff00"

    bar = create_progress_bar(2, 4, width=8)
    assert "[" in bar and "]" in bar

    res = fuzzy_match("abc", ["abc", "xabcy"], threshold=0.5)
    assert any(r[0] == "abc" for r in res)


def test_validate_pkg_helpers():
    assert validate_email("a@b.co")
    assert not validate_email("invalid")
    assert validate_url("https://x.org")
    assert not validate_url("ftp://x.org")
