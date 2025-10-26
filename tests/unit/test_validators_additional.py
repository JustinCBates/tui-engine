from datetime import date
from types import SimpleNamespace

import pytest
from questionary import ValidationError

# Use existing project imports
from questionary_extended.validators import (
    ChoiceValidator,
    CompositeValidator,
    DateValidator,
    LengthValidator,
    NumberValidator,
    RangeValidator,
    RegexValidator,
)


def _doc(text):
    return SimpleNamespace(text=text)


def test_number_validator_empty_and_invalid():
    v = NumberValidator()
    with pytest.raises(ValidationError):
        v.validate(_doc(""))

    v2 = NumberValidator(allow_float=False)
    with pytest.raises(ValidationError):
        v2.validate(_doc("1.23"))


def test_number_validator_min_max_and_step():
    v = NumberValidator(min_value=10, max_value=20)
    with pytest.raises(ValidationError):
        v.validate(_doc("9"))
    with pytest.raises(ValidationError):
        v.validate(_doc("21"))

    v2 = NumberValidator(step=5, min_value=0)
    # 7 is not a multiple of 5 -> fail
    with pytest.raises(ValidationError):
        v2.validate(_doc("7"))
    # 10 is fine
    v2.validate(_doc("10"))


def test_date_validator_format_and_bounds():
    v = DateValidator(format_str="%Y-%m-%d")
    with pytest.raises(ValidationError):
        v.validate(_doc("not-a-date"))

    v2 = DateValidator(min_date=date(2020, 1, 1), max_date=date(2020, 12, 31))
    with pytest.raises(ValidationError):
        v2.validate(_doc("2019-12-31"))
    with pytest.raises(ValidationError):
        v2.validate(_doc("2021-01-01"))
    # valid
    v2.validate(_doc("2020-06-15"))


def test_range_validator_inclusive_and_exclusive():
    inc = RangeValidator(1, 5, inclusive=True)
    inc.validate(_doc("3"))
    with pytest.raises(ValidationError):
        inc.validate(_doc("0"))

    exc = RangeValidator(1, 5, inclusive=False)
    with pytest.raises(ValidationError):
        exc.validate(_doc("1"))
    with pytest.raises(ValidationError):
        exc.validate(_doc("5"))
    exc.validate(_doc("3"))


def test_regex_and_length_and_choice_validators():
    r = RegexValidator(r"^abc$")
    with pytest.raises(ValidationError):
        r.validate(_doc("abcd"))
    r.validate(_doc("abc"))

    l = LengthValidator(min_length=2, max_length=4)
    with pytest.raises(ValidationError):
        l.validate(_doc("a"))
    with pytest.raises(ValidationError):
        l.validate(_doc("toolong"))
    l.validate(_doc("ok"))

    c = ChoiceValidator(["A", "B", "C"], case_sensitive=False)
    c.validate(_doc("a"))
    with pytest.raises(ValidationError):
        c.validate(_doc("z"))


def test_composite_validator_re_raises_first_error():
    v1 = LengthValidator(min_length=3)
    v2 = RegexValidator(r"^a.*$")
    comp = CompositeValidator([v1, v2])

    # First validator should trigger on short text
    with pytest.raises(ValidationError):
        comp.validate(_doc("ab"))
