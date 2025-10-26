from pathlib import Path

from tests.helpers.test_helpers import load_module_from_path


def _load_utils_module():
    module_path = (
        Path(__file__).parents[2] / "src" / "questionary_extended" / "utils.py"
    )
    mod = load_module_from_path("questionary_extended.utils", str(module_path))
    return mod


def test_date_format_and_parse():
    mod = _load_utils_module()
    from datetime import date

    d = date(2022, 3, 14)
    s = mod.format_date(d, "%Y/%m/%d")
    assert s == "2022/03/14"

    p = mod.parse_date("2022/03/14", "%Y/%m/%d")
    assert p == d


def test_format_number_variants():
    mod = _load_utils_module()
    assert mod.format_number(1234.5) == "1234.5"
    assert mod.format_number(1234.5, decimal_places=1) == "1234.5"
    assert mod.format_number(1234, thousands_sep=True) == "1,234"
    assert mod.format_number(12.3456, decimal_places=2, currency="$") == "$12.35"
    assert mod.format_number(50, percentage=True) == "50.0%"


def test_parse_number_and_ranges():
    mod = _load_utils_module()
    assert mod.parse_number("1,234") == 1234.0
    assert mod.parse_number("42", allow_float=False) == 42
    assert mod.parse_number("$5.00") == 5.0


def test_parse_color_hex_named_rgb_and_invalid():
    mod = _load_utils_module()
    # hex
    ci = mod.parse_color("#ff00ff")
    assert ci.hex.lower() == "#ff00ff"
    # named
    ci2 = mod.parse_color("Red")
    assert ci2.hex.lower() == "#ff0000"
    # rgb
    ci3 = mod.parse_color("rgb(0, 128, 255)")
    # Accept color objects that expose `.rgb` or only `.hex` (compute rgb from hex)
    if hasattr(ci3, "rgb"):
        assert ci3.rgb == (0, 128, 255)
    elif hasattr(ci3, "hex"):
        h = ci3.hex.lstrip("#")
        rgb = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        assert rgb == (0, 128, 255)
    else:
        import pytest

        pytest.fail("parse_color returned object without .rgb or .hex")

    # invalid should raise ValueError
    try:
        mod.parse_color("not-a-color")
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_render_markdown_basic():
    mod = _load_utils_module()
    txt = "# Title\nSome **bold** and *italic* with `code`"
    out = mod.render_markdown(txt)
    # ANSI codes expected for formatting
    assert "\033[1m" in out
    assert "\033[3m" in out
    assert "\033[2m" in out


def test_truncate_wrap_center():
    mod = _load_utils_module()
    assert mod.truncate_text("hello", 10) == "hello"
    assert mod.truncate_text("abcdefghijkl", 5) == "ab..."

    wrapped = mod.wrap_text("The quick brown fox", width=10)
    assert all(len(line) <= 10 for line in wrapped)

    centered = mod.center_text("hi", 6, "-")
    assert centered == "--hi--"


def test_progress_bar_and_table_and_tree():
    mod = _load_utils_module()
    bar = mod.create_progress_bar(2, 4, width=10)
    assert "[" in bar and "]" in bar

    row = mod.create_table_row(["A", "B"], [6, 6])
    assert row.count("|") == 3

    line = mod.create_tree_line("leaf", 0, is_last=True, has_children=False)
    assert line.endswith("leaf")
    line2 = mod.create_tree_line(
        "node", 1, is_last=False, has_children=True, expanded=True
    )
    assert "▼" in line2 or "▶" in line2


def test_sanitize_and_fuzzy_and_validators_and_range():
    mod = _load_utils_module()
    s = mod.sanitize_input("a\x00b\x07c")
    assert "\x00" not in s and "\x07" not in s

    s2 = mod.sanitize_input("abc123", allowed_chars="abc123")
    assert s2 == "abc123"

    matches = mod.fuzzy_match("qui", ["quick", "slow", "quiet"], threshold=0.6)
    assert any(m[0] == "quick" for m in matches)
    assert any(m[0] == "quiet" for m in matches)

    assert mod.validate_email("me@example.com") is True
    assert mod.validate_email("not-an-email") is False

    assert mod.validate_url("http://example.com") is True
    assert mod.validate_url("example.com") is False

    choices = mod.generate_choices_from_range(1, 3)
    assert choices == ["1", "2", "3"]

    choices2 = mod.generate_choices_from_range(
        0.0, 0.5, step=0.25, format_fn=lambda x: f"{x:.2f}"
    )
    assert "0.25" in choices2
