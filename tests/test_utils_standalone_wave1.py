import importlib.util
import os


def _load_utils_module():
    path = os.path.join(
        os.path.dirname(__file__), "..", "src", "questionary_extended", "utils.py"
    )
    path = os.path.abspath(path)
    spec = importlib.util.spec_from_file_location(
        "questionary_extended._utils_file", path
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_parse_color_variants_and_invalid():
    mod = _load_utils_module()
    # hex with #
    c = mod.parse_color("#ff0000")
    assert c.hex.lower() == "#ff0000"

    # named color
    c = mod.parse_color("red")
    assert c.hex.lower() == "#ff0000"

    # rgb format
    c = mod.parse_color("rgb(0, 128, 255)")
    assert c.hex.lower() == "#0080ff"

    # hex without #
    c = mod.parse_color("00ff00")
    assert c.hex.lower() == "#00ff00"

    # invalid -> raises ValueError
    try:
        mod.parse_color("notacolor")
    except ValueError:
        pass
    else:
        raise AssertionError("parse_color should raise ValueError for invalid input")


def test_format_and_parse_number_and_percentage():
    mod = _load_utils_module()
    assert mod.format_number(1234.5) == "1234.5"
    assert mod.format_number(1234.5, decimal_places=1, thousands_sep=True) == "1,234.5"
    assert mod.format_number(0.125, percentage=True) == "0.1%"
    assert mod.format_number(99, currency="$") == "$99"

    assert mod.parse_number("1,234.56") == 1234.56
    assert mod.parse_number("1234", allow_float=False) == 1234


def test_render_markdown_and_truncate_wrap_center():
    mod = _load_utils_module()
    s = "**bold** and *italic* and `code`"
    rendered = mod.render_markdown(s)
    assert "\033[1m" in rendered and "\033[3m" in rendered and "\033[2m" in rendered

    # truncate
    assert mod.truncate_text("hello", 10) == "hello"
    assert mod.truncate_text("hello world", 5).endswith("...")

    # wrap: long word
    wrapped = mod.wrap_text("supercalifragilisticexpialidocious", 5)
    assert any(len(line) <= 5 for line in wrapped)

    # center
    assert mod.center_text("x", 3) == " x "


def test_progress_table_tree_and_sanitize():
    mod = _load_utils_module()
    bar = mod.create_progress_bar(5, 10, width=10)
    assert "[" in bar and "]" in bar

    row = mod.create_table_row(["a long text"], [8])
    assert "|" in row

    line = mod.create_tree_line(
        "node", 1, is_last=True, has_children=True, expanded=False
    )
    assert "└──" in line or "├──" in line

    assert mod.sanitize_input("abc\x00def") == "abcdef"


def test_fuzzy_and_validation_and_generate_choices():
    mod = _load_utils_module()
    matches = mod.fuzzy_match("app", ["apple", "application", "banana"])
    assert any(m[0].startswith("app") for m in matches)

    assert mod.validate_email("me@example.com") is True
    assert mod.validate_email("not an email") is False

    assert mod.validate_url("http://example.com") is True
    assert mod.validate_url("notaurl") is False

    choices = mod.generate_choices_from_range(1, 3)
    assert choices == ["1", "2", "3"]
