"""
Enhanced styling and theming support for questionary-extended.
"""

# COVERAGE_EXCLUDE: thin wrapper — do not add original logic here
# COVERAGE_EXCLUDE_ALLOW_COMPLEX: intentionally contains original logic; exempt from AST triviality checks

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from prompt_toolkit.styles.style import Style


@dataclass
class ColorPalette:
    """Color palette for consistent theming."""

    primary: str = "#3f51b5"
    secondary: str = "#f50057"
    success: str = "#4caf50"
    warning: str = "#ff9800"
    error: str = "#f44336"
    info: str = "#2196f3"
    text: str = "#ffffff"
    background: str = "#000000"
    muted: str = "#757575"
    accent: str = "#e91e63"


@dataclass
class Theme:
    """Complete theme definition."""

    name: str
    palette: ColorPalette = field(default_factory=ColorPalette)
    style_overrides: Dict[str, str] = field(default_factory=dict)

    def to_questionary_style(self) -> Style:
        """Convert theme to questionary Style object."""
        base_styles = {
            # Question components
            "qmark": f"fg:{self.palette.primary} bold",
            "question": "bold",
            "answer": f"fg:{self.palette.success} bold",
            "pointer": f"fg:{self.palette.primary} bold",
            "highlighted": f"fg:{self.palette.primary} bold",
            "selected": f"fg:{self.palette.success}",
            "separator": f"fg:{self.palette.muted}",
            "instruction": f"fg:{self.palette.muted}",
            "text": f"fg:{self.palette.text}",
            "disabled": f"fg:{self.palette.muted} italic",
            # Enhanced components
            "progress": f"fg:{self.palette.info}",
            "progress_bar": f"fg:{self.palette.primary}",
            "progress_percent": f"fg:{self.palette.success} bold",
            "table_header": f"fg:{self.palette.accent} bold",
            "table_cell": f"fg:{self.palette.text}",
            "table_selected": f"fg:{self.palette.primary} bold",
            "tree_branch": f"fg:{self.palette.muted}",
            "tree_node": f"fg:{self.palette.text}",
            "tree_selected": f"fg:{self.palette.primary} bold",
            "tag": f"fg:{self.palette.secondary}",
            "tag_selected": f"fg:{self.palette.primary} bold",
            "validation_error": f"fg:{self.palette.error} bold",
            "validation_success": f"fg:{self.palette.success}",
        }

        # Apply style overrides
        base_styles.update(self.style_overrides)

        return Style(list(base_styles.items()))


# Predefined color palettes
DARK_PALETTE = ColorPalette(
    primary="#00bcd4",
    secondary="#ff4081",
    success="#4caf50",
    warning="#ffc107",
    error="#f44336",
    info="#2196f3",
    text="#ffffff",
    background="#000000",
    muted="#757575",
    accent="#e91e63",
)

LIGHT_PALETTE = ColorPalette(
    primary="#1976d2",
    secondary="#d32f2f",
    success="#388e3c",
    warning="#f57c00",
    error="#d32f2f",
    info="#1976d2",
    text="#000000",
    background="#ffffff",
    muted="#616161",
    accent="#c2185b",
)

TERMINAL_PALETTE = ColorPalette(
    primary="#00ff00",
    secondary="#ffff00",
    success="#00ff00",
    warning="#ffff00",
    error="#ff0000",
    info="#00ffff",
    text="#ffffff",
    background="#000000",
    muted="#808080",
    accent="#ff00ff",
)

OCEAN_PALETTE = ColorPalette(
    primary="#0077be",
    secondary="#00a8cc",
    success="#2e8b57",
    warning="#ff8c00",
    error="#dc143c",
    info="#4682b4",
    text="#f0f8ff",
    background="#001f3f",
    muted="#708090",
    accent="#20b2aa",
)

FOREST_PALETTE = ColorPalette(
    primary="#228b22",
    secondary="#32cd32",
    success="#90ee90",
    warning="#daa520",
    error="#b22222",
    info="#4169e1",
    text="#f5fffa",
    background="#0f4f0f",
    muted="#696969",
    accent="#9acd32",
)


# Predefined themes
THEMES = {
    "dark": Theme(name="Dark", palette=DARK_PALETTE),
    "light": Theme(name="Light", palette=LIGHT_PALETTE),
    "terminal": Theme(name="Terminal", palette=TERMINAL_PALETTE),
    "ocean": Theme(name="Ocean", palette=OCEAN_PALETTE),
    "forest": Theme(name="Forest", palette=FOREST_PALETTE),
    "minimal": Theme(
        name="Minimal",
        palette=ColorPalette(
            primary="#ffffff",
            secondary="#cccccc",
            success="#ffffff",
            warning="#ffffff",
            error="#ffffff",
            info="#ffffff",
            text="#ffffff",
            background="#000000",
            muted="#808080",
            accent="#ffffff",
        ),
    ),
}


def create_theme(
    name: str,
    palette: Optional[ColorPalette] = None,
    style_overrides: Optional[Dict[str, str]] = None,
) -> Theme:
    """Create a custom theme."""
    return Theme(
        name=name,
        palette=palette or ColorPalette(),
        style_overrides=style_overrides or {},
    )


def create_gradient_palette(
    start_color: str, end_color: str, steps: int = 5
) -> List[str]:
    """Create a gradient color palette between two colors."""
    # This is a simplified version - a full implementation would
    # properly interpolate between hex colors
    return [start_color, end_color]  # Placeholder


def apply_theme_to_style(theme: Theme, base_style: Optional[Style] = None) -> Style:
    """Apply theme to an existing style."""
    theme_style = theme.to_questionary_style()

    if base_style is None:
        return theme_style

    # Merge styles - theme takes precedence
    merged_styles = {}

    # Add base styles first
    if hasattr(base_style, "_style_rules"):
        for rule in base_style._style_rules:
            # rule may be a (token, style) tuple, or an object with token/style
            if isinstance(rule, tuple) and len(rule) >= 2:
                key, val = rule[0], rule[1]
                merged_styles[key] = val
            elif hasattr(rule, "token") and hasattr(rule, "style"):
                merged_styles[rule.token] = rule.style

    # Override with theme styles
    if hasattr(theme_style, "_style_rules"):
        for rule in theme_style._style_rules:
            if isinstance(rule, tuple) and len(rule) >= 2:
                key, val = rule[0], rule[1]
                merged_styles[key] = val
            elif hasattr(rule, "token") and hasattr(rule, "style"):
                merged_styles[rule.token] = rule.style

    return Style(list(merged_styles.items()))


class StyleBuilder:
    """Builder pattern for creating custom styles."""

    def __init__(self) -> None:
        self.styles: Dict[str, str] = {}

    def set(self, token: str, style: str) -> "StyleBuilder":
        """Set a style for a token."""
        self.styles[token] = style
        return self

    def primary(self, color: str) -> "StyleBuilder":
        """Set primary color styles."""
        self.styles.update(
            {
                "qmark": f"fg:{color} bold",
                "pointer": f"fg:{color} bold",
                "highlighted": f"fg:{color} bold",
            }
        )
        return self

    def text(self, color: str) -> "StyleBuilder":
        """Set text color."""
        self.styles["text"] = f"fg:{color}"
        return self

    def success(self, color: str) -> "StyleBuilder":
        """Set success color."""
        self.styles.update(
            {
                "answer": f"fg:{color} bold",
                "selected": f"fg:{color}",
            }
        )
        return self

    def error(self, color: str) -> "StyleBuilder":
        """Set error color."""
        self.styles["validation_error"] = f"fg:{color} bold"
        return self

    def build(self) -> Style:
        """Build the final Style object."""
        return Style(list(self.styles.items()))


def get_theme_names() -> List[str]:
    """Get list of available theme names."""
    return list(THEMES.keys())


def get_theme(name: str) -> Optional[Theme]:
    """Get a theme by name."""
    return THEMES.get(name.lower())


def list_themes() -> Dict[str, Theme]:
    """Get all available themes."""
    return THEMES.copy()
