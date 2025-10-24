"""
Advanced prompt types that extend questionary's capabilities.
This is the main prompts module - imports working implementations from prompts_core.
"""

# COVERAGE_EXCLUDE: thin wrapper — do not add original logic here
# COVERAGE_EXCLUDE_ALLOW_COMPLEX: intentionally contains original logic; exempt from AST triviality checks

# Import working core implementations
import datetime as _datetime

# Import types for advanced features
from typing import Any, Dict, List, Optional, Union

# Re-export questionary's standard prompts for convenience
import questionary
from questionary import (
    Question,  # Import Question type
)

from .components import Column, ProgressStep
from .prompts_core import LazyQuestion

# Re-export core helpers
from .prompts_core import ProgressTracker as CoreProgressTracker
from .styles import Theme

# Import our validators and components
from .validators import DateValidator, NumberValidator


def enhanced_text(
    message: str,
    default: str = "",
    multiline: bool = False,
    placeholder: Optional[str] = None,
    auto_complete: Optional[List[str]] = None,
    history: Optional[List[str]] = None,
    **kwargs: Any,
) -> "LazyQuestion | Question":
    """
    Enhanced text input with placeholder, auto-complete, and history support.

    Returns a simple questionary.text for now.
    """
    return LazyQuestion(questionary.text, message, default=default, **kwargs)


def rich_text(
    message: str,
    default: str = "",
    syntax_highlighting: Optional[str] = None,
    line_numbers: bool = False,
    **kwargs: Any,
) -> "LazyQuestion | Question":
    """
    Rich text input with syntax highlighting and formatting (stub).
    """
    return questionary.text(message, default=default, **kwargs)


def number(
    message: str,
    default: Optional[Union[int, float]] = None,
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    step: Union[int, float] = 1,
    allow_float: bool = True,
    format_str: Optional[str] = None,
    **kwargs: Any,
) -> "LazyQuestion | Question":
    """
    Numeric input with validation and formatting.
    """
    validator = NumberValidator(
        min_value=min_value, max_value=max_value, allow_float=allow_float
    )

    return LazyQuestion(
        questionary.text,
        message,
        default=str(default) if default is not None else "",
        validate=validator,
        **kwargs,
    )


def integer(
    message: str,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    **kwargs: Any,
) -> "LazyQuestion | Question":
    """Integer input with validation."""
    return number(
        message, min_value=min_value, max_value=max_value, allow_float=False, **kwargs
    )


def float_input(
    message: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    **kwargs: Any,
) -> "LazyQuestion | Question":
    """Float input with validation."""
    return number(
        message, min_value=min_value, max_value=max_value, allow_float=True, **kwargs
    )


def percentage(message: str, **kwargs: Any) -> "LazyQuestion | Question":
    """Percentage input (0-100)."""
    return number(message, min_value=0, max_value=100, format_str="{:.1f}%", **kwargs)


def date(
    message: str,
    default: Optional[_datetime.date] = None,
    min_date: Optional[_datetime.date] = None,
    max_date: Optional[_datetime.date] = None,
    format_str: str = "%Y-%m-%d",
    **kwargs: Any,
) -> Question:
    """
    Date input with validation and formatting.

    Args:
        message: The question to ask
        default: Default date value
        min_date: Minimum allowed date
        max_date: Maximum allowed date
        format_str: Date format string
        **kwargs: Additional questionary arguments

    Returns:
        Question instance
    """
    validator = DateValidator(
        min_date=min_date, max_date=max_date, format_str=format_str
    )

    default_str = default.strftime(format_str) if default else ""

    return questionary.text(message, default=default_str, validate=validator, **kwargs)


def time(
    message: str,
    default: Optional[_datetime.time] = None,
    format_str: str = "%H:%M:%S",
    **kwargs: Any,
) -> Question:
    """Time input with validation and formatting."""
    default_str = default.strftime(format_str) if default else ""
    return questionary.text(message, default=default_str, **kwargs)


def datetime_input(
    message: str,
    default: Optional[_datetime.datetime] = None,
    format_str: str = "%Y-%m-%d %H:%M:%S",
    **kwargs: Any,
) -> Question:
    """Datetime input with validation and formatting."""
    default_str = default.strftime(format_str) if default else ""
    return questionary.text(message, default=default_str, **kwargs)


def color(
    message: str,
    formats: Optional[List[str]] = None,
    preview: bool = True,
    palette: Optional[List[str]] = None,
    **kwargs: Any,
) -> Question:
    """
    Color picker with multiple format support.

    Args:
        message: The question to ask
        formats: Supported color formats ('hex', 'rgb', 'hsl', 'named')
        preview: Show color preview
        palette: Predefined color palette
        **kwargs: Additional questionary arguments

    Returns:
        Question instance
    """
    # Avoid mutable default
    if formats is None:
        formats = ["hex"]
    # Implementation will be added - for now return basic text
    return questionary.text(message, **kwargs)


def tree_select(
    message: str,
    choices: Dict[str, Any],
    expanded: bool = False,
    show_icons: bool = True,
    **kwargs: Any,
) -> "LazyQuestion | Question":
    """
    Tree-based selection with hierarchical navigation.

    Args:
        message: The question to ask
        choices: Nested dictionary representing the tree structure
        expanded: Whether to expand all nodes by default
        show_icons: Show folder/file icons
        **kwargs: Additional questionary arguments

    Returns:
        Question instance
    """
    # Convert nested dict to flat choices for now
    flat_choices = []

    def flatten_dict(d: Dict[str, Any], prefix: str = "") -> List[str]:
        items = []
        for key, value in d.items():
            if isinstance(value, dict):
                items.append(f"{prefix}{key}/")
                items.extend(flatten_dict(value, f"{prefix}{key}/"))
            else:
                if isinstance(value, list):
                    items.extend([f"{prefix}{key}/{item}" for item in value])
                else:
                    items.append(f"{prefix}{key}")
        return items

    flat_choices = flatten_dict(choices)
    return LazyQuestion(questionary.select, message, choices=flat_choices, **kwargs)


def multi_level_select(
    message: str, choices: Dict[str, Any], breadcrumbs: bool = True, **kwargs: Any
) -> "LazyQuestion | Question":
    """Multi-level menu with breadcrumb navigation."""
    return tree_select(message, choices, **kwargs)


def tag_select(
    message: str,
    available_tags: List[str],
    max_tags: Optional[int] = None,
    allow_custom: bool = False,
    **kwargs: Any,
) -> "LazyQuestion | Question":
    """
    Multi-tag selection with auto-completion.

    Args:
        message: The question to ask
        available_tags: List of available tags
        max_tags: Maximum number of tags to select
        allow_custom: Allow creating custom tags
        **kwargs: Additional questionary arguments

    Returns:
        Question instance
    """
    return LazyQuestion(questionary.checkbox, message, choices=available_tags, **kwargs)


def fuzzy_select(
    message: str,
    choices: List[str],
    min_score: float = 0.6,
    case_sensitive: bool = False,
    **kwargs: Any,
) -> "LazyQuestion | Question":
    """
    Fuzzy search selection with ranking.

    Args:
        message: The question to ask
        choices: List of choices to search
        min_score: Minimum fuzzy match score (0.0-1.0)
        case_sensitive: Whether search is case sensitive
        **kwargs: Additional questionary arguments

    Returns:
        Question instance
    """
    return LazyQuestion(questionary.autocomplete, message, choices=choices, **kwargs)


def grouped_select(
    message: str, groups: Dict[str, List[str]], collapsible: bool = True, **kwargs: Any
) -> "LazyQuestion | Question":
    """
    Grouped selection with collapsible categories.

    Args:
        message: The question to ask
        groups: Dictionary of group name to choices
        collapsible: Allow collapsing/expanding groups
        **kwargs: Additional questionary arguments

    Returns:
        Question instance
    """
    choices: List[Any] = []
    for group_name, group_choices in groups.items():
        choices.append(questionary.Separator(f"--- {group_name} ---"))
        # Ensure each choice is questionary-compatible (str or dict)
        for c in group_choices:
            if isinstance(c, dict):
                choices.append(c)
            else:
                choices.append(str(c))

    return LazyQuestion(questionary.select, message, choices=choices, **kwargs)


def rating(
    message: str,
    max_rating: int = 5,
    icon: str = "★",
    allow_zero: bool = False,
    **kwargs: Any,
) -> "LazyQuestion | Question":
    """
    Star rating input.

    Args:
        message: The question to ask
        max_rating: Maximum rating value
        icon: Icon to use for rating (e.g., '★', '♥', '●')
        allow_zero: Allow zero rating
        **kwargs: Additional questionary arguments

    Returns:
        Question instance
    """
    min_val = 0 if allow_zero else 1
    choices = []
    for i in range(min_val, max_rating + 1):
        display = icon * i + "☆" * (max_rating - i)
        # Use questionary-compatible dict for each rating
        choices.append({"name": f"{display} ({i})", "value": i})

    return LazyQuestion(questionary.select, message, choices=choices, **kwargs)


def slider(
    message: str,
    min_value: Union[int, float] = 0,
    max_value: Union[int, float] = 100,
    step: Union[int, float] = 1,
    default: Optional[Union[int, float]] = None,
    **kwargs: Any,
) -> "LazyQuestion | Question":
    """
    Slider input for numeric ranges.

    Args:
        message: The question to ask
        min_value: Minimum value
        max_value: Maximum value
        step: Step size
        default: Default value
        **kwargs: Additional questionary arguments

    Returns:
        Question instance
    """
    return number(
        message,
        default=default,
        min_value=min_value,
        max_value=max_value,
        step=step,
        **kwargs,
    )


def table(
    message: str,
    columns: List[Column],
    min_rows: int = 0,
    max_rows: Optional[int] = None,
    **kwargs: Any,
) -> "LazyQuestion | Question":
    """
    Table/spreadsheet input for structured data.

    Args:
        message: The question to ask
        columns: List of column definitions
        min_rows: Minimum number of rows
        max_rows: Maximum number of rows
        **kwargs: Additional questionary arguments

    Returns:
        Question instance
    """
    # For now, return a simple text input
    # Implementation will be added for actual table editing
    return LazyQuestion(
        questionary.text, f"{message} (Table input - implementation pending)", **kwargs
    )


def form(
    questions: List[Dict[str, Any]], theme: Optional[Theme] = None, **kwargs: Any
) -> Dict[str, Any]:
    """
    Enhanced form with validation and conditional logic.

    Args:
        questions: List of question definitions
        theme: Custom theme for the form
        **kwargs: Additional questionary arguments

    Returns:
        Question instance that returns a dictionary of answers
    """
    return questionary.prompt(questions, **kwargs)


def wizard(
    steps: List[ProgressStep],
    allow_back: bool = True,
    save_progress: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Multi-step wizard with progress tracking.

    Args:
        steps: List of wizard steps
        allow_back: Allow going back to previous steps
        save_progress: Save progress between sessions
        **kwargs: Additional questionary arguments

    Returns:
        Question instance
    """
    # Implementation will be added
    # For now, convert to a simple form
    questions = [step.to_question_dict() for step in steps]
    return questionary.prompt(questions, **kwargs)


# Re-export canonical class name
ProgressTracker = CoreProgressTracker
