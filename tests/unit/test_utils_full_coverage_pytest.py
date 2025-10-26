import importlib.util
import os
from datetime import date

import pytest

# Load the standalone src/questionary_extended/utils.py module explicitly so
# tests exercise that file (there is also a utils package which provides a
# different, smaller API). This ensures coverage is measured on the intended
# module.
HERE = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SRC = os.path.join(HERE, "src", "questionary_extended")

# Load components first and register it as the package submodule so relative
# imports inside utils.py resolve to this module instead of triggering the
# package import machinery.
COMP_PATH = os.path.join(SRC, "components.py")
spec_c = importlib.util.spec_from_file_location(
    "questionary_extended.components", COMP_PATH
)
components = importlib.util.module_from_spec(spec_c)
spec_c.loader.exec_module(components)
import sys

sys.modules["questionary_extended.components"] = components

UTILS_PATH = os.path.join(SRC, "utils.py")
spec = importlib.util.spec_from_file_location("questionary_extended.utils", UTILS_PATH)
utils = importlib.util.module_from_spec(spec)
# Ensure relative imports inside the module work
utils.__package__ = "questionary_extended"
sys.modules["questionary_extended.utils"] = utils
spec.loader.exec_module(utils)

ColorInfo = components.ColorInfo


def test_format_and_parse_date():
    d = date(2020, 1, 2)
    assert utils.format_date(d) == "2020-01-02"
    assert utils.parse_date("2020-01-02") == d


def test_format_number_variants():
    assert utils.format_number(123) == "123"
    assert utils.format_number(1234, thousands_sep=True) == "1,234"
    assert utils.format_number(12.3456, decimal_places=2) == "12.35"
    assert utils.format_number(0.5, percentage=True) == "0.5%"
    assert utils.format_number(1000, currency="$") == "$1000"
    assert utils.format_number(
        1234567.89, decimal_places=2, thousands_sep=True, currency="$"
    )


def test_parse_number_int_and_float():
    assert utils.parse_number("1,234") == 1234.0
    assert utils.parse_number("42", allow_float=False) == 42


def test_parse_color_hex_and_named_and_rgb_and_invalid():
    # hex with #
    c = utils.parse_color("#ff0000")
    assert isinstance(c, ColorInfo)
    assert c.hex.lower() == "#ff0000"

    # named color
    c2 = utils.parse_color("blue")
    assert c2.hex.lower() == "#0000ff"

    # rgb format
    c3 = utils.parse_color("rgb(0,128,255)")
    assert c3.hex.startswith("#")

    # no-hash hex
    c4 = utils.parse_color("00ff00")
    assert c4.hex.lower() == "#00ff00"

    # invalid should raise
    with pytest.raises(ValueError):
        utils.parse_color("not-a-color")


def test_render_markdown_and_truncate_and_wrap_center():
    md = "**bold** *italic* `code`\n# Header\n## Sub"
    out = utils.render_markdown(md)
    assert "\033[1m" in out
    assert "\033[3m" in out
    assert "\033[2m" in out

    assert utils.truncate_text("hello", 10) == "hello"
    assert utils.truncate_text("hello world", 5) == "he..."

    # wrap text: normal wrapping and long single word
    text = "a b c d e f g"
    wrapped = utils.wrap_text(text, 3)
    assert all(len(line) <= 3 for line in wrapped)

    long_word = "abcdefghij"
    wrapped2 = utils.wrap_text(long_word, 4)
    assert any(len(line) <= 4 for line in wrapped2)

    assert utils.center_text("hi", 6, "-") == "--hi--"


def test_create_progress_bar_and_table_and_tree():
    bar = utils.create_progress_bar(5, 10, width=10, fill_char="#", empty_char=".")
    assert "[" in bar and "]" in bar

    row = utils.create_table_row(["a", "b"], [6, 6])
    assert row.count("|") == 3

    t = utils.create_tree_line(
        "node", 0, is_last=False, has_children=True, expanded=False
    )
    assert "node" in t


def test_sanitize_and_fuzzy_and_validators_and_generate_choices():
    assert utils.sanitize_input("abc\x00def") == "abcdef"
    assert utils.sanitize_input("abcXYZ", allowed_chars="abcXYZ") == "abcXYZ"

    choices = ["apple", "banana", "apricot", "blueberry"]
    matches = utils.fuzzy_match("ap", choices, threshold=0.5)
    assert any("ap" in m[0] for m in matches)

    assert utils.validate_email("a@b.com") is True
    assert utils.validate_email("not-an-email") is False

    assert utils.validate_url("http://example.com") is True
    assert utils.validate_url("ftp://example.com") is False

    rng = utils.generate_choices_from_range(1, 3, 1)
    assert rng == ["1", "2", "3"]
