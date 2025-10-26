from questionary_extended.utils import (
    create_progress_bar,
    format_number,
    fuzzy_match,
    parse_number,
    truncate_text,
)


def test_format_and_parse_number():
    assert format_number(1234.5, decimal_places=1, thousands_sep=True) == "1,234.5"
    assert format_number(50, percentage=True) == "50.0%"
    assert parse_number("1,234.5") == 1234.5
    assert parse_number("1234", allow_float=False) == 1234


def test_truncate_and_progress_and_fuzzy():
    assert truncate_text("hello world", 5) == "he..."

    bar = create_progress_bar(3, 10, width=10)
    assert "[" in bar and "]" in bar and "3/10" in bar

    choices = ["Alpha", "Beta", "Gamma"]
    matches = fuzzy_match("al", choices)
    assert any(name == "Alpha" for name, _ in matches)
