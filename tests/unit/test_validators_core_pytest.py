import pytest
from datetime import date

from questionary import ValidationError

from questionary_extended import validators


class _D:
    def __init__(self, t):
        self.text = t


class _BadText:
    @property
    def text(self):
        raise RuntimeError("boom")


def test__doc_text_handles_text_and_exceptions():
    assert validators._doc_text(" abc ") == "abc"
    assert validators._doc_text(_D(" x ")) == "x"
    # when accessing .text raises, fall back to str(document)
    bad = _BadText()
    assert validators._doc_text(bad) == str(bad).strip()


def test_number_validator_basic_and_errors():
    v = validators.NumberValidator()
    with pytest.raises(ValidationError):
        v.validate("")

    with pytest.raises(ValidationError):
        v.validate("notanumber")

    # integer only mode rejects decimals
    vi = validators.NumberValidator(allow_float=False)
    with pytest.raises(ValidationError):
        vi.validate("1.2")

    # min/max
    vmin = validators.NumberValidator(min_value=5)
    with pytest.raises(ValidationError):
        vmin.validate("4")

    vmax = validators.NumberValidator(max_value=10)
    with pytest.raises(ValidationError):
        vmax.validate("11")

    # step
    vst = validators.NumberValidator(step=2)
    with pytest.raises(ValidationError):
        vst.validate("3")

    # valid
    v.validate("3.5")
    vi.validate("3")


def test_date_validator_formats_and_bounds():
    dv = validators.DateValidator(format_str="%Y-%m-%d")
    with pytest.raises(ValidationError):
        dv.validate("")

    with pytest.raises(ValidationError):
        dv.validate("2020/01/01")

    dvmin = validators.DateValidator(min_date=date(2020, 1, 2))
    with pytest.raises(ValidationError):
        dvmin.validate("2020-01-01")

    dvmax = validators.DateValidator(max_date=date(2020, 1, 1))
    with pytest.raises(ValidationError):
        dvmax.validate("2020-01-02")

    # valid
    dv.validate("2020-01-01")


def test_email_validator():
    ev = validators.EmailValidator()
    with pytest.raises(ValidationError):
        ev.validate("")

    with pytest.raises(ValidationError):
        ev.validate("not-an-email")

    ev.validate("a.b@example.com")


def test_url_validator():
    uv = validators.URLValidator()
    with pytest.raises(ValidationError):
        uv.validate("")

    with pytest.raises(ValidationError):
        uv.validate("not-a-url")

    uv.validate("http://example.com/")

    uv2 = validators.URLValidator(require_https=True)
    with pytest.raises(ValidationError):
        uv2.validate("http://example.com/")

    uv2.validate("https://example.com/")


def test_range_validator_and_inclusive_exclusive():
    rv = validators.RangeValidator(1, 3, inclusive=True)
    with pytest.raises(ValidationError):
        rv.validate("")

    with pytest.raises(ValidationError):
        rv.validate("xyz")

    with pytest.raises(ValidationError):
        rv.validate("0")

    with pytest.raises(ValidationError):
        rv.validate("4")

    # exclusive
    rv2 = validators.RangeValidator(1, 3, inclusive=False)
    with pytest.raises(ValidationError):
        rv2.validate("1")
    with pytest.raises(ValidationError):
        rv2.validate("3")

    rv.validate("2")


def test_range_validator_float_and_string_min_max():
    # float min/max path
    rvf = validators.RangeValidator(0.5, 2.5, inclusive=True)
    with pytest.raises(ValidationError):
        rvf.validate("0.1")
    rvf.validate("1.5")

    # string min/max should exercise the else path (value = text)
    rvs = validators.RangeValidator("a", "z", inclusive=True)
    # 'm' is between 'a' and 'z'
    rvs.validate("m")


def test_regex_length_choice_validators_and_composite():
    r = validators.RegexValidator(r"^a.*z$", message="nope")
    with pytest.raises(ValidationError):
        r.validate("")
    with pytest.raises(ValidationError):
        r.validate("abc")
    r.validate("abz")

    lv = validators.LengthValidator(min_length=2, max_length=4)
    with pytest.raises(ValidationError):
        lv.validate("a")
    with pytest.raises(ValidationError):
        lv.validate("toolong")
    lv.validate("ok")

    cv = validators.ChoiceValidator(["A", "B"], case_sensitive=False)
    with pytest.raises(ValidationError):
        cv.validate("")
    with pytest.raises(ValidationError):
        cv.validate("c")
    cv.validate("a")

    # composite should re-raise the first validation error
    comp = validators.CompositeValidator([validators.LengthValidator(min_length=5), validators.RegexValidator(r"^x")])
    with pytest.raises(ValidationError):
        comp.validate("no")
