import pytest
from questionary import ValidationError

from questionary_extended.validators import (
    EmailValidator,
    NumberValidator,
    URLValidator,
)


def test_email_validator():
    v = EmailValidator()
    # valid
    v.validate("user@example.com")

    # invalid
    with pytest.raises(ValidationError):
        v.validate("not-an-email")


def test_url_validator():
    v = URLValidator()
    v.validate("http://example.com")

    v_https = URLValidator(require_https=True)
    with pytest.raises(ValidationError):
        v_https.validate("http://example.com")


def test_number_validator_basic():
    v = NumberValidator(min_value=0, max_value=10, allow_float=False)
    v.validate("5")

    with pytest.raises(ValidationError):
        v.validate("-1")
