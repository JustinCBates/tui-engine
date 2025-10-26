"""
Questionary Extended - Advanced extensions for the questionary CLI prompt library.

This package provides advanced input types, enhanced UI components, workflow management,
and data integration features for building sophisticated command-line interfaces.
"""

# Version management
# Default version (fallback when package metadata is unavailable)
__version__ = "0.1.0"

# Try to obtain distribution version when available (installed package).
# Don't raise if the package isn't installed in the environment (editable/dev tree).
try:
    from importlib.metadata import PackageNotFoundError, version

    try:
        __version__ = version("questionary-extended")
    except PackageNotFoundError:
        # Not an installed distribution; keep the default __version__.
        pass
except Exception:
    # importlib.metadata may be unavailable on very old Python runtimes.
    # Keep the default version in that case.
    pass

# Import core functionality - start with basics that work
from .components import (
    Choice,
    ProgressStep,
    Separator,
    ValidationResult,
)

# Export newly implemented core API (Page/Card/Assembly/components)
from .core import (
    AssemblyBase,
    Card,
    Component,
    # convenience wrappers also available
    # autocomplete and path are available via core.component
    PageState,
    autocomplete,
    checkbox,
    confirm,
    password,
    path,
    select,
    text,
)

# Provide a higher-level Page implementation that wires runtime execution.
from .page import Page  # noqa: E402

# Provide a higher-level Assembly implementation that wires runtime execution.
from .assembly import Assembly  # noqa: E402

from .prompts import rating

# Import existing prompts and utilities
from .prompts_core import (
    ProgressTracker,
    enhanced_text,
    form,
    integer,
    number,
)
from .styles import (
    THEMES,
    ColorPalette,
    Theme,
    create_theme,
)
from .utils import (
    format_date,
    format_number,
    parse_color,
    render_markdown,
)
from .validators import (
    DateValidator,
    EmailValidator,
    NumberValidator,
    RangeValidator,
    RegexValidator,
    URLValidator,
)

# NOTE: Do not attempt to re-resolve the package version here — doing so
# in a development environment (where the package isn't installed) can
# raise PackageNotFoundError and break simple imports. Version was
# resolved above when possible and otherwise remains the default.

__all__ = [
    # High-level containers
    "Page",
    "Assembly",
    # Advanced prompts
    "rating",
    "enhanced_text",
    "number",
    "integer",
    "form",
    "ProgressTracker",
    # Validators
    "DateValidator",
    "EmailValidator", 
    "NumberValidator",
    "RangeValidator",
    "RegexValidator",
    # Styles
    "Theme",
    "ColorPalette",
    "create_theme",
    "THEMES",
    # Utils
    "format_date",
    "format_number",
    "parse_color",
    "render_markdown",
    # Core wrappers (compatibility)
    "text",
    "select",
    "confirm",
    "password",
    "checkbox",
    "autocomplete",
    "path",
]


# NOTE: The lowercase `progress_tracker` factory was removed to keep the
# public API clean. Use the canonical `ProgressTracker` class instead.
