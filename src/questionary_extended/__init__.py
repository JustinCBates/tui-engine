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
from .validators import (
    NumberValidator,
    DateValidator, 
    EmailValidator,
    URLValidator,
    RangeValidator,
    RegexValidator,
)

from .styles import (
    Theme,
    ColorPalette,
    create_theme,
    THEMES,
)

from .utils import (
    format_date,
    format_number,
    parse_color,
    render_markdown,
)

# Import working prompts from our core implementation
from .prompts_core import (
    # Basic enhanced prompts that work
    enhanced_text,
    number,
    integer,
    rating,
    form,
    progress_tracker,
)

from .components import (
    Choice,
    Separator,
    ProgressStep,
    ValidationResult,
)



from .styles import (
    Theme,
    ColorPalette,
    create_theme,
    THEMES,
)

from .utils import (
    format_date,
    format_number,
    parse_color,
    render_markdown,
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
]