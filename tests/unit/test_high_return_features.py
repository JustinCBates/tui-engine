import pytest
from questionary_extended import prompts, utils
from questionary_extended.integration.questionary_bridge import QuestionaryBridge
from questionary_extended.core.state import PageState


def test_grouped_select_flattening():
    groups = {"Fruits": ["apple", "banana"], "Veg": ["carrot"]}
    q = prompts.grouped_select("pick", groups)
    # LazyQuestion should be returned; repr contains factory name
    r = repr(q)
    assert "LazyQuestion" in r or "questionary.select" in r


def test_rating_allow_zero_and_choices():
    q = prompts.rating("rate", max_rating=3, allow_zero=True)
    r = repr(q)
    assert "select" in r or "LazyQuestion" in r


def test_number_edge_cases():
    # integer only
    q = prompts.integer("num", min_value=1, max_value=3)
    assert q is not None
    # float input allowed
    q2 = prompts.number("numf", allow_float=True, min_value=0.0, max_value=10.0)
    assert q2 is not None


def test_utils_parse_color_and_format_number():
    c = utils.parse_color("00ff00")
    assert hasattr(c, "rgb") and c.rgb[0] == 0
    s = utils.format_number(1234.56, thousands_sep=True, decimal_places=2)
    assert "," in s or s.replace(" ", "").isdigit()


def test_questionary_bridge_ask_component(monkeypatch):
    state = PageState()
    bridge = QuestionaryBridge(state)

    # Create a fake component with create_questionary_component method
    class FakeComponent:
        def __init__(self, name):
            self.name = name

        def create_questionary_component(self):
            class F:
                def ask(self, *a, **k):
                    return "answer"

            return F()

    comp = FakeComponent("field1")
    # should not raise and should set state
    bridge.ask_component(comp)
    assert state.get("field1") == "answer"
