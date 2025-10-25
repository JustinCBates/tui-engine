from pathlib import Path
from datetime import date
from tests.helpers.test_helpers import load_module_from_path

# load utils via centralized helper
utils = load_module_from_path(
    "questionary_extended.utils", Path("src/questionary_extended/utils.py").resolve()
)


def test_format_and_parse_date():
    d = utils.format_date(date(2020, 1, 2))
    assert d == "2020-01-02"
    pd = utils.parse_date("2020-01-02")
    assert pd == date(2020, 1, 2)


def test_format_number_variants():
    s = utils.format_number(1234.5, decimal_places=2, thousands_sep=True, currency="$")
    assert s.startswith("$")
    assert "," in s or s.count("$")

    p = utils.format_number(12.345, percentage=True)
    assert p.endswith("%")


def test_parse_number_allow_float_and_int():
    assert isinstance(utils.parse_number("1,234.50"), float)
    assert utils.parse_number("100%", allow_float=True) == 100.0
    assert utils.parse_number("42", allow_float=False) == 42


def test_parse_color_hex_named_and_rgb():
    ci = utils.parse_color("#ff0000")
    # Don't rely on class identity (modules may be loaded separately in tests).
    assert hasattr(ci, "hex") and ci.hex.lower() == "#ff0000"

    ci2 = utils.parse_color("red")
    assert ci2.hex.lower() == "#ff0000"

    ci3 = utils.parse_color("rgb(0,128,255)")
    assert ci3.rgb == (0, 128, 255)


def test_truncate_wrap_center_and_progress():
    t = "hello world"
    assert utils.truncate_text(t, 5).endswith("...")
    lines = utils.wrap_text("a b c d e f", 3)
    assert isinstance(lines, list)
    centered = utils.center_text("x", 3)
    assert centered.strip() == "x"
    bar = utils.create_progress_bar(2, 4, width=4)
    assert "[" in bar and "2/4" in bar


def test_create_table_row_and_tree_line_and_sanitize():
    row = utils.create_table_row(["a", "b"], [5, 5])
    assert "|" in row
    line = utils.create_tree_line("node", level=1, is_last=True, has_children=True, expanded=False)
    assert "node" in line
    sanitized = utils.sanitize_input("x\x00y")
    assert "\x00" not in sanitized


def test_wrap_long_word_and_table_truncate_and_sanitize_allowed_chars():
    # long word longer than width should be cut
    long = "verylongword"
    wrapped = utils.wrap_text(long, 4)
    assert any(len(l) <= 4 for l in wrapped)

    # table row truncates cell content when too long
    row2 = utils.create_table_row(["thisislong"], [6], padding=1)
    assert "this" in row2 or "..." in row2

    # sanitize with allowed chars keeps only those
    s2 = utils.sanitize_input("abc123!", allowed_chars="abc123")
    assert s2 == "abc123"


def test_parse_color_no_hash_and_invalid():
    ci = utils.parse_color("ff0000")
    assert hasattr(ci, "hex") and ci.hex.lower() == "#ff0000"

    # invalid color should raise
    try:
        utils.parse_color("notacolor!!")
        assert False
    except ValueError:
        pass


def test_render_markdown_headers_and_code():
    s = "# Title\nSome `code` and **bold**"
    out = utils.render_markdown(s)
    assert "Title" in out
    assert "\033[1m" in out or "\033[2m" in out


def test_fuzzy_email_url_and_range():
    matches = utils.fuzzy_match("a", ["a", "b", "abc"], threshold=0.5)
    assert any(m[0] == "a" for m in matches)
    assert utils.validate_email("test@example.com") is True
    assert utils.validate_email("bad@") is False
    assert utils.validate_url("http://example.com") is True
    assert utils.validate_url("ftp://example.com") is False
    choices = utils.generate_choices_from_range(1, 3, 1)
    assert choices == ["1", "2", "3"]
