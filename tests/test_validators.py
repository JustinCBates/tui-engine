"""Tests for validators module."""

import pytest
from datetime import date, datetime
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
    CompositeValidator
)


class MockDocument:
    """Mock document for testing validators."""
    
    def __init__(self, text: str):
        self.text = text


class TestNumberValidator:
    """Test NumberValidator class."""
    
    def test_valid_integer(self):
        validator = NumberValidator(allow_float=False)
        doc = MockDocument("42")
        # Should not raise an exception
        validator.validate(doc)
    
    def test_valid_float(self):
        validator = NumberValidator(allow_float=True)
        doc = MockDocument("42.5")
        # Should not raise an exception
        validator.validate(doc)
    
    def test_invalid_float_when_not_allowed(self):
        validator = NumberValidator(allow_float=False)
        doc = MockDocument("42.5")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)
    
    def test_min_value_validation(self):
        validator = NumberValidator(min_value=10)
        doc = MockDocument("5")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)
    
    def test_max_value_validation(self):
        validator = NumberValidator(max_value=100)
        doc = MockDocument("150")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)
    
    def test_empty_input(self):
        validator = NumberValidator()
        doc = MockDocument("")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)
    
    def test_invalid_number(self):
        validator = NumberValidator()
        doc = MockDocument("not_a_number")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)


class TestDateValidator:
    """Test DateValidator class."""
    
    def test_valid_date(self):
        validator = DateValidator(format_str="%Y-%m-%d")
        doc = MockDocument("2023-12-25")
        # Should not raise an exception
        validator.validate(doc)
    
    def test_invalid_date_format(self):
        validator = DateValidator(format_str="%Y-%m-%d")
        doc = MockDocument("25-12-2023")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)
    
    def test_date_before_min(self):
        min_date = date(2023, 1, 1)
        validator = DateValidator(min_date=min_date, format_str="%Y-%m-%d")
        doc = MockDocument("2022-12-31")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)
    
    def test_date_after_max(self):
        max_date = date(2023, 12, 31)
        validator = DateValidator(max_date=max_date, format_str="%Y-%m-%d")
        doc = MockDocument("2024-01-01")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)


class TestEmailValidator:
    """Test EmailValidator class."""
    
    def test_valid_email(self):
        validator = EmailValidator()
        doc = MockDocument("user@example.com")
        # Should not raise an exception
        validator.validate(doc)
    
    def test_invalid_email(self):
        validator = EmailValidator()
        doc = MockDocument("invalid-email")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)
    
    def test_empty_email(self):
        validator = EmailValidator()
        doc = MockDocument("")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)


class TestURLValidator:
    """Test URLValidator class."""
    
    def test_valid_http_url(self):
        validator = URLValidator()
        doc = MockDocument("http://example.com")
        # Should not raise an exception
        validator.validate(doc)
    
    def test_valid_https_url(self):
        validator = URLValidator()
        doc = MockDocument("https://example.com")
        # Should not raise an exception
        validator.validate(doc)
    
    def test_require_https(self):
        validator = URLValidator(require_https=True)
        doc = MockDocument("http://example.com")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)
    
    def test_invalid_url(self):
        validator = URLValidator()
        doc = MockDocument("not-a-url")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)


class TestRangeValidator:
    """Test RangeValidator class."""
    
    def test_valid_range(self):
        validator = RangeValidator(min_val=1, max_val=10)
        doc = MockDocument("5")
        # Should not raise an exception
        validator.validate(doc)
    
    def test_below_range(self):
        validator = RangeValidator(min_val=1, max_val=10)
        doc = MockDocument("0")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)
    
    def test_above_range(self):
        validator = RangeValidator(min_val=1, max_val=10)
        doc = MockDocument("11")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)


class TestRegexValidator:
    """Test RegexValidator class."""
    
    def test_valid_pattern(self):
        validator = RegexValidator(r'^[A-Z][a-z]+$', "Must start with uppercase")
        doc = MockDocument("Hello")
        # Should not raise an exception
        validator.validate(doc)
    
    def test_invalid_pattern(self):
        validator = RegexValidator(r'^[A-Z][a-z]+$', "Must start with uppercase")
        doc = MockDocument("hello")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)


class TestLengthValidator:
    """Test LengthValidator class."""
    
    def test_valid_length(self):
        validator = LengthValidator(min_length=3, max_length=10)
        doc = MockDocument("hello")
        # Should not raise an exception
        validator.validate(doc)
    
    def test_too_short(self):
        validator = LengthValidator(min_length=5)
        doc = MockDocument("hi")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)
    
    def test_too_long(self):
        validator = LengthValidator(max_length=5)
        doc = MockDocument("this is too long")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)


class TestChoiceValidator:
    """Test ChoiceValidator class."""
    
    def test_valid_choice(self):
        validator = ChoiceValidator(["apple", "banana", "cherry"])
        doc = MockDocument("apple")
        # Should not raise an exception
        validator.validate(doc)
    
    def test_invalid_choice(self):
        validator = ChoiceValidator(["apple", "banana", "cherry"])
        doc = MockDocument("grape")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)
    
    def test_case_insensitive(self):
        validator = ChoiceValidator(["Apple", "Banana", "Cherry"], case_sensitive=False)
        doc = MockDocument("apple")
        # Should not raise an exception
        validator.validate(doc)


class TestCompositeValidator:
    """Test CompositeValidator class."""
    
    def test_all_validators_pass(self):
        validators = [
            LengthValidator(min_length=3),
            RegexValidator(r'^[a-zA-Z]+$', "Only letters allowed")
        ]
        validator = CompositeValidator(validators)
        doc = MockDocument("hello")
        # Should not raise an exception
        validator.validate(doc)
    
    def test_first_validator_fails(self):
        validators = [
            LengthValidator(min_length=10),  # This will fail
            RegexValidator(r'^[a-zA-Z]+$', "Only letters allowed")
        ]
        validator = CompositeValidator(validators)
        doc = MockDocument("hi")
        
        with pytest.raises(ValidationError):
            validator.validate(doc)