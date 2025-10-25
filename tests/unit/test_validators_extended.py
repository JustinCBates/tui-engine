from pathlib import Path
from datetime import date
from tests.helpers.test_helpers import load_module_from_path

validators = load_module_from_path(
    "questionary_extended.validators", Path("src/questionary_extended/validators.py").resolve()
)


class Doc:
    def __init__(self, text):
        self.text = text


def test_number_validator_errors_and_success():
    NV = validators.NumberValidator
    from questionary import ValidationError

    v = NV()
    try:
        v.validate(Doc(""))
        assert False
    except ValidationError:
        pass

    # invalid format
    try:
        v.validate(Doc("notanumber"))
        assert False
    except ValidationError:
        pass

    # integer-only
    vi = NV(allow_float=False)
    try:
        vi.validate(Doc("1.5"))
        assert False
    except ValidationError:
        pass

    # min/max
    vmin = NV(min_value=10)
    try:
        vmin.validate(Doc("5"))
        assert False
    except ValidationError:
        pass

    vmax = NV(max_value=2)
    try:
        vmax.validate(Doc("3"))
        assert False
    except ValidationError:
        pass

    # step
    vs = NV(min_value=0, step=2)
    try:
        vs.validate(Doc("3"))
        assert False
    except ValidationError:
        pass

    # success
    vgood = NV(min_value=0, max_value=10)
    vgood.validate(Doc("5"))


def test_date_validator_branches():
    DV = validators.DateValidator
    from questionary import ValidationError

    v = DV(format_str="%Y-%m-%d")
    try:
        v.validate(Doc(""))
        assert False
    except ValidationError:
        pass

    try:
        v.validate(Doc("2020/01/01"))
        assert False
    except ValidationError:
        pass

    vmin = DV(min_date=date(2020, 1, 2))
    try:
        vmin.validate(Doc("2020-01-01"))
        assert False
    except ValidationError:
        pass

    vmax = DV(max_date=date(2020, 1, 1))
    try:
        vmax.validate(Doc("2020-01-02"))
        assert False
    except ValidationError:
        pass

    # success
    vs = DV()
    vs.validate(Doc("2020-01-01"))


def test_email_and_url_validator():
    EV = validators.EmailValidator
    UV = validators.URLValidator
    from questionary import ValidationError

    e = EV()
    try:
        e.validate(Doc(""))
        assert False
    except ValidationError:
        pass

    try:
        e.validate(Doc("bad@"))
        assert False
    except ValidationError:
        pass

    e.validate(Doc("user@example.com"))

    u = UV()
    try:
        u.validate(Doc(""))
        assert False
    except ValidationError:
        pass

    try:
        u.validate(Doc("http:/bad"))
        assert False
    except ValidationError:
        pass

    u.validate(Doc("http://example.com"))

    # require https
    uh = UV(require_https=True)
    try:
        uh.validate(Doc("http://example.com"))
        assert False
    except ValidationError:
        pass


def test_range_regex_length_choice_and_composite():
    from questionary import ValidationError

    RV = validators.RangeValidator(1, 3, inclusive=True)
    try:
        RV.validate(Doc(""))
        assert False
    except ValidationError:
        pass

    try:
        RV.validate(Doc("a"))
        assert False
    except ValidationError:
        pass

    try:
        RV.validate(Doc("0"))
        assert False
    except ValidationError:
        pass

    RV2 = validators.RangeValidator(1, 3, inclusive=False)
    try:
        RV2.validate(Doc("1"))
        assert False
    except ValidationError:
        pass

    # RegexValidator
    RX = validators.RegexValidator(r"^a+$", message="nope")
    try:
        RX.validate(Doc(""))
        assert False
    except ValidationError:
        pass
    try:
        RX.validate(Doc("b"))
        assert False
    except ValidationError as e:
        assert "nope" in str(e)

    RX.validate(Doc("aaa"))

    # LengthValidator
    LV = validators.LengthValidator(min_length=2, max_length=3)
    try:
        LV.validate(Doc("a"))
        assert False
    except ValidationError:
        pass
    try:
        LV.validate(Doc("abcd"))
        assert False
    except ValidationError:
        pass

    # ChoiceValidator
    CV = validators.ChoiceValidator(["A", "B"], case_sensitive=False)
    try:
        CV.validate(Doc(""))
        assert False
    except ValidationError:
        pass
    try:
        CV.validate(Doc("c"))
        assert False
    except ValidationError:
        pass
    CV.validate(Doc("a"))

    # CompositeValidator re-raises first ValidationError
    comp = validators.CompositeValidator([validators.RegexValidator(r"^x+$"), validators.LengthValidator(min_length=5)])
    try:
        comp.validate(Doc("y"))
        assert False
    except ValidationError:
        pass
import importlib.util
import pathlib
import sys
import types
import pytest


def _load_validators_with_stub():
    # Ensure any existing imports won't interfere
    for name in ["questionary", "questionary_extended.validators", "questionary_extended"]:
        if name in sys.modules:
            sys.modules.pop(name)

    # Insert a minimal questionary stub with ValidationError and Validator
    q = types.ModuleType("questionary")
    class ValidationError(Exception):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)

    class Validator:
        def validate(self, document):
            raise NotImplementedError()

    q.ValidationError = ValidationError
    q.Validator = Validator
    sys.modules["questionary"] = q

    root = pathlib.Path(__file__).resolve().parents[2] / "src" / "questionary_extended"
    path = root / "validators.py"
    from tests.helpers.test_helpers import load_module_from_path

    module = load_module_from_path("questionary_extended.validators", path)
    return module


class Doc:
    def __init__(self, text):
        self.text = text


def test_number_validator_basic():
    vmod = _load_validators_with_stub()
    NumberValidator = vmod.NumberValidator

    nv = NumberValidator()
    nv.validate(Doc("123"))
    nv2 = NumberValidator(allow_float=False)
    with pytest.raises(Exception):
        nv2.validate(Doc("1.23"))

    nv3 = NumberValidator(min_value=10)
    with pytest.raises(vmod.ValidationError):
        nv3.validate(Doc("5"))

    nv4 = NumberValidator(max_value=5)
    with pytest.raises(vmod.ValidationError):
        nv4.validate(Doc("10"))

    nv5 = NumberValidator(step=2, min_value=0)
    with pytest.raises(vmod.ValidationError):
        nv5.validate(Doc("3"))


def test_date_validator():
    vmod = _load_validators_with_stub()
    DateValidator = vmod.DateValidator

    dv = DateValidator(format_str="%Y-%m-%d")
    dv.validate(Doc("2020-01-02"))

    with pytest.raises(Exception):
        dv.validate(Doc("bad-date"))

    dv2 = DateValidator(min_date=vmod.datetime.strptime("2020-01-01", "%Y-%m-%d").date())
    with pytest.raises(vmod.ValidationError):
        dv2.validate(Doc("2019-12-31"))


def test_email_and_url_validators():
    vmod = _load_validators_with_stub()
    ev = vmod.EmailValidator()
    ev.validate(Doc("test@example.com"))
    with pytest.raises(Exception):
        ev.validate(Doc("no-at-symbol"))

    uv = vmod.URLValidator()
    uv.validate(Doc("http://example.com"))
    with pytest.raises(Exception):
        uv.validate(Doc("notaurl"))

    uv2 = vmod.URLValidator(require_https=True)
    with pytest.raises(Exception):
        uv2.validate(Doc("http://example.com"))


def test_range_regex_length_choice():
    vmod = _load_validators_with_stub()
    RangeValidator = vmod.RangeValidator
    rv = RangeValidator(1, 3, inclusive=True)
    rv.validate(Doc("2"))
    with pytest.raises(Exception):
        rv.validate(Doc("0"))

    rv2 = RangeValidator(1, 3, inclusive=False)
    with pytest.raises(Exception):
        rv2.validate(Doc("1"))

    RegexValidator = vmod.RegexValidator
    r = RegexValidator(r"^a.*z$", message="no match")
    r.validate(Doc("abcz"))
    with pytest.raises(Exception):
        r.validate(Doc("nomatch"))

    lv = vmod.LengthValidator(min_length=2, max_length=4)
    lv.validate(Doc("abc"))
    with pytest.raises(Exception):
        lv.validate(Doc("a"))
    with pytest.raises(Exception):
        lv.validate(Doc("abcdef"))

    cv = vmod.ChoiceValidator(["A", "B"], case_sensitive=False)
    cv.validate(Doc("a"))
    with pytest.raises(Exception):
        cv.validate(Doc("c"))


def test_composite_validator():
    vmod = _load_validators_with_stub()
    # Small failing validator
    class AlwaysFail(vmod.Validator):
        def validate(self, document):
            raise vmod.ValidationError("fail")

    cv = vmod.CompositeValidator([AlwaysFail()])
    with pytest.raises(Exception):
        cv.validate(Doc("x"))
from pathlib import Path
from datetime import date
from tests.helpers.test_helpers import load_module_from_path

validators = load_module_from_path(
    "questionary_extended.validators", Path("src/questionary_extended/validators.py").resolve()
)


class Doc:
    def __init__(self, text):
        self.text = text


def test_number_validator_errors_and_success():
    NV = validators.NumberValidator
    from questionary import ValidationError

    v = NV()
    try:
        v.validate(Doc(""))
        assert False
    except ValidationError:
        pass

    # invalid format
    try:
        v.validate(Doc("notanumber"))
        assert False
    except ValidationError:
        pass

    # integer-only
    vi = NV(allow_float=False)
    try:
        vi.validate(Doc("1.5"))
        assert False
    except ValidationError:
        pass

    # min/max
    vmin = NV(min_value=10)
    try:
        vmin.validate(Doc("5"))
        assert False
    except ValidationError:
        pass

    vmax = NV(max_value=2)
    try:
        vmax.validate(Doc("3"))
        assert False
    except ValidationError:
        pass

    # step
    vs = NV(min_value=0, step=2)
    try:
        vs.validate(Doc("3"))
        assert False
    except ValidationError:
        pass

    # success
    vgood = NV(min_value=0, max_value=10)
    vgood.validate(Doc("5"))


def test_date_validator_branches():
    DV = validators.DateValidator
    from questionary import ValidationError

    v = DV(format_str="%Y-%m-%d")
    try:
        v.validate(Doc(""))
        assert False
    except ValidationError:
        pass

    try:
        v.validate(Doc("2020/01/01"))
        assert False
    except ValidationError:
        pass

    vmin = DV(min_date=date(2020, 1, 2))
    try:
        vmin.validate(Doc("2020-01-01"))
        assert False
    except ValidationError:
        pass

    vmax = DV(max_date=date(2020, 1, 1))
    try:
        vmax.validate(Doc("2020-01-02"))
        assert False
    except ValidationError:
        pass

    # success
    vs = DV()
    vs.validate(Doc("2020-01-01"))


def test_email_and_url_validator():
    EV = validators.EmailValidator
    UV = validators.URLValidator
    from questionary import ValidationError

    e = EV()
    try:
        e.validate(Doc(""))
        assert False
    except ValidationError:
        pass

    try:
        e.validate(Doc("bad@"))
        assert False
    except ValidationError:
        pass

    e.validate(Doc("user@example.com"))

    u = UV()
    try:
        u.validate(Doc(""))
        assert False
    except ValidationError:
        pass

    try:
        u.validate(Doc("http:/bad"))
        assert False
    except ValidationError:
        pass

    u.validate(Doc("http://example.com"))

    # require https
    uh = UV(require_https=True)
    try:
        uh.validate(Doc("http://example.com"))
        assert False
    except ValidationError:
        pass


def test_range_regex_length_choice_and_composite():
    from questionary import ValidationError

    RV = validators.RangeValidator(1, 3, inclusive=True)
    try:
        RV.validate(Doc(""))
        assert False
    except ValidationError:
        pass

    try:
        RV.validate(Doc("a"))
        assert False
    except ValidationError:
        pass

    try:
        RV.validate(Doc("0"))
        assert False
    except ValidationError:
        pass

    RV2 = validators.RangeValidator(1, 3, inclusive=False)
    try:
        RV2.validate(Doc("1"))
        assert False
    except ValidationError:
        pass

    # RegexValidator
    RX = validators.RegexValidator(r"^a+$", message="nope")
    try:
        RX.validate(Doc(""))
        assert False
    except ValidationError:
        pass
    try:
        RX.validate(Doc("b"))
        assert False
    except ValidationError as e:
        assert "nope" in str(e)

    RX.validate(Doc("aaa"))

    # LengthValidator
    LV = validators.LengthValidator(min_length=2, max_length=3)
    try:
        LV.validate(Doc("a"))
        assert False
    except ValidationError:
        pass
    try:
        LV.validate(Doc("abcd"))
        assert False
    except ValidationError:
        pass

    # ChoiceValidator
    CV = validators.ChoiceValidator(["A", "B"], case_sensitive=False)
    try:
        CV.validate(Doc(""))
        assert False
    except ValidationError:
        pass
    try:
        CV.validate(Doc("c"))
        assert False
    except ValidationError:
        pass
    CV.validate(Doc("a"))

    # CompositeValidator re-raises first ValidationError
    comp = validators.CompositeValidator([validators.RegexValidator(r"^x+$"), validators.LengthValidator(min_length=5)])
    try:
        comp.validate(Doc("y"))
        assert False
    except ValidationError:
        pass
