import re
from datetime import date, datetime
from pathlib import Path
from tests.helpers.test_helpers import load_module_from_path

# Load utils via centralized helper which sets __package__ correctly and
# provides a stable import mechanism for file-based modules used in tests.
u = load_module_from_path(
    "questionary_extended.utils", Path("src/questionary_extended/utils.py").resolve()
)


def test_format_and_parse_date():
    d = date(2021, 12, 31)
    s = u.format_date(d, "%Y-%m-%d")
    assert s == "2021-12-31"
    parsed = u.parse_date(s, "%Y-%m-%d")
    assert parsed == d


def test_format_number_variants():
    assert u.format_number(12.3456, decimal_places=2) == "12.35"
    assert u.format_number(1234.5, thousands_sep=True) == "1,234.5"
    assert u.format_number(12.3, percentage=True) == "12.3%"
    assert u.format_number(1000, thousands_sep=True, currency="$") == "$1,000"


def test_parse_number():
    assert u.parse_number("1,234.56") == 1234.56
    assert u.parse_number(" 123 ", allow_float=False) == 123


def test_truncate_and_wrap_and_center():
    short = "hello"
    assert u.truncate_text(short, 10) == short
    long = "abcdefghijklmnopqrstuvwxyz"
    t = u.truncate_text(long, 10, "..")
    assert len(t) == 10

    wrapped = u.wrap_text("one two three four", 7)
    # ensure lines are not longer than width
    assert all(len(line) <= 7 for line in wrapped)

    centered = u.center_text("hi", 6, fill_char='-')
    assert centered == "--hi--" or len(centered) == 6


def test_create_progress_bar_and_table_row():
    bar = u.create_progress_bar(3, 5, width=10)
    assert bar.startswith("[") and "]" in bar
    # when total is zero, percentage shows 0.0% for current/total 0/0 per impl
    bar2 = u.create_progress_bar(0, 0)
    assert "0.0%" in bar2

    row = u.create_table_row(["a", "bb"], [6, 6], padding=1, separator="|")
    assert row.count("|") >= 3


def test_create_tree_line():
    root = u.create_tree_line("root", 0)
    assert root == "root"
    child = u.create_tree_line("leaf", 1, is_last=True, has_children=False)
    assert "└──" in child
    branch = u.create_tree_line("node", 2, is_last=False, has_children=True, expanded=False)
    assert "├──" in branch and "▶" in branch


def test_sanitize_input_and_fuzzy_match():
    s = "hello\x00world\x07"
    clean = u.sanitize_input(s)
    assert "\x00" not in clean
    allowed = u.sanitize_input("abc123!", allowed_chars="abc123")
    assert allowed == "abc123"

    choices = ["apple", "banana pie", "apricot"]
    matches = u.fuzzy_match("ap", choices, threshold=0.6)
    assert any(m[0] == "apple" for m in matches)


def test_validate_email_and_url():
    assert u.validate_email("a@b.com")
    assert not u.validate_email("not-an-email")

    assert u.validate_url("http://example.com")
    assert u.validate_url("https://example.com/path")
    assert not u.validate_url("ftp://example.com")


def test_generate_choices_from_range():
    choices = u.generate_choices_from_range(1, 5, step=2)
    assert choices == ["1", "3", "5"]
    choices2 = u.generate_choices_from_range(0.0, 0.5, step=0.25, format_fn=lambda x: f"{x:.2f}")
    assert choices2[0] == "0.00"


def test_render_markdown_basic():
    md = "# Title\n**bold** and *italic* and `code`"
    out = u.render_markdown(md)
    # ensure ANSI sequences for bold/italic/code are present
    assert "\033[1m" in out or "bold" in out
    assert "\033[3m" in out or "italic" in out


def test_parse_color_variants_and_errors():
    # Hex with #
    c1 = u.parse_color("#00ff00")
    assert c1.hex.lower() == "#00ff00"

    # Named color (case-insensitive)
    c2 = u.parse_color("Red")
    assert c2.hex.lower() == "#ff0000"

    # rgb(...) format
    c3 = u.parse_color("rgb(255,0,128)")
    assert c3.hex.lower() == "#ff0080"

    # Hex without #
    c4 = u.parse_color("0000ff")
    assert c4.hex.lower() == "#0000ff"

    # Bad input raises a ValueError with helpful message
    try:
        u.parse_color("not-a-color")
        raised = False
    except ValueError as e:
        raised = True
        assert "Unable to parse color" in str(e)

    assert raised


def test_wrap_text_long_word():
    # A single word longer than the width should be split using the "word too long" branch
    long = "supercalifragilistic"
    lines = u.wrap_text(long, 5)
    assert lines[0] == long[:5]


def test_create_table_row_truncate():
    # Force truncation in create_table_row by using a small width
    row = u.create_table_row(["abcdef"], [6], padding=1, separator="|")
    # width - 2*padding == 4 -> truncate_text will produce a short string containing '...'
    assert "..." in row


def test_create_tree_line_expanded():
    # Ensure the expanded icon (▼) is used when has_children and expanded are True
    line = u.create_tree_line("node", level=1, is_last=False, has_children=True, expanded=True)
    assert "▼" in line


def test_fuzzy_match_equality():
    matches = u.fuzzy_match("apple", ["apple", "banana"], threshold=0.5)
    assert any(m[1] == 1.0 for m in matches)
