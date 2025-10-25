from questionary import Separator
import questionary

from questionary_extended import prompts, utils
from questionary_extended.components import ColorInfo


def _fake_select_factory(message, choices=None, **kw):
    # return a simple namespace mimicking questionary prompt holding choices
    return type("Q", (), {"choices": choices, "kwargs": kw})()


def test_grouped_select_builds_choices_list(monkeypatch):
    monkeypatch.setattr(questionary, "select", _fake_select_factory)
    groups = {"Fruits": ["apple", "banana"], "Veg": ["carrot"]}
    lq = prompts.grouped_select("pick", groups)
    # inspect choices passed into LazyQuestion (no need to build a real prompt)
    choices = lq._kwargs.get("choices")
    # Accept either internal storage: ensure separators and items present
    assert any(isinstance(c, Separator) for c in choices)
    assert any((isinstance(c, str) and "apple" in c) or (not isinstance(c, str) and "apple" in str(c)) for c in choices)


def test_rating_choices_allow_zero_and_values(monkeypatch):
    monkeypatch.setattr(questionary, "select", _fake_select_factory)
    lq1 = prompts.rating("rate", max_rating=3, allow_zero=False)
    # inspect stored choices on the LazyQuestion
    choices1 = lq1._kwargs.get("choices")
    # Values should be present and start at 1
    assert any((isinstance(c, dict) and c.get("value") == 1) for c in choices1)

    lq2 = prompts.rating("rate", max_rating=3, allow_zero=True)
    choices2 = lq2._kwargs.get("choices")
    assert any((isinstance(c, dict) and c.get("value") == 0) for c in choices2)


def test_tree_select_flattens_nested_dict(monkeypatch):
    monkeypatch.setattr(questionary, "select", _fake_select_factory)
    choices = {"root": {"child": ["a", "b"], "leaf": "x"}}
    lq = prompts.tree_select("t", choices)
    flat = lq._kwargs.get("choices")
    # Flattening should contain paths
    assert any("root/child/a" in str(c) or "root/child/a" == c for c in flat)


def test_format_and_parse_number_and_percentage():
    assert utils.format_number(1234.56, decimal_places=2) == "1234.56"
    assert utils.format_number(1234.56, thousands_sep=True) == "1,234.56"
    assert utils.format_number(0.1567, decimal_places=1, percentage=True).endswith("%")

    assert utils.parse_number("1,234.56") == 1234.56
    assert utils.parse_number("42", allow_float=False) == 42


def test_parse_color_named_and_rgb():
    ci = utils.parse_color("red")
    # utils.parse_color may return a local Color dataclass or a shared ColorInfo
    assert hasattr(ci, "hex") and hasattr(ci, "rgb")
    assert ci.hex.lower() == "#ff0000"

    ci2 = utils.parse_color("rgb(0, 128, 255)")
    assert hasattr(ci2, "hex") and hasattr(ci2, "rgb")
    assert ci2.rgb[1] == 128


def test_create_progress_bar_and_truncate_and_wrap_and_fuzzy():
    bar = utils.create_progress_bar(5, 10, width=10)
    assert "[" in bar and "]" in bar

    assert utils.truncate_text("hello world", 5) == "he..."

    wrapped = utils.wrap_text("one two three", 5)
    assert isinstance(wrapped, list)

    matches = utils.fuzzy_match("one", ["one", "onetime", "two"])
    assert any(m[0] == "one" for m in matches)
