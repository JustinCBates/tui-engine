"""
Advanced prompt types that extend questionary's capabilities.
This is the main prompts module - imports working implementations from prompts_core.
"""

# COVERAGE_EXCLUDE_ALLOW_COMPLEX: thin wrapper — do not add original logic here

# (Coverage markers removed so prompt tests run in CI)

# Import working core implementations
import datetime as _datetime

# Import types for advanced features
from typing import Any, Dict, List, Optional, Union

import importlib
from types import SimpleNamespace

# Use the shared proxy as the module-level `questionary` object. This keeps
# imports safe and lets tests monkeypatch `questionary` attributes on this
# module when needed.
try:
    from ._questionary_proxy import questionary_proxy as questionary
except Exception:
    from types import SimpleNamespace

    def _questionary_placeholder(*a: object, **kw: object) -> object:
        raise NotImplementedError("questionary is not configured in this environment")

    questionary = SimpleNamespace(
        text=_questionary_placeholder,
        select=_questionary_placeholder,
        confirm=_questionary_placeholder,
        password=_questionary_placeholder,
        checkbox=_questionary_placeholder,
        autocomplete=_questionary_placeholder,
        path=_questionary_placeholder,
        prompt=_questionary_placeholder,
    )

def _resolve_questionary():
    _rt = importlib.import_module("questionary_extended._runtime")
    q = _rt.get_questionary()
    if q is None:
        raise ImportError(
            "`questionary` is not available. In tests call setup_questionary_mocks() to install a mock."
        )
    return q


def _lazy_factory(name: str):
    def _f(*a, **kw):
        q = _resolve_questionary()
        return getattr(q, name)(*a, **kw)

    return _f

from .components import Column, ProgressStep
try:
    # Prefer direct relative import (normal package import)
    from .prompts_core import LazyQuestion, _lazy_factory
except Exception:
    # Fallback for tests that load modules from a path where relative
    # imports may fail; import by absolute package name instead.
    import importlib as _il

    _pc = _il.import_module("questionary_extended.prompts_core")
    # Use _lazy_factory from the imported module when available; otherwise
    # fall back to the local _lazy_factory defined above. If the imported
    # object is a test-provided stub (e.g., types.SimpleNamespace) that
    # lacks the expected symbols, patch it in-place so subsequent imports
    # and code paths see a consistent API. This keeps the test harness's
    # practice of inserting lightweight stubs working without causing
    # AttributeError during isolated module loads.
    if hasattr(_pc, "_lazy_factory"):
        _lazy_factory = _pc._lazy_factory
    else:
        # provide local fallback and ensure the stub exposes it
        _lazy_factory = _lazy_factory
        try:
            setattr(_pc, "_lazy_factory", _lazy_factory)
        except Exception:
            # best-effort: if we can't patch the imported object, continue
            pass

    # LazyQuestion: prefer the imported class, otherwise provide a
    # compatible local implementation (mirrors prompts_core.LazyQuestion).
    if hasattr(_pc, "LazyQuestion"):
        LazyQuestion = _pc.LazyQuestion
    else:
        class LazyQuestion:
            def __init__(self, factory, *args, **kwargs):
                self._factory = factory
                self._args = args
                self._kwargs = kwargs

            def build(self):
                return self._factory(*self._args, **self._kwargs)

            def __call__(self):
                return self.build()

            def ask(self, *a, **kw):
                return self.build().ask(*a, **kw)

            def __repr__(self):
                factory_name = getattr(self._factory, "__name__", repr(self._factory))
                return f"<LazyQuestion factory={factory_name} args={self._args} kwargs={self._kwargs}>"
        # ensure the imported stub/module also exposes LazyQuestion to keep
        # future relative imports stable
        try:
            setattr(_pc, "LazyQuestion", LazyQuestion)
        except Exception:
            pass

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
) -> "LazyQuestion | Any":
    """
    Enhanced text input with placeholder, auto-complete, and history support.

    Returns a simple questionary.text for now.
    """
    return LazyQuestion(_lazy_factory("text"), message, default=default, **kwargs)


def rich_text(
    message: str,
    default: str = "",
    syntax_highlighting: Optional[str] = None,
    line_numbers: bool = False,
    **kwargs: Any,
) -> "LazyQuestion | Any":
    """
    Rich text input with syntax highlighting and formatting (stub).
    """
    return LazyQuestion(_lazy_factory("text"), message, default=default, **kwargs)


def number(
    message: str,
    default: Optional[Union[int, float]] = None,
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    step: Union[int, float] = 1,
    allow_float: bool = True,
    format_str: Optional[str] = None,
    **kwargs: Any,
) -> "LazyQuestion | Any":
    """
    Numeric input with validation and formatting.
    """
    validator = NumberValidator(
        min_value=min_value, max_value=max_value, allow_float=allow_float
    )

    return LazyQuestion(
        _lazy_factory("text"),
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
) -> "LazyQuestion | Any":
    """Integer input with validation."""
    return number(
        message, min_value=min_value, max_value=max_value, allow_float=False, **kwargs
    )


def float_input(
    message: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    **kwargs: Any,
) -> "LazyQuestion | Any":
    """Float input with validation."""
    return number(
        message, min_value=min_value, max_value=max_value, allow_float=True, **kwargs
    )


def percentage(message: str, **kwargs: Any) -> "LazyQuestion | Any":
    """Percentage input (0-100)."""
    return number(message, min_value=0, max_value=100, format_str="{:.1f}%", **kwargs)


def date(
    message: str,
    default: Optional[_datetime.date] = None,
    min_date: Optional[_datetime.date] = None,
    max_date: Optional[_datetime.date] = None,
    format_str: str = "%Y-%m-%d",
    **kwargs: Any,
)-> Any:
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

    q = _resolve_questionary()
    return q.text(message, default=default_str, validate=validator, **kwargs)


def time(
    message: str,
    default: Optional[_datetime.time] = None,
    format_str: str = "%H:%M:%S",
    **kwargs: Any,
) -> Any:
    """Time input with validation and formatting."""
    default_str = default.strftime(format_str) if default else ""
    q = _resolve_questionary()
    return q.text(message, default=default_str, **kwargs)


def datetime_input(
    message: str,
    default: Optional[_datetime.datetime] = None,
    format_str: str = "%Y-%m-%d %H:%M:%S",
    **kwargs: Any,
) -> Any:
    """Datetime input with validation and formatting."""
    default_str = default.strftime(format_str) if default else ""
    q = _resolve_questionary()
    return q.text(message, default=default_str, **kwargs)


def color(
    message: str,
    formats: Optional[List[str]] = None,
    preview: bool = True,
    palette: Optional[List[str]] = None,
    **kwargs: Any,
) -> Any:
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
    q = _resolve_questionary()
    return q.text(message, **kwargs)


def tree_select(
    message: str,
    choices: Dict[str, Any],
    expanded: bool = False,
    show_icons: bool = True,
    **kwargs: Any,
) -> "LazyQuestion | Any":
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
    return LazyQuestion(_lazy_factory("select"), message, choices=flat_choices, **kwargs)


def multi_level_select(
    message: str, choices: Dict[str, Any], breadcrumbs: bool = True, **kwargs: Any
) -> "LazyQuestion | Any":
    """Multi-level menu with breadcrumb navigation."""
    return tree_select(message, choices, **kwargs)


def tag_select(
    message: str,
    available_tags: List[str],
    max_tags: Optional[int] = None,
    allow_custom: bool = False,
    **kwargs: Any,
) -> "LazyQuestion | Any":
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
    return LazyQuestion(_lazy_factory("checkbox"), message, choices=available_tags, **kwargs)


def fuzzy_select(
    message: str,
    choices: List[str],
    min_score: float = 0.6,
    case_sensitive: bool = False,
    **kwargs: Any,
) -> "LazyQuestion | Any":
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
    return LazyQuestion(_lazy_factory("autocomplete"), message, choices=choices, **kwargs)


def grouped_select(
    message: str, groups: Dict[str, List[str]], collapsible: bool = True, **kwargs: Any
) -> "LazyQuestion | Any":
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
        q = _resolve_questionary()
        choices.append(q.Separator(f"--- {group_name} ---"))
        # Ensure each choice is questionary-compatible (str or dict)
        for c in group_choices:
            if isinstance(c, dict):
                choices.append(c)
            else:
                choices.append(str(c))

    return LazyQuestion(_lazy_factory("select"), message, choices=choices, **kwargs)


def rating(
    message: str,
    max_rating: int = 5,
    icon: str = "★",
    allow_zero: bool = False,
    **kwargs: Any,
) -> "LazyQuestion | Any":
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

    return LazyQuestion(_lazy_factory("select"), message, choices=choices, **kwargs)


def slider(
    message: str,
    min_value: Union[int, float] = 0,
    max_value: Union[int, float] = 100,
    step: Union[int, float] = 1,
    default: Optional[Union[int, float]] = None,
    **kwargs: Any,
) -> "LazyQuestion | Any":
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
) -> "LazyQuestion | Any":
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
        _lazy_factory("text"), f"{message} (Table input - implementation pending)", **kwargs
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
    q = _resolve_questionary()
    return q.prompt(questions, **kwargs)


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
    q = _resolve_questionary()
    return q.prompt(questions, **kwargs)


# Re-export canonical class name
ProgressTracker = CoreProgressTracker
