from questionary import ValidationError

from questionary_extended.validators import RangeValidator


def test_range_validator_inclusive_accepts_bounds():
    v = RangeValidator(1, 3, inclusive=True)
    # on lower bound
    v.validate("1")
    # on upper bound
    v.validate("3")


def test_range_validator_inclusive_rejects_outside():
    v = RangeValidator(1, 3, inclusive=True)
    try:
        v.validate("0")
        assert False, "Expected ValidationError for value below min"
    except ValidationError as e:
        assert "between" in e.message

    try:
        v.validate("4")
        assert False, "Expected ValidationError for value above max"
    except ValidationError as e:
        assert "between" in e.message


def test_range_validator_exclusive_rejects_bounds_and_accepts_middle():
    v = RangeValidator(1, 3, inclusive=False)
    # bounds should be rejected
    for val in ("1", "3"):
        try:
            v.validate(val)
            assert False, f"Expected ValidationError for exclusive bound {val}"
        except ValidationError as e:
            assert "exclusive" in e.message

    # middle value ok
    v.validate("2")


def test_range_validator_invalid_format_raises():
    v = RangeValidator(1, 3)
    try:
        v.validate("not-a-number")
        assert False, "Expected ValidationError for invalid format"
    except ValidationError as e:
        assert "Invalid value format" in e.message


def test_range_validator_float_conversion():
    v = RangeValidator(1.0, 3.0, inclusive=True)
    # float input should be parsed and accepted
    v.validate("2.5")


def test_range_validator_exclusive_string_bounds():
    # Use non-numeric min/max to exercise the 'else' branch and exclusive message
    v = RangeValidator("a", "z", inclusive=False)
    try:
        v.validate("a")
        assert False, "Expected ValidationError for exclusive bound 'a'"
    except ValidationError as e:
        # ensure the exclusive message is produced
        assert "exclusive" in str(e) or "exclusive" in getattr(e, "message", "")
