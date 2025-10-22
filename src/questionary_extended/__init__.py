"""
Questionary Extended - Advanced extensions for the questionary CLI prompt library.

This package provides advanced input types, enhanced UI components, workflow management,
and data integration features for building sophisticated command-line interfaces.
"""

# Version management
__version__ = "0.1.0"

try:
    from importlib.metadata import version

    __version__ = version("questionary-extended")
except ImportError:
    # Fallback to hardcoded version
    pass

# Import core functionality - start with basics that work
from .components import (
    Choice,
    ProgressStep,
    Separator,
    ValidationResult,
)

# Import existing prompts and utilities
from .prompts_core import (
    enhanced_text,
    form,
    integer,
    number,
    progress_tracker,
    rating,
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

# Export newly implemented core API (Page/Card/Assembly/components)
from .core import (
    Page,
    Card,
    Assembly,
    Component,
    text,
    select,
    confirm,
    password,
    checkbox,
    autocomplete,
    path,
    # convenience wrappers also available
    # autocomplete and path are available via core.component
    
    PageState,
)

__version__ = version("questionary-extended")

__all__ = [
    # Version
    "__version__",
    # Working prompts (core functionality)
    "enhanced_text",
    "number",
    "integer",
    "rating",
    "form",
    "progress_tracker",
    # Components
    "Choice",
    "Separator",
    "ProgressStep",
    "ValidationResult",
    # Validators
    "NumberValidator",
    "DateValidator",
    "EmailValidator",
    "URLValidator",
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
