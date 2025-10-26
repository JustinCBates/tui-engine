import sys
import types
from pathlib import Path

from tests.conftest_questionary import setup_questionary_mocks
from tests.helpers.test_helpers import load_module_from_path


def _load_prompts_with_stubs():
    # Install canonical questionary mock so imports like `from questionary import X`
    # resolve to a stable, test-friendly module. This avoids creating real
    # prompt_toolkit sessions during import on CI/Windows.
    _module_q = setup_questionary_mocks(None)

    # Create a fake package module for 'questionary_extended' so relative
    # imports inside prompts.py don't trigger the real package __init__.
    pkg = types.ModuleType("questionary_extended")
    # mark as a package so relative imports work
    pkg.__path__ = [str(Path(__file__).parents[2] / "src" / "questionary_extended")]
    sys.modules["questionary_extended"] = pkg

    # provide a fake components module with minimal Column/ProgressStep
    fake_components = types.SimpleNamespace()

    class Column:
        def __init__(self, name, width=10):
            self.name = name
            self.width = width

    class ProgressStep:
        def __init__(self, title):
            self.title = title

        def to_question_dict(self):
            return {"name": self.title}

    fake_components.Column = Column
    fake_components.ProgressStep = ProgressStep
    sys.modules["questionary_extended.components"] = fake_components

    # provide a fake styles module with Theme
    fake_styles = types.SimpleNamespace()

    class Theme:
        pass

    fake_styles.Theme = Theme
    sys.modules["questionary_extended.styles"] = fake_styles

    # Fake prompts_core with LazyQuestion that records inputs
    fake_pc = types.SimpleNamespace()

    def LazyQuestion(func, message, **kwargs):
        return {
            "func": getattr(func, "__name__", str(func)),
            "message": message,
            **kwargs,
        }

    fake_pc.LazyQuestion = LazyQuestion
    fake_pc.ProgressTracker = lambda *a, **k: None
    sys.modules["questionary_extended.prompts_core"] = fake_pc

    # Fake validators with simple classes
    fake_val = types.SimpleNamespace()

    class NumberValidator:
        def __init__(self, **kwargs):
            self._kwargs = kwargs

        def __repr__(self):
            return f"NumberValidator({self._kwargs})"

    class DateValidator:
        def __init__(self, **kwargs):
            self._kwargs = kwargs

        def __repr__(self):
            return f"DateValidator({self._kwargs})"

    fake_val.NumberValidator = NumberValidator
    fake_val.DateValidator = DateValidator
    sys.modules["questionary_extended.validators"] = fake_val

    # load the prompts module by path using centralized helper
    module_path = (
        Path(__file__).parents[2] / "src" / "questionary_extended" / "prompts.py"
    )
    mod = load_module_from_path("questionary_extended.prompts", str(module_path))
    return mod


def test_tree_select_flattening():
    mod = _load_prompts_with_stubs()
    # nested structure with dict, list and scalar
    choices = {"src": {"pkg": ["a", "b"], "file": "x"}, "top": "y"}

    res = mod.tree_select("Pick", choices)

    # LazyQuestion returns dict with 'choices'
    assert isinstance(res, dict)
    flat = res.get("choices")
    assert isinstance(flat, list)
    # expected flatten order per implementation
    assert "src/" in flat
    assert "src/pkg/a" in flat
    assert "src/pkg/b" in flat
    assert "src/file" in flat
    assert "top" in flat


def test_grouped_select_preserves_separators_and_dict_choices():
    mod = _load_prompts_with_stubs()
    groups = {"G1": ["a", {"name": "b", "value": 2}], "G2": ["c"]}

    res = mod.grouped_select("Group", groups)
    assert isinstance(res, dict)
    choices = res.get("choices")
    # first element should be a Separator instance
    assert len(choices) >= 3
    # separators are created using questionary.Separator wrapper
    sep = choices[0]
    from questionary import Separator as SepCls

    assert isinstance(sep, SepCls)
    # ensure dict choice preserved
    assert any(isinstance(c, dict) and c.get("name") == "b" for c in choices)


def test_rating_generates_display_and_values():
    mod = _load_prompts_with_stubs()
    res = mod.rating("Rate", max_rating=3, icon="*", allow_zero=False)
    choices = res.get("choices")
    assert isinstance(choices, list)
    # values should be 1..3 when allow_zero is False
    values = [c["value"] for c in choices]
    assert values == [1, 2, 3]
    # display should contain icons
    assert any("*" in c["name"] for c in choices)


def test_number_returns_lazy_with_validator_object():
    mod = _load_prompts_with_stubs()
    res = mod.number("Num", default=5, min_value=0, max_value=10, allow_float=False)
    # LazyQuestion returns a prompt that exposes 'validate' via .get()
    assert res.get("validate") is not None
    validator = res.get("validate")
    # our fake NumberValidator should be instance-like (repr check)
    assert "NumberValidator" in repr(validator)


# cleanup
import atexit


def _cleanup():
    for k in [
        "questionary",
        "questionary_extended.prompts_core",
        "questionary_extended.validators",
    ]:
        sys.modules.pop(k, None)


atexit.register(_cleanup)


def test_date_time_and_datetime_formatting_and_validation():
    import datetime as dt

    mod = _load_prompts_with_stubs()
    d = dt.date(2021, 12, 31)
    res = mod.date("When", default=d)
    # questionary.text stub returns a prompt object with 'default' passed through
    assert res.get("default") == "2021-12-31"
    assert res.get("validate") is not None

    t = dt.time(13, 5, 9)
    res2 = mod.time("At", default=t)
    assert res2.get("default") == "13:05:09"

    dtv = dt.datetime(2020, 1, 2, 3, 4, 5)
    res3 = mod.datetime_input("DT", default=dtv)
    assert res3.get("default") == "2020-01-02 03:04:05"


def test_tag_select_fuzzy_and_table_and_form_wizard():
    mod = _load_prompts_with_stubs()

    tag = mod.tag_select("tags", ["a", "b"], allow_custom=True)
    assert tag.get("choices") == ["a", "b"]

    fuzzy = mod.fuzzy_select("f", ["x", "y"])
    assert fuzzy.get("choices") == ["x", "y"]

    tbl = mod.table("Table", [mod.Column("c1")])
    # table returns a LazyQuestion wrapping text with an implementation note
    assert "Table input - implementation pending" in tbl.get("message")

    # form/wizard use questionary.prompt and should return our stubbed dict
    questions = [{"type": "text", "name": "q", "message": "Q?"}]
    f = mod.form(questions)
    assert f.get("prompted") is questions

    step = mod.ProgressStep("step1")
    w = mod.wizard([step])
    assert w.get("prompted") == [step.to_question_dict()]
