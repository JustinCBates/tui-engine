from pathlib import Path
from datetime import date
from tests.helpers.test_helpers import load_module_from_path

u = load_module_from_path(
    "questionary_extended.utils", Path("src/questionary_extended/utils/__init__.py").resolve()
)


def test_format_and_parse_date_init():
    d = u.format_date(date(2021, 2, 3))
    assert d == "2021-02-03"
    assert u.parse_date("2021-02-03") == date(2021, 2, 3)


def test_format_number_init_and_parse():
    s = u.format_number(1234.5, decimal_places=1, thousands_sep=True, currency="$")
    assert s.startswith("$")
    assert u.parse_number("1,234.50") == 1234.5
    assert u.parse_number(42, allow_float=False) == 42


def test_parse_color_and_render_markdown_init():
    ci = u.parse_color("#00ff00")
    assert ci.hex == "#00ff00"
    ci2 = u.parse_color("green")
    assert ci2.rgb[1] == 255
    out = u.render_markdown("**b** *i*")
    assert "\033[1m" in out and "\033[3m" in out


def test_truncate_wrap_center_progress_init():
    assert u.truncate_text("hello", 10) == "hello"
    assert isinstance(u.wrap_text("a b c d", 2), list)
    assert u.center_text("x", 3).strip() == "x"
    assert "[" in u.create_progress_bar(1, 2, width=5)


def test_fuzzy_and_validate_init():
    matches = u.fuzzy_match("a", ["a", "ab"], threshold=0.5)
    assert any(m[0] == "a" for m in matches)
    assert u.validate_email("a@b.com") is True
    assert u.validate_email("bad") is False
    assert u.validate_url("https://x.test") is True
    assert u.validate_url("notaurl") is False
