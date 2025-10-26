import importlib.util
import os
import sys
from datetime import date

HERE = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SRC = os.path.join(HERE, "src", "questionary_extended")

# load components first so relative imports inside utils.py resolve
COMP_PATH = os.path.join(SRC, "components.py")
spec_c = importlib.util.spec_from_file_location(
    "questionary_extended.components", COMP_PATH
)
components = importlib.util.module_from_spec(spec_c)
spec_c.loader.exec_module(components)
sys.modules["questionary_extended.components"] = components

UTILS_PATH = os.path.join(SRC, "utils.py")
spec = importlib.util.spec_from_file_location("questionary_extended.utils", UTILS_PATH)
utils = importlib.util.module_from_spec(spec)
utils.__package__ = "questionary_extended"
sys.modules["questionary_extended.utils"] = utils
spec.loader.exec_module(utils)


def test_date_and_number_formatting_and_parsing():
    d = date(2021, 12, 31)
    assert utils.format_date(d) == "2021-12-31"
    assert utils.parse_date("2021-12-31") == d

    assert utils.format_number(123) == "123"
    assert utils.format_number(1234, thousands_sep=True).startswith("1,234")
    assert utils.format_number(12.3456, decimal_places=2) == "12.35"
    assert utils.format_number(0.5, percentage=True).endswith("%")
    assert utils.format_number(1000, currency="$").startswith("$")

    assert utils.parse_number("1,234") == 1234.0
    assert utils.parse_number("42", allow_float=False) == 42


def test_color_parsing_variants_and_errors():
    c1 = utils.parse_color("#ff0000")
    assert c1.hex.lower() == "#ff0000"
    c2 = utils.parse_color("blue")
    assert c2.hex.lower() == "#0000ff"
    c3 = utils.parse_color("rgb(0,128,255)")
    assert c3.hex.startswith("#")
    c4 = utils.parse_color("00ff00")
    assert c4.hex.lower() == "#00ff00"
    import pytest

    with pytest.raises(ValueError):
        utils.parse_color("not-a-color")


def test_render_and_truncate_wrap_center():
    md = "**b** *i* `c`\n# H\n## S"
    out = utils.render_markdown(md)
    assert "\033[1m" in out

    assert utils.truncate_text("hello", 10) == "hello"
    assert utils.truncate_text("hello world", 5) == "he..."

    wrapped = utils.wrap_text("a b c d e", 3)
    assert all(len(line) <= 3 for line in wrapped)

    long = "abcdefghij"
    wrapped2 = utils.wrap_text(long, 4)
    assert any(len(line) <= 4 for line in wrapped2)

    assert utils.center_text("hi", 6, "-") == "--hi--"


def test_progress_table_tree_and_sanitize():
    bar = utils.create_progress_bar(2, 4, width=6, fill_char="#", empty_char=".")
    assert "2/4" in bar

    row = utils.create_table_row(["hello", "world"], [6, 6])
    assert row.count("|") == 3

    t1 = utils.create_tree_line(
        "n", 0, is_last=False, has_children=True, expanded=False
    )
    assert "n" in t1

    assert utils.sanitize_input("a\x00b") == "ab"
    assert utils.sanitize_input("abc", allowed_chars="ab") == "ab"


def test_fuzzy_and_validators_and_generate_choices():
    choices = ["apple", "banana", "apricot", "blueberry"]
    m = utils.fuzzy_match("ap", choices, threshold=0.5)
    assert any("ap" in x[0] for x in m)

    assert utils.validate_email("a@b.com")
    assert not utils.validate_email("not-an-email")

    assert utils.validate_url("http://example.com")
    assert not utils.validate_url("ftp://example.com")

    rng = utils.generate_choices_from_range(1, 3, 1)
    assert rng == ["1", "2", "3"]

    rng2 = utils.generate_choices_from_range(0, 0, 1, format_fn=lambda x: f"x{x}")
    assert rng2 == ["x0"]
