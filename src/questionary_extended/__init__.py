"""
Questionary Extended - Advanced extensions for the questionary CLI prompt library.

This package provides advanced input types, enhanced UI components, workflow management,
and data integration features for building sophisticated command-line interfaces.
"""

try:
    from importlib.metadata import version
except ImportError:
    # Python < 3.8
    from importlib_metadata import version

from .prompts import (
    # Basic enhanced prompts
    enhanced_text,
    rich_text,
    
    # Numeric prompts  
    number,
    integer,
    float_input,
    percentage,
    
    # Date/Time prompts
    date,
    time, 
    datetime_input,
    
    # Color prompts
    color,
    
    # Selection prompts
    tree_select,
    multi_level_select,
    tag_select,
    fuzzy_select,
    grouped_select,
    
    # Advanced input prompts
    rating,
    slider,
    table,
    
    # Workflow prompts
    form,
    wizard,
    progress_tracker,
)

from .components import (
    Choice,
    Separator,
    Column,
    TableRow,
    TreeNode,
    ProgressStep,
)

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

__version__ = version("questionary-extended")

__all__ = [
    # Version
    "__version__",
    
    # Prompts
    "enhanced_text",
    "rich_text", 
    "number",
    "integer",
    "float_input",
    "percentage",
    "date",
    "time",
    "datetime_input",
    "color",
    "tree_select",
    "multi_level_select", 
    "tag_select",
    "fuzzy_select",
    "grouped_select",
    "rating",
    "slider",
    "table",
    "form",
    "wizard",
    "progress_tracker",
    
    # Components
    "Choice",
    "Separator",
    "Column", 
    "TableRow",
    "TreeNode",
    "ProgressStep",
    
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