import importlib.util
from pathlib import Path
import builtins
from tests.helpers.test_helpers import load_module_from_path
from tests.conftest_questionary import setup_questionary_mocks

# Install the canonical questionary mock before importing/loading modules
# so that modules loaded via load_module_from_path pick up the fake module
# and don't attempt to create real prompt_toolkit sessions during import.
_module_q = setup_questionary_mocks(None)

pc = load_module_from_path(
    "questionary_extended.prompts_core",
    Path("src/questionary_extended/prompts_core.py").resolve(),
)

# Ensure the loaded module references the same mock for deterministic factories
try:
    pc.questionary = _module_q
except Exception:
    pass


def test_lazyquestion_build_and_repr(monkeypatch):
    class FakeQ:
        def __init__(self, *a, **k):
            self.args = a
            self.kw = k

        def ask(self):
            return "ok"

    lq = pc.LazyQuestion(FakeQ, "msg", default=1)
    assert "LazyQuestion" in repr(lq)
    built = lq.build()
    assert hasattr(built, "ask")
    assert lq.ask() == "ok"


def test_progress_tracker_steps(capsys):
    pt = pc.ProgressTracker("T", total=3)
    with pt as p:
        p.step("one")
        p.step("two")
        p.update(3, "three")
        p.complete("done")

    out = capsys.readouterr().out
    assert "Starting" in out or "Total" in out
    assert "done" in out


def test_wrappers_return_lazyquestion():
    # confirm/select/checkbox should return LazyQuestion
    cq = pc.confirm_enhanced("ok")
    assert isinstance(cq, pc.LazyQuestion)
    sq = pc.select_enhanced("choose", [1, 2])
    assert isinstance(sq, pc.LazyQuestion)
    cb = pc.checkbox_enhanced("cb", [1, 2])
    assert isinstance(cb, pc.LazyQuestion)
import pytest
from unittest.mock import Mock

import questionary

from src.questionary_extended import prompts_core as pc


def test_lazyquestion_build_call_ask_repr():
    mock_q = Mock()
    mock_q.ask.return_value = "the-answer"

    def factory(*args, **kwargs):
        return mock_q

    lq = pc.LazyQuestion(factory, "msg", foo=1)
    assert lq.build() is mock_q
    assert lq() is mock_q
    assert lq.ask() == "the-answer"
    r = repr(lq)
    assert "LazyQuestion" in r
    assert "factory=" in r


def test_enhanced_text_includes_validator_in_kwargs():
    def dummy_validator(x):
        return True

    lq = pc.enhanced_text("hello", default="d", multiline=True, validator=dummy_validator, extra=1)
    # validator should be placed into kwargs under 'validate'
    assert isinstance(lq, pc.LazyQuestion)
    assert "validate" in lq._kwargs
    assert lq._kwargs["validate"] is dummy_validator
    assert lq._kwargs["default"] == "d"


def test_number_uses_numbervalidator_and_default_str(monkeypatch):
    # replace the heavy NumberValidator with a lightweight dummy
    class DummyNumberValidator:
        def __init__(self, min_value=None, max_value=None, allow_float=True):
            self.min_value = min_value
            self.max_value = max_value
            self.allow_float = allow_float

        def __call__(self, val):
            return True

    monkeypatch.setattr("src.questionary_extended.validators.NumberValidator", DummyNumberValidator)

    lq = pc.number("num", default=7, min_value=0, max_value=10, allow_float=False)
    assert isinstance(lq, pc.LazyQuestion)
    # default converted to string
    assert lq._kwargs["default"] == "7"
    assert isinstance(lq._kwargs["validate"], DummyNumberValidator)


def test_form_calls_questionary_prompt(monkeypatch):
    monkeypatch.setattr(questionary, "prompt", lambda questions, **kw: {"ok": True})
    res = pc.form([{"type": "input", "name": "a", "message": "m"}], foo=1)
    assert res == {"ok": True}


def test_progress_tracker_steps_and_complete(capsys):
    with pc.ProgressTracker("MyJob", total=3) as p:
        assert isinstance(p, pc.ProgressTracker)
        p.step("first")
        p.update(2, "second")
        p.complete("done")

    out = capsys.readouterr().out
    assert "Starting: MyJob" in out
    assert "Total steps" in out
    assert "first" in out
    assert "second" in out
    assert "🎉 done" in out


def test_progress_tracker_exit_on_exception(capsys):
    with pytest.raises(ValueError):
        with pc.ProgressTracker("X", total=2):
            raise ValueError("boom")

    out = capsys.readouterr().out
    assert "Starting: X" in out
    assert "❌ Failed: boom" in out


def test_confirm_select_checkbox_return_lazyquestion():
    c = pc.confirm_enhanced("Are you sure?", default=False)
    assert isinstance(c, pc.LazyQuestion)
    assert c._factory is questionary.confirm

    s = pc.select_enhanced("Pick", choices=[1, 2])
    assert isinstance(s, pc.LazyQuestion)
    assert s._factory is questionary.select

    cb = pc.checkbox_enhanced("Pick many", choices=["a"]) 
    assert isinstance(cb, pc.LazyQuestion)
    assert cb._factory is questionary.checkbox


def test_progress_tracker_update_idempotent(capsys):
    p = pc.ProgressTracker("Idem", total=None)
    # step once, then update with same description to exercise idempotent branch
    p.step("one")
    # Now update with same description; since it's already in completed_steps,
    # the conditional branch should not append it again.
    p.update(1, "one")
    assert p.completed_steps.count("one") == 1
    out = capsys.readouterr().out
    assert "one" in out


def test_integer_delegates_to_number(monkeypatch):
    class DummyNumberValidator:
        def __init__(self, min_value=None, max_value=None, allow_float=True):
            self.min_value = min_value
            self.max_value = max_value
            self.allow_float = allow_float

        def __call__(self, v):
            return True

    monkeypatch.setattr("src.questionary_extended.validators.NumberValidator", DummyNumberValidator)
    lq = pc.integer("intmsg", min_value=0, max_value=5)
    assert isinstance(lq, pc.LazyQuestion)
    # integer should set allow_float=False on the validator
    assert hasattr(lq._kwargs, "__contains__") or True
    # validator present and configured
    assert hasattr(lq._kwargs["validate"], "allow_float")
    assert lq._kwargs["validate"].allow_float is False


def test_lazyquestion_repr_without_name():
    class CallableObj:
        def __call__(self, *a, **k):
            return Mock()

    c = CallableObj()
    lq = pc.LazyQuestion(c, "m")
    r = repr(lq)
    # should include the repr of the callable object when __name__ isn't present
    assert "factory=" in r
    assert "CallableObj" in r or "object" in r


def test_enhanced_text_without_validator():
    lq = pc.enhanced_text("hi", default="x", multiline=False)
    # no validator passed, so 'validate' should not be in kwargs
    assert "validate" not in lq._kwargs


def test_number_removes_user_validate_and_uses_internal_validator(monkeypatch):
    class DummyNumberValidator:
        def __init__(self, min_value=None, max_value=None, allow_float=True):
            self.min_value = min_value
            self.max_value = max_value
            self.allow_float = allow_float

        def __call__(self, v):
            return True

    monkeypatch.setattr("src.questionary_extended.validators.NumberValidator", DummyNumberValidator)
    lq = pc.number("n", default=None, min_value=0, max_value=10, extra=5, validate="ignore_me")
    # The user-supplied 'validate' must be removed from clean_kwargs and replaced by internal validator
    assert isinstance(lq._kwargs.get("validate"), DummyNumberValidator)
    assert lq._kwargs.get("extra") == 5


def test_progress_tracker_step_with_total(capsys):
    p = pc.ProgressTracker("T", total=4)
    p.step("a")
    p.step("b")
    assert p.completed_steps == ["a", "b"]
    out = capsys.readouterr().out
    assert "[" in out and "]" in out
from types import SimpleNamespace

from questionary_extended.prompts_core import LazyQuestion, ProgressTracker, enhanced_text


def test_lazy_question_repr_and_build_and_ask(monkeypatch):
    # Fake question object with ask()
    class FakeQ:
        def __init__(self, msg, default=None, **kw):
            self.msg = msg
            self.default = default

        def ask(self):
            return f"asked:{self.msg}:{self.default}"

    # monkeypatch questionary.text factory via a simple factory
    fake_factory = lambda message, default=None, **kw: FakeQ(message, default=default)

    lq = LazyQuestion(fake_factory, "hello", default="x")
    r = repr(lq)
    assert "LazyQuestion" in r

    built = lq.build()
    assert isinstance(built, FakeQ)

    # ask should call FakeQ.ask and return its result
    assert lq.ask() == "asked:hello:x"


def test_progress_tracker_context_and_steps(capsys):
    pt = ProgressTracker("MyTask", total=3)
    with pt as p:
        p.step("one")
        p.step("two")
        p.update(3, "three")
        p.complete("Done!")

    out = capsys.readouterr().out
    assert "Starting: MyTask" in out
    assert "Total steps: 3" in out
    assert "(100.0%)" in out or "(66.7%)" in out
    assert "🎉 Done!" in out


def test_enhanced_text_returns_lazy_question():
    lq = enhanced_text("hi", default="x")
    # Should be callable and have a repr that mentions LazyQuestion
    assert callable(lq)
    assert "LazyQuestion" in repr(lq)
from questionary_extended.prompts_core import LazyQuestion, ProgressTracker
import questionary


def test_lazy_question_repr_and_build(monkeypatch):
    # Monkeypatch questionary.text to avoid prompt_toolkit PromptSession creation
    def fake_text(message, *args, **kwargs):
        class F:
            def ask(self, *a, **k):
                return "ok"

        return F()

    monkeypatch.setattr(questionary, "text", fake_text)

    lq = LazyQuestion(questionary.text, "Enter:")
    r = repr(lq)
    assert "LazyQuestion" in r
    # build returns the fake object that has ask method
    obj = lq.build()
    assert hasattr(obj, "ask")


def test_progress_tracker_basic(capsys):
    with ProgressTracker("T", total=2) as p:
        p.step("a")
        p.step("b")
    captured = capsys.readouterr()
    assert "Starting" in captured.out or "Completed" in captured.out
