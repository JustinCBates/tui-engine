import importlib.util
import sys
import types
from pathlib import Path


def _load_validators_with_stub():
    fake_q = types.SimpleNamespace()

    class ValidationError(Exception):
        def __init__(self, message: str = "", cursor_position: int = 0):
            super().__init__(message)
            self.message = message
            self.cursor_position = cursor_position

    class Validator:
        def validate(self, document):
            raise NotImplementedError()

    fake_q.ValidationError = ValidationError
    fake_q.Validator = Validator

    sys.modules["questionary"] = fake_q

    module_path = Path(__file__).parents[2] / "src" / "questionary_extended" / "validators.py"
    from tests.helpers.test_helpers import load_module_from_path

    mod = load_module_from_path("questionary_extended.validators", module_path)
    return mod


def test__doc_text_doc_attr_and_exception_path():
    mod = _load_validators_with_stub()

    class D:
        text = "  hello  "

    assert mod._doc_text(D()) == "hello"

    class Bad:
        @property
        def text(self):
            raise RuntimeError("nope")

        def __str__(self):
            return " fallback "

    assert mod._doc_text(Bad()) == "fallback"


def test_number_validator_empty_and_invalid_and_bounds_and_step():
    mod = _load_validators_with_stub()
    ValidationError = mod.ValidationError

    nv = mod.NumberValidator()
    with pytest_raises(ValidationError):
        nv.validate(type("X", (), {"text": ""})())

    nv2 = mod.NumberValidator(allow_float=False)
    with pytest_raises(ValidationError):
        nv2.validate(type("X", (), {"text": "3.5"})())

    nv3 = mod.NumberValidator(min_value=5)
    with pytest_raises(ValidationError):
        nv3.validate(type("X", (), {"text": "3"})())

    nv4 = mod.NumberValidator(max_value=2)
    with pytest_raises(ValidationError):
        nv4.validate(type("X", (), {"text": "3"})())

    nv5 = mod.NumberValidator(step=2, min_value=0)
    with pytest_raises(ValidationError):
        nv5.validate(type("X", (), {"text": "3"})())

    # success case
    nv_ok = mod.NumberValidator(min_value=0, max_value=10, allow_float=False)
    nv_ok.validate(type("X", (), {"text": "4"})())


def test_date_validator_format_and_bounds():
    mod = _load_validators_with_stub()
    ValidationError = mod.ValidationError

    dv = mod.DateValidator(format_str="%Y-%m-%d")
    with pytest_raises(ValidationError):
        dv.validate(type("X", (), {"text": ""})())

    with pytest_raises(ValidationError):
        dv.validate(type("X", (), {"text": "not-a-date"})())

    from datetime import date

    dv2 = mod.DateValidator(format_str="%Y-%m-%d", min_date=date(2020, 1, 1))
    with pytest_raises(ValidationError):
        dv2.validate(type("X", (), {"text": "2019-12-31"})())

    dv3 = mod.DateValidator(format_str="%Y-%m-%d", max_date=date(2020, 1, 1))
    with pytest_raises(ValidationError):
        dv3.validate(type("X", (), {"text": "2020-02-01"})())

    # success
    dv_ok = mod.DateValidator()
    dv_ok.validate(type("X", (), {"text": "2020-01-01"})())


def test_email_validator_and_url_validator():
    mod = _load_validators_with_stub()
    ValidationError = mod.ValidationError

    ev = mod.EmailValidator()
    with pytest_raises(ValidationError):
        ev.validate(type("X", (), {"text": ""})())
    with pytest_raises(ValidationError):
        ev.validate(type("X", (), {"text": "not@ok@"})())
    ev.validate(type("X", (), {"text": "me@example.com"})())

    uv = mod.URLValidator(require_https=True)
    with pytest_raises(ValidationError):
        uv.validate(type("X", (), {"text": "http://example.com"})())

    uv2 = mod.URLValidator()
    with pytest_raises(ValidationError):
        uv2.validate(type("X", (), {"text": "no-scheme"})())
    uv2.validate(type("X", (), {"text": "http://localhost"})())


def test_range_regex_length_choice_and_composite():
    mod = _load_validators_with_stub()
    ValidationError = mod.ValidationError

    rv = mod.RangeValidator(1, 3, inclusive=True)
    with pytest_raises(ValidationError):
        rv.validate(type("X", (), {"text": ""})())
    with pytest_raises(ValidationError):
        rv.validate(type("X", (), {"text": "0"})())
    rv.validate(type("X", (), {"text": "2"})())

    rg = mod.RegexValidator(r"^a+$")
    with pytest_raises(ValidationError):
        rg.validate(type("X", (), {"text": ""})())
    with pytest_raises(ValidationError):
        rg.validate(type("X", (), {"text": "b"})())
    rg.validate(type("X", (), {"text": "aaa"})())

    lv = mod.LengthValidator(min_length=2, max_length=3)
    with pytest_raises(ValidationError):
        lv.validate(type("X", (), {"text": "a"})())
    with pytest_raises(ValidationError):
        lv.validate(type("X", (), {"text": "abcd"})())
    lv.validate(type("X", (), {"text": "ab"})())

    cv = mod.ChoiceValidator(["A", "B"], case_sensitive=False)
    with pytest_raises(ValidationError):
        cv.validate(type("X", (), {"text": ""})())
    with pytest_raises(ValidationError):
        cv.validate(type("X", (), {"text": "c"})())
    cv.validate(type("X", (), {"text": "a"})())

    # composite: first validator fails
    class FailVal:
        def validate(self, document):
            raise ValidationError("bad")

    class PassVal:
        def validate(self, document):
            return None

    comp = mod.CompositeValidator([FailVal(), PassVal()])
    with pytest_raises(ValidationError):
        comp.validate(type("X", (), {"text": "ok"})())


# small pytest compatibility helper
import contextlib


@contextlib.contextmanager
def pytest_raises(exc):
    try:
        yield
    except Exception as e:
        if not isinstance(e, exc):
            raise
        return
    raise AssertionError(f"Expected exception {exc}")
