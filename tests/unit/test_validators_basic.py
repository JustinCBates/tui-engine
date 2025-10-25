import pytest

from questionary_extended import validators
from questionary import ValidationError


class Doc:
    def __init__(self, text: str):
        self.text = text


def test_number_validator_basic():
    v = validators.NumberValidator(min_value=0, max_value=10, allow_float=False)

    # valid integer
    doc = Doc("5")
    v.validate(doc)

    # empty input -> ValidationError
    with pytest.raises(ValidationError):
        v.validate(Doc(""))

    # non-numeric
    with pytest.raises(ValidationError):
        v.validate(Doc("abc"))

    # decimal when integers only
    with pytest.raises(ValidationError):
        v.validate(Doc("3.14"))


def test_email_validator_basic():
    v = validators.EmailValidator()

    # valid
    v.validate(Doc("user@example.com"))

    # invalid
    with pytest.raises(ValidationError):
        v.validate(Doc("not-an-email"))


def test_url_validator_require_https():
    v = validators.URLValidator(require_https=True)

    # https ok
    v.validate(Doc("https://example.com"))

    # http fails when require_https is True
    with pytest.raises(ValidationError):
        v.validate(Doc("http://example.com"))
