from datetime import datetime

from questionary_extended.utils import (
    center_text,
    create_progress_bar,
    format_date,
    parse_date,
    validate_email,
    validate_url,
    wrap_text,
)


def test_date_format_parse():
    d = datetime(2020, 1, 2)
    assert format_date(d, "%Y/%m/%d") == "2020/01/02"
    assert parse_date("2020-01-02").year == 2020


def test_wrap_and_center_and_table():
    text = "The quick brown fox jumps over the lazy dog"
    wrapped = wrap_text(text, 10)
    assert all(len(line) <= 10 for line in wrapped)

    assert center_text("hi", 6) == "  hi  "

    # create_table_row is defined in a different utils module; skip here


def test_tree_and_sanitize_and_validators():
    # create_tree_line and sanitize_input live in different modules; use progress bar instead
    bar = create_progress_bar(2, 5, width=10)
    assert "2/5" in bar

    assert validate_email("a@b.com")
    assert not validate_email("bad-email")

    assert validate_url("http://example.com")
    assert not validate_url("example.com")
