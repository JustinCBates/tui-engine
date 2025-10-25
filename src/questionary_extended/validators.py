"""
Enhanced validators for different input types.
"""

import re
from datetime import date, datetime
from typing import Any, List, Optional, Union

from questionary import ValidationError, Validator


def _doc_text(document: object) -> str:
    """Return the textual content for a document-like or string input."""
    try:
        return getattr(document, "text", str(document)).strip()
    except Exception as _exc:
        # Defensive fallback if the document-like object doesn't expose
        # a textual attribute. Capture the exception in `_exc` for
        # potential debugging without altering behavior.
        return str(document).strip()


class NumberValidator(Validator):
    """Validator for numeric input."""

    def __init__(
        self,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        allow_float: bool = True,
        step: Optional[Union[int, float]] = None,
    ):
        self.min_value = min_value
        self.max_value = max_value
        self.allow_float = allow_float
        self.step = step

    def validate(self, document: object) -> None:
        text = _doc_text(document)

        if not text:
            raise ValidationError(
                message="Please enter a number", cursor_position=len(text)
            )

        try:
            if self.allow_float:
                value = float(text)
            else:
                if "." in text:
                    raise ValueError("Decimal numbers not allowed")
                value = int(text)
        except ValueError as e:
            number_type = "number" if self.allow_float else "integer"
            raise ValidationError(
                message=f"Please enter a valid {number_type}", cursor_position=len(text)
            ) from e

        if self.min_value is not None and value < self.min_value:
            raise ValidationError(
                message=f"Value must be at least {self.min_value}",
                cursor_position=len(text),
            )

        if self.max_value is not None and value > self.max_value:
            raise ValidationError(
                message=f"Value must be at most {self.max_value}",
                cursor_position=len(text),
            )

        if self.step is not None:
            remainder = (value - (self.min_value or 0)) % self.step
            if remainder != 0:
                raise ValidationError(
                    message=f"Value must be a multiple of {self.step}",
                    cursor_position=len(text),
                )


class DateValidator(Validator):
    """Validator for date input."""

    def __init__(
        self,
        format_str: str = "%Y-%m-%d",
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
    ):
        self.format_str = format_str
        self.min_date = min_date
        self.max_date = max_date

    def validate(self, document: object) -> None:
        text = _doc_text(document)

        if not text:
            raise ValidationError(
                message=f"Please enter a date in format {self.format_str}",
                cursor_position=len(text),
            )

        try:
            parsed_date = datetime.strptime(text, self.format_str).date()
        except ValueError as e:
            raise ValidationError(
                message=f"Invalid date format. Expected: {self.format_str}",
                cursor_position=len(text),
            ) from e

        if self.min_date and parsed_date < self.min_date:
            raise ValidationError(
                message=(
                    "Date must be after " + self.min_date.strftime(self.format_str)
                ),
                cursor_position=len(text),
            )

        if self.max_date and parsed_date > self.max_date:
            raise ValidationError(
                message=(
                    "Date must be before " + self.max_date.strftime(self.format_str)
                ),
                cursor_position=len(text),
            )


class EmailValidator(Validator):
    """Validator for email addresses."""

    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}"
        r"[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    )

    def validate(self, document: object) -> None:
        text = _doc_text(document)

        if not text:
            raise ValidationError(
                message="Please enter an email address", cursor_position=len(text)
            )

        if not self.EMAIL_REGEX.match(text):
            raise ValidationError(
                message="Please enter a valid email address", cursor_position=len(text)
            )


class URLValidator(Validator):
    """Validator for URLs."""

    URL_REGEX = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    def __init__(self, require_https: bool = False):
        self.require_https = require_https

    def validate(self, document: Any) -> None:
        text = _doc_text(document)

        if not text:
            raise ValidationError(
                message="Please enter a URL", cursor_position=len(text)
            )

        if self.require_https and not text.startswith("https://"):
            raise ValidationError(
                message="URL must use HTTPS", cursor_position=len(text)
            )

        if not self.URL_REGEX.match(text):
            raise ValidationError(
                message="Please enter a valid URL (include http:// or https://)",
                cursor_position=len(text),
            )


class RangeValidator(Validator):
    """Validator for values within a specific range."""

    def __init__(self, min_val: Any, max_val: Any, inclusive: bool = True):
        self.min_val = min_val
        self.max_val = max_val
        self.inclusive = inclusive

    def validate(self, document: object) -> None:
        text = _doc_text(document)

        if not text:
            raise ValidationError(
                message="Please enter a value", cursor_position=len(text)
            )

        try:
            # Try to convert to the same type as min/max values
            if isinstance(self.min_val, int):
                value: Any = int(text)
            elif isinstance(self.min_val, float):
                value = float(text)
            else:
                value = text
        except ValueError as e:
            raise ValidationError(
                message="Invalid value format", cursor_position=len(text)
            ) from e

        if self.inclusive:
            if value < self.min_val or value > self.max_val:
                raise ValidationError(
                    message=(
                        "Value must be between " + f"{self.min_val} and {self.max_val}"
                    ),
                    cursor_position=len(text),
                )
        else:
            if value <= self.min_val or value >= self.max_val:
                raise ValidationError(
                    message=(
                        "Value must be between "
                        + f"{self.min_val} and {self.max_val} (exclusive)"
                    ),
                    cursor_position=len(text),
                )


class RegexValidator(Validator):
    """Validator using regular expressions."""

    def __init__(
        self,
        pattern: str,
        message: str = "Input does not match required format",
        flags: int = 0,
    ):
        self.pattern = re.compile(pattern, flags)
        self.message = message

    def validate(self, document: object) -> None:
        text = _doc_text(document)

        if not text:
            raise ValidationError(
                message="Please enter a value", cursor_position=len(text)
            )

        if not self.pattern.match(text):
            raise ValidationError(message=self.message, cursor_position=len(text))


class LengthValidator(Validator):
    """Validator for string length."""

    def __init__(
        self, min_length: Optional[int] = None, max_length: Optional[int] = None
    ):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, document: object) -> None:
        text = _doc_text(document)
        length = len(text)

        if self.min_length is not None and length < self.min_length:
            raise ValidationError(
                message=f"Must be at least {self.min_length} characters long",
                cursor_position=len(text),
            )

        if self.max_length is not None and length > self.max_length:
            raise ValidationError(
                message=f"Must be at most {self.max_length} characters long",
                cursor_position=len(text),
            )


class ChoiceValidator(Validator):
    """Validator that ensures input is one of the allowed choices."""

    def __init__(self, choices: List[str], case_sensitive: bool = True):
        self.choices = choices
        self.case_sensitive = case_sensitive

        if not case_sensitive:
            self.choices = [choice.lower() for choice in choices]

    def validate(self, document: object) -> None:
        text = _doc_text(document)

        if not text:
            raise ValidationError(
                message="Please select a value", cursor_position=len(text)
            )

        check_text = text if self.case_sensitive else text.lower()

        if check_text not in self.choices:
            choices_str = ", ".join(self.choices)
            raise ValidationError(
                message=f"Please choose from: {choices_str}", cursor_position=len(text)
            )


class CompositeValidator(Validator):
    """Validator that combines multiple validators."""

    def __init__(self, validators: List[Validator]):
        self.validators = validators

    def validate(self, document: Any) -> None:
        for validator in self.validators:
            try:
                validator.validate(document)
            except ValidationError:
                # Re-raise the first validation error encountered
                raise
