"""
Advanced prompt types that extend questionary's capabilities.
This is the main prompts module - imports working implementations from prompts_core.
"""

# Import working core implementations
from datetime import date as Date
from datetime import datetime
from datetime import time as Time

# Import types for advanced features
from typing import Any, Dict, List, Optional, Union

# Re-export questionary's standard prompts for convenience
import questionary
from questionary import (
    Question,  # Import Question type
)

from .components import Choice, Column, ProgressStep
from .prompts_core import (
    enhanced_text,
    form,
    integer,
    number,
    progress_tracker,
    rating,
)
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
    **kwargs,
) -> Question:
    """
    Enhanced text input with placeholder, auto-complete, and history support.

    Args:
        message: The question to ask
        default: Default value
        multiline: Enable multiline input
        placeholder: Placeholder text to show when empty
        auto_complete: List of auto-completion suggestions
        history: List of previous inputs for history navigation
        **kwargs: Additional questionary arguments

    Returns:
        Question instance
    """
    # Implementation will be added
    return questionary.text(message, default=default, **kwargs)


def rich_text(
    message: str,
    default: str = "",
    syntax_highlighting: Optional[str] = None,
    line_numbers: bool = False,
    **kwargs,
) -> Question:
    """
    Rich text input with syntax highlighting and formatting.

    Args:
        message: The question to ask
        default: Default value
        syntax_highlighting: Language for syntax highlighting (e.g., 'python', 'json')
        line_numbers: Show line numbers
        **kwargs: Additional questionary arguments

    Returns:
        Question instance
    """
    # Implementation will be added
    return questionary.text(message, default=default, **kwargs)


def number(
    message: str,
    default: Optional[Union[int, float]] = None,
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    step: Union[int, float] = 1,
    allow_float: bool = True,
    format_str: Optional[str] = None,
    **kwargs,
) -> Question:
    """
    Numeric input with validation and formatting.

    Args:
        message: The question to ask
        default: Default numeric value
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        step: Step size for increment/decrement
        allow_float: Allow floating point numbers
        format_str: Format string for display (e.g., '${:.2f}')
        **kwargs: Additional questionary arguments

    Returns:
        Question instance
    """
    validator = NumberValidator(
        min_value=min_value, max_value=max_value, allow_float=allow_float
    )

    return questionary.text(
        message,
        default=str(default) if default is not None else "",
        validate=validator,
        **kwargs,
    )


def integer(
    message: str,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    **kwargs,
) -> Question:
    """Integer input with validation."""
    return number(
        message, min_value=min_value, max_value=max_value, allow_float=False, **kwargs
    )


def float_input(
    message: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    **kwargs,
) -> Question:
    """Float input with validation."""
    return number(
        message, min_value=min_value, max_value=max_value, allow_float=True, **kwargs
    )


def percentage(message: str, **kwargs) -> Question:
    """Percentage input (0-100)."""
    return number(message, min_value=0, max_value=100, format_str="{:.1f}%", **kwargs)


def date(
    message: str,
    default: Optional[Date] = None,
    min_date: Optional[Date] = None,
    max_date: Optional[Date] = None,
    format_str: str = "%Y-%m-%d",
    **kwargs,
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
    message: str, default: Optional[Time] = None, format_str: str = "%H:%M:%S", **kwargs
) -> Question:
    """Time input with validation and formatting."""
    default_str = default.strftime(format_str) if default else ""
    return questionary.text(message, default=default_str, **kwargs)


def datetime_input(
    message: str,
    default: Optional[datetime] = None,
    format_str: str = "%Y-%m-%d %H:%M:%S",
    **kwargs,
) -> Question:
    """Datetime input with validation and formatting."""
    default_str = default.strftime(format_str) if default else ""
    return questionary.text(message, default=default_str, **kwargs)


def color(
    message: str,
    formats: List[str] = ["hex"],
    preview: bool = True,
    palette: Optional[List[str]] = None,
    **kwargs,
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
    # Implementation will be added - for now return basic text
    return questionary.text(message, **kwargs)


def tree_select(
    message: str,
    choices: Dict[str, Any],
    expanded: bool = False,
    show_icons: bool = True,
    **kwargs,
) -> Question:
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
    return questionary.select(message, choices=flat_choices, **kwargs)


def multi_level_select(
    message: str, choices: Dict[str, Any], breadcrumbs: bool = True, **kwargs
) -> Question:
    """Multi-level menu with breadcrumb navigation."""
    return tree_select(message, choices, **kwargs)


def tag_select(
    message: str,
    available_tags: List[str],
    max_tags: Optional[int] = None,
    allow_custom: bool = False,
    **kwargs,
) -> Question:
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
    return questionary.checkbox(message, choices=available_tags, **kwargs)


def fuzzy_select(
    message: str,
    choices: List[str],
    min_score: float = 0.6,
    case_sensitive: bool = False,
    **kwargs,
) -> Question:
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
    return questionary.autocomplete(message, choices=choices, **kwargs)


def grouped_select(
    message: str, groups: Dict[str, List[str]], collapsible: bool = True, **kwargs
) -> Question:
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
    choices = []
    for group_name, group_choices in groups.items():
        choices.append(questionary.Separator(f"--- {group_name} ---"))
        choices.extend(group_choices)

    return questionary.select(message, choices=choices, **kwargs)


def rating(
    message: str,
    max_rating: int = 5,
    icon: str = "★",
    allow_zero: bool = False,
    **kwargs,
) -> Question:
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
        choices.append(Choice(title=f"{display} ({i})", value=i))

    return questionary.select(message, choices=choices, **kwargs)


def slider(
    message: str,
    min_value: Union[int, float] = 0,
    max_value: Union[int, float] = 100,
    step: Union[int, float] = 1,
    default: Optional[Union[int, float]] = None,
    **kwargs,
) -> Question:
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
    **kwargs,
) -> Question:
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
    return questionary.text(
        f"{message} (Table input - implementation pending)", **kwargs
    )


def form(
    questions: List[Dict[str, Any]], theme: Optional[Theme] = None, **kwargs
) -> Question:
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
    **kwargs,
) -> Question:
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


class progress_tracker:
    """
    Context manager for tracking progress through multi-step operations.

    Usage:
        with progress_tracker("Operation", total_steps=5) as progress:
            progress.step("Step 1...")
            # do work
            progress.step("Step 2...")
            # do work
            progress.complete("Done!")
    """

    def __init__(self, title: str, total_steps: int):
        self.title = title
        self.total_steps = total_steps
        self.current_step = 0

    def __enter__(self):
        print(f"🚀 {self.title}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            print("✅ Operation completed successfully!")
        else:
            print("❌ Operation failed!")

    def step(self, description: str):
        """Advance to the next step."""
        self.current_step += 1
        progress = (self.current_step / self.total_steps) * 100
        print(
            f"  [{self.current_step}/{self.total_steps}] ({progress:.1f}%) {description}"
        )

    def complete(self, message: str = "Complete!"):
        """Mark the operation as complete."""
        print(f"🎉 {message}")
