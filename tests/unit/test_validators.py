from datetime import date
import pytest
from questionary import ValidationError

from pathlib import Path
from tests.helpers.test_helpers import load_module_from_path

# Load validators module via centralized helper to ensure __package__ is set
vmod = load_module_from_path(
    "questionary_extended.validators", Path("src/questionary_extended/validators.py").resolve()
)


class Dummy:
    def __init__(self, text):
        self.text = text


def test__doc_text_with_object_and_string():
    assert vmod._doc_text(Dummy(" hi ")) == "hi"
    assert vmod._doc_text("abc") == "abc"


def test_number_validator_basic_and_bounds_and_step():
    nv = vmod.NumberValidator()
    with pytest.raises(ValidationError):
        nv.validate(Dummy(""))

    nv2 = vmod.NumberValidator(min_value=1, max_value=10, allow_float=False)
    with pytest.raises(ValidationError):
        nv2.validate(Dummy("0"))
    with pytest.raises(ValidationError):
        nv2.validate(Dummy("11"))

    nv3 = vmod.NumberValidator(step=2, min_value=0)
    # non multiple of step
    with pytest.raises(ValidationError):
        nv3.validate(Dummy("3"))
    # valid multiple
    nv3.validate(Dummy("4"))


def test_date_validator_format_and_range():
    dv = vmod.DateValidator(format_str="%Y-%m-%d")
    with pytest.raises(ValidationError):
        dv.validate(Dummy(""))
    with pytest.raises(ValidationError):
        dv.validate(Dummy("not-a-date"))

    dv2 = vmod.DateValidator(min_date=date(2020, 1, 1), max_date=date(2020, 12, 31))
    with pytest.raises(ValidationError):
        dv2.validate(Dummy("2019-12-31"))
    with pytest.raises(ValidationError):
        dv2.validate(Dummy("2021-01-01"))


def test_email_and_url_validators():
    ev = vmod.EmailValidator()
    with pytest.raises(ValidationError):
        ev.validate(Dummy(""))
    with pytest.raises(ValidationError):
        ev.validate(Dummy("not-an-email"))
    ev.validate(Dummy("a@b.com"))

    uv = vmod.URLValidator()
    with pytest.raises(ValidationError):
        uv.validate(Dummy(""))
    with pytest.raises(ValidationError):
        uv.validate(Dummy("ftp://example.com"))
    uv.validate(Dummy("http://example.com"))
    # require https
    uv2 = vmod.URLValidator(require_https=True)
    with pytest.raises(ValidationError):
        uv2.validate(Dummy("http://example.com"))
    uv2.validate(Dummy("https://example.com"))


def test_range_validator_inclusive_and_exclusive_and_format():
    rv = vmod.RangeValidator(1, 3, inclusive=True)
    with pytest.raises(ValidationError):
        rv.validate(Dummy("0"))
    rv.validate(Dummy("2"))

    rv2 = vmod.RangeValidator(1, 3, inclusive=False)
    with pytest.raises(ValidationError):
        rv2.validate(Dummy("1"))

    # format error
    with pytest.raises(ValidationError):
        rv.validate(Dummy("not-int"))


def test_regex_and_length_and_choice_validators():
    rg = vmod.RegexValidator(r"^a.*z$", message="bad")
    with pytest.raises(ValidationError):
        rg.validate(Dummy(""))
    with pytest.raises(ValidationError):
        rg.validate(Dummy("abc"))
    rg.validate(Dummy("abcz"))

    lv = vmod.LengthValidator(min_length=2, max_length=4)
    with pytest.raises(ValidationError):
        lv.validate(Dummy("a"))
    with pytest.raises(ValidationError):
        lv.validate(Dummy("toolonghere"))
    lv.validate(Dummy("ok"))

    cv = vmod.ChoiceValidator(["one", "Two"], case_sensitive=False)
    with pytest.raises(ValidationError):
        cv.validate(Dummy(""))
    with pytest.raises(ValidationError):
        cv.validate(Dummy("three"))
    cv.validate(Dummy("two"))


def test_composite_validator_re_raises_first_error():
    nv_fail = vmod.NumberValidator()
    # empty doc will cause ValidationError
    comp = vmod.CompositeValidator([nv_fail])
    with pytest.raises(ValidationError):
        comp.validate(Dummy(""))
import pytest
from datetime import date

import questionary

from src.questionary_extended import validators as v


def test_numbervalidator_basic_cases():
    NV = v.NumberValidator

    with pytest.raises(questionary.ValidationError):
        NV().validate("")

    with pytest.raises(questionary.ValidationError):
        NV().validate("abc")

    # decimals not allowed when allow_float=False
    with pytest.raises(questionary.ValidationError):
        NV(allow_float=False).validate("1.2")

    # min and max checks
    with pytest.raises(questionary.ValidationError):
        NV(min_value=5).validate("3")

    with pytest.raises(questionary.ValidationError):
        NV(max_value=10).validate("11")

    # step check
    with pytest.raises(questionary.ValidationError):
        NV(min_value=0, step=3).validate("5")

    # valid integer
    NV(min_value=0, max_value=10, allow_float=False).validate("5")


def test_datevalidator_and_bounds():
    DV = v.DateValidator

    with pytest.raises(questionary.ValidationError):
        DV().validate("")

    with pytest.raises(questionary.ValidationError):
        DV().validate("not-a-date")

    # valid date
    DV().validate("2020-01-02")

    # min_date and max_date enforcement
    dv = DV(min_date=date(2020, 1, 2))
    with pytest.raises(questionary.ValidationError):
        dv.validate("2020-01-01")

    dv2 = DV(max_date=date(2020, 1, 1))
    with pytest.raises(questionary.ValidationError):
        dv2.validate("2020-01-02")


def test_rangevalidator_inclusive_and_exclusive():
    RV = v.RangeValidator

    with pytest.raises(questionary.ValidationError):
        RV(1, 3).validate("")

    # valid inside inclusive
    RV(1, 3).validate("2")

    with pytest.raises(questionary.ValidationError):
        RV(1, 3).validate("4")

    # exclusive bounds
    with pytest.raises(questionary.ValidationError):
        RV(1, 3, inclusive=False).validate("1")

    with pytest.raises(questionary.ValidationError):
        RV(1, 3, inclusive=False).validate("3")

    # invalid format
    with pytest.raises(questionary.ValidationError):
        RV(1, 3).validate("notnum")


def test_choice_validator_and_case_insensitive():
    CV = v.ChoiceValidator
    with pytest.raises(questionary.ValidationError):
        CV(["a", "b"]).validate("")

    # not in choices
    with pytest.raises(questionary.ValidationError):
        CV(["a", "b"]).validate("c")

    # case-insensitive
    CV(["A", "B"], case_sensitive=False).validate("a")


def test_composite_validator_raises_first_error():
    class Bad:
        def validate(self, doc):
            raise questionary.ValidationError(message="bad", cursor_position=0)

    comp = v.CompositeValidator([Bad()])
    with pytest.raises(questionary.ValidationError):
        comp.validate("x")
from datetime import date

import pytest

from questionary import ValidationError

from questionary_extended.validators import (
    NumberValidator,
    DateValidator,
    EmailValidator,
    URLValidator,
    RangeValidator,
    RegexValidator,
    LengthValidator,
    ChoiceValidator,
    CompositeValidator,
)


class Doc:
    def __init__(self, text: str):
        self.text = text


def test_number_validator_integer_and_float_behaviour():
    v = NumberValidator(allow_float=False)
    # valid integer
    v.validate(Doc("10"))

    # decimals not allowed when allow_float=False
    with pytest.raises(ValidationError):
        v.validate(Doc("3.14"))

    # min/max enforcement
    v2 = NumberValidator(min_value=0, max_value=5, allow_float=True)
    v2.validate(Doc("4.5"))
    with pytest.raises(ValidationError):
        v2.validate(Doc("-1"))
    with pytest.raises(ValidationError):
        v2.validate(Doc("6"))

    # step enforcement (min_value defaults to None -> uses 0 in calculation)
    v3 = NumberValidator(step=2)
    with pytest.raises(ValidationError):
        v3.validate(Doc("3"))


def test_date_validator_parsing_and_bounds():
    dv = DateValidator(format_str="%Y-%m-%d")
    dv.validate(Doc("2020-01-02"))

    # invalid format
    with pytest.raises(ValidationError):
        dv.validate(Doc("01/02/2020"))

    # min/max
    dv2 = DateValidator(min_date=date(2020, 1, 1), max_date=date(2020, 12, 31))
    dv2.validate(Doc("2020-06-01"))
    with pytest.raises(ValidationError):
        dv2.validate(Doc("2019-12-31"))


def test_email_validator():
    ev = EmailValidator()
    ev.validate(Doc("user@example.com"))
    with pytest.raises(ValidationError):
        ev.validate(Doc("not-an-email"))


def test_url_validator_and_https_requirement():
    uv = URLValidator()
    uv.validate(Doc("http://example.com"))
    uv.validate(Doc("https://example.com/path"))

    uv2 = URLValidator(require_https=True)
    uv2.validate(Doc("https://secure.example.com"))
    with pytest.raises(ValidationError):
        uv2.validate(Doc("http://example.com"))

    with pytest.raises(ValidationError):
        uv.validate(Doc("not-a-url"))


def test_range_validator_inclusive_and_exclusive():
    rv = RangeValidator(1, 5, inclusive=True)
    rv.validate(Doc("1"))
    rv.validate(Doc("5"))
    with pytest.raises(ValidationError):
        rv.validate(Doc("0"))

    rv2 = RangeValidator(1, 5, inclusive=False)
    with pytest.raises(ValidationError):
        rv2.validate(Doc("1"))
    with pytest.raises(ValidationError):
        rv2.validate(Doc("5"))


def test_regex_length_choice_validators_and_composite():
    regex = RegexValidator(r"^ab+$", message="nope")
    regex.validate(Doc("abb"))
    with pytest.raises(ValidationError):
        regex.validate(Doc("ac"))

    length = LengthValidator(min_length=2, max_length=4)
    length.validate(Doc("ab"))
    with pytest.raises(ValidationError):
        length.validate(Doc("a"))

    choice = ChoiceValidator(["One", "Two"], case_sensitive=False)
    # case-insensitive check
    choice.validate(Doc("one"))
    with pytest.raises(ValidationError):
        choice.validate(Doc("Three"))

    # composite: using an input that fails one of the validators should raise
    comp = CompositeValidator([regex, length])
    with pytest.raises(ValidationError):
        comp.validate(Doc("a"))
