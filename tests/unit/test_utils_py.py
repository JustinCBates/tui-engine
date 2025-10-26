import pathlib
from datetime import date

import pytest

# Load the file-based utils module (src/questionary_extended/utils.py) directly
ROOT = pathlib.Path(__file__).resolve().parents[2]
UTILS_PATH = ROOT / "src" / "questionary_extended" / "utils.py"
# Load utils via centralized helper to ensure package resolution
from tests.helpers.test_helpers import load_module_from_path

utils = load_module_from_path("questionary_extended.utils", UTILS_PATH)


def test_date_format_and_parse():
    d = date(2020, 1, 2)
    s = utils.format_date(d, "%Y/%m/%d")
    assert s == "2020/01/02"

    parsed = utils.parse_date("2020/01/02", "%Y/%m/%d")
    assert parsed == d


def test_number_format_and_parse():
    assert utils.format_number(1234.567, decimal_places=2) == "1234.57"
    assert utils.format_number(1234.5, thousands_sep=True) == "1,234.5"
    assert utils.format_number(0.1234, percentage=True, decimal_places=1) == "0.1%"
    assert utils.format_number(10, currency="$") == "$10"

    assert utils.parse_number("1,234.5") == 1234.5
    assert utils.parse_number("42", allow_float=False) == 42


def test_parse_color_variants():
    # Hex with #
    c = utils.parse_color("#ff00ff")
    assert c.hex.lower() == "#ff00ff"

    # Named color
    c2 = utils.parse_color("Red")
    assert c2.hex.lower() == "#ff0000"

    # rgb() format
    c3 = utils.parse_color("rgb(0, 128, 255)")
    assert c3.hex.lower() == "#0080ff"

    # hex without #
    c4 = utils.parse_color("00ff00")
    assert c4.hex.lower() == "#00ff00"

    # invalid color raises
    with pytest.raises(ValueError):
        utils.parse_color("not-a-color-xyz")


def test_render_markdown_and_truncate_wrap_center():
    s = "**bold** and *italic* and `code`\n# Header"
    rendered = utils.render_markdown(s)
    # ANSI sequences should be present for bold/italic/code and header
    assert "\033[1m" in rendered
    assert "\033[3m" in rendered
    assert "\033[2m" in rendered

    assert utils.truncate_text("hello", 10) == "hello"
    assert utils.truncate_text("hello world", 5) == "he..."

    wrapped = utils.wrap_text("one two three", 5)
    assert isinstance(wrapped, list)
    # word longer than width
    longwrap = utils.wrap_text("supercalifragilisticexpialidocious", 5)
    assert any(len(line) <= 5 for line in longwrap)

    centered = utils.center_text("x", 3, "-")
    assert centered == "-x-"


def test_progress_table_tree():
    p = utils.create_progress_bar(3, 5, width=10)
    assert "[" in p and "]" in p and "3/5" in p

    row = utils.create_table_row(["a", "bc"], [6, 6])
    assert row.startswith("|") and row.endswith("|")

    t1 = utils.create_tree_line("root", 0)
    assert t1 == "root"
    t2 = utils.create_tree_line("leaf", 2, is_last=True, has_children=False)
    assert "└──" in t2 or "├──" in t2


def test_sanitize_and_fuzzy_and_validators():
    s = utils.sanitize_input("abc\x00def\x07")
    assert "\x00" not in s

    s2 = utils.sanitize_input("abc!@#", allowed_chars="abc")
    assert s2 == "abc"

    choices = ["Alpha", "Beta", "Gamma"]
    matches = utils.fuzzy_match("Al", choices, threshold=0.5)
    assert any(m[0] == "Alpha" for m in matches)

    assert utils.validate_email("test@example.com")
    assert not utils.validate_email("not-an-email")

    assert utils.validate_url("http://example.com")
    assert not utils.validate_url("ftp://example.com")


def test_generate_choices_from_range():
    c = utils.generate_choices_from_range(1, 3)
    assert c == ["1", "2", "3"]

    c2 = utils.generate_choices_from_range(
        0.0, 0.5, step=0.25, format_fn=lambda v: f"{v:.2f}"
    )
    assert c2[0] == "0.00" and c2[-1] == "0.50"
