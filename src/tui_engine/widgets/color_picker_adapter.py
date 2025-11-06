"""
ColorPicker adapter for TUI Engine with Questionary integration.

This module provides a comprehensive color selection interface with support for:
- Multiple color formats (hex, rgb, hsl, named colors)
- Color palette selection with predefined collections
- Real-time color preview with ANSI rendering
- Color wheel and picker interfaces
- Color history and favorites
- Professional styling with theme integration

Classes:
    ColorFormat: Enum for supported color formats
    ColorPalette: Predefined color collections
    ColorValidator: Color value validation
    ColorRenderer: Visual color representation
    EnhancedColorPickerAdapter: Feature-rich color picker
    ColorPickerAdapter: Backward-compatible wrapper

Dependencies:
    - questionary: For interactive prompts
    - colorsys: For color space conversions
    - re: For color format validation
    - typing: For type hints
"""

import colorsys
import re
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
import questionary
from questionary import Choice

# Import TUI Engine components
try:
    from ..themes import TUIEngineThemes
    from ..style_adapter import QuestionaryStyleAdapter
except ImportError:
    # Fallback for testing
    class TUIEngineThemes:
        @staticmethod
        def get_theme(variant: str) -> Dict[str, Any]:
            return {}
    
    class QuestionaryStyleAdapter:
        @staticmethod
        def convert_style(theme: Dict[str, Any]) -> Any:
            return None


class ColorFormat(Enum):
    """Supported color formats for input and output."""
    HEX = "hex"
    RGB = "rgb"
    HSL = "hsl"
    NAMED = "named"
    ANSI = "ansi"


class ColorPalette(Enum):
    """Predefined color palettes."""
    BASIC = "basic"
    WEB_SAFE = "web_safe"
    MATERIAL = "material"
    SOLARIZED = "solarized"
    TERMINAL = "terminal"
    CUSTOM = "custom"


@dataclass
class ColorInfo:
    """Color information with multiple format representations."""
    name: str = ""
    hex_value: str = "#000000"
    rgb: Tuple[int, int, int] = (0, 0, 0)
    hsl: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    ansi_code: Optional[int] = None
    preview: str = ""
    
    def __post_init__(self):
        """Generate preview after initialization."""
        self.preview = self._generate_preview()
    
    def _generate_preview(self) -> str:
        """Generate ANSI color preview."""
        r, g, b = self.rgb
        # Use RGB escape sequence for true color
        bg_color = f"\033[48;2;{r};{g};{b}m"
        reset = "\033[0m"
        return f"{bg_color}  {reset}"


class ColorValidator:
    """Validates color values in different formats."""
    
    HEX_PATTERN = re.compile(r'^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    RGB_PATTERN = re.compile(r'^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$')
    HSL_PATTERN = re.compile(r'^hsl\(\s*(\d{1,3})\s*,\s*(\d{1,3})%\s*,\s*(\d{1,3})%\s*\)$')
    
    NAMED_COLORS = {
        'black': '#000000', 'white': '#ffffff', 'red': '#ff0000',
        'green': '#008000', 'blue': '#0000ff', 'yellow': '#ffff00',
        'cyan': '#00ffff', 'magenta': '#ff00ff', 'silver': '#c0c0c0',
        'gray': '#808080', 'maroon': '#800000', 'olive': '#808000',
        'lime': '#00ff00', 'aqua': '#00ffff', 'teal': '#008080',
        'navy': '#000080', 'fuchsia': '#ff00ff', 'purple': '#800080',
        'orange': '#ffa500', 'pink': '#ffc0cb', 'brown': '#a52a2a'
    }
    
    @classmethod
    def validate_hex(cls, value: str) -> bool:
        """Validate hex color format."""
        return bool(cls.HEX_PATTERN.match(value))
    
    @classmethod
    def validate_rgb(cls, value: str) -> bool:
        """Validate RGB color format."""
        match = cls.RGB_PATTERN.match(value)
        if not match:
            return False
        r, g, b = map(int, match.groups())
        return all(0 <= val <= 255 for val in (r, g, b))
    
    @classmethod
    def validate_hsl(cls, value: str) -> bool:
        """Validate HSL color format."""
        match = cls.HSL_PATTERN.match(value)
        if not match:
            return False
        h, s, l = map(int, match.groups())
        return 0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100
    
    @classmethod
    def validate_named(cls, value: str) -> bool:
        """Validate named color."""
        return value.lower() in cls.NAMED_COLORS
    
    @classmethod
    def parse_color(cls, value: str) -> Optional[ColorInfo]:
        """Parse color string into ColorInfo."""
        value = value.strip()
        
        # Try hex format
        if cls.validate_hex(value):
            return cls._parse_hex(value)
        
        # Try RGB format
        if cls.validate_rgb(value):
            return cls._parse_rgb(value)
        
        # Try HSL format
        if cls.validate_hsl(value):
            return cls._parse_hsl(value)
        
        # Try named color
        if cls.validate_named(value):
            return cls._parse_named(value)
        
        return None
    
    @classmethod
    def _parse_hex(cls, hex_value: str) -> ColorInfo:
        """Parse hex color value."""
        # Remove # if present
        hex_value = hex_value.lstrip('#')
        
        # Expand 3-digit hex to 6-digit
        if len(hex_value) == 3:
            hex_value = ''.join([c*2 for c in hex_value])
        
        # Convert to RGB
        r = int(hex_value[0:2], 16)
        g = int(hex_value[2:4], 16)
        b = int(hex_value[4:6], 16)
        
        # Convert to HSL
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        hsl = (h*360, s*100, l*100)
        
        return ColorInfo(
            hex_value=f"#{hex_value.upper()}",
            rgb=(r, g, b),
            hsl=hsl
        )
    
    @classmethod
    def _parse_rgb(cls, rgb_value: str) -> ColorInfo:
        """Parse RGB color value."""
        match = cls.RGB_PATTERN.match(rgb_value)
        r, g, b = map(int, match.groups())
        
        # Convert to hex
        hex_value = f"#{r:02X}{g:02X}{b:02X}"
        
        # Convert to HSL
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        hsl = (h*360, s*100, l*100)
        
        return ColorInfo(
            hex_value=hex_value,
            rgb=(r, g, b),
            hsl=hsl
        )
    
    @classmethod
    def _parse_hsl(cls, hsl_value: str) -> ColorInfo:
        """Parse HSL color value."""
        match = cls.HSL_PATTERN.match(hsl_value)
        h, s, l = map(int, match.groups())
        
        # Convert to RGB
        r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
        rgb = (int(r*255), int(g*255), int(b*255))
        
        # Convert to hex
        hex_value = f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
        
        return ColorInfo(
            hex_value=hex_value,
            rgb=rgb,
            hsl=(h, s, l)
        )
    
    @classmethod
    def _parse_named(cls, name: str) -> ColorInfo:
        """Parse named color."""
        hex_value = cls.NAMED_COLORS[name.lower()]
        color_info = cls._parse_hex(hex_value)
        color_info.name = name.lower()
        return color_info


class ColorPaletteManager:
    """Manages predefined color palettes."""
    
    PALETTES = {
        ColorPalette.BASIC: [
            ('#000000', 'Black'), ('#FFFFFF', 'White'), ('#FF0000', 'Red'),
            ('#00FF00', 'Green'), ('#0000FF', 'Blue'), ('#FFFF00', 'Yellow'),
            ('#FF00FF', 'Magenta'), ('#00FFFF', 'Cyan'), ('#808080', 'Gray'),
            ('#800000', 'Maroon'), ('#008000', 'Dark Green'), ('#000080', 'Navy'),
            ('#808000', 'Olive'), ('#800080', 'Purple'), ('#008080', 'Teal'),
            ('#C0C0C0', 'Silver'), ('#FFA500', 'Orange'), ('#FFC0CB', 'Pink')
        ],
        
        ColorPalette.WEB_SAFE: [
            ('#000000', 'Black'), ('#000033', 'Dark Blue'), ('#000066', 'Blue'),
            ('#000099', 'Medium Blue'), ('#0000CC', 'Light Blue'), ('#0000FF', 'Blue'),
            ('#003300', 'Dark Green'), ('#003333', 'Dark Teal'), ('#003366', 'Steel Blue'),
            ('#003399', 'Royal Blue'), ('#0033CC', 'Blue'), ('#0033FF', 'Bright Blue'),
            ('#006600', 'Green'), ('#006633', 'Forest Green'), ('#006666', 'Teal'),
            ('#006699', 'Ocean Blue'), ('#0066CC', 'Sky Blue'), ('#0066FF', 'Light Blue')
        ],
        
        ColorPalette.MATERIAL: [
            ('#F44336', 'Red'), ('#E91E63', 'Pink'), ('#9C27B0', 'Purple'),
            ('#673AB7', 'Deep Purple'), ('#3F51B5', 'Indigo'), ('#2196F3', 'Blue'),
            ('#03A9F4', 'Light Blue'), ('#00BCD4', 'Cyan'), ('#009688', 'Teal'),
            ('#4CAF50', 'Green'), ('#8BC34A', 'Light Green'), ('#CDDC39', 'Lime'),
            ('#FFEB3B', 'Yellow'), ('#FFC107', 'Amber'), ('#FF9800', 'Orange'),
            ('#FF5722', 'Deep Orange'), ('#795548', 'Brown'), ('#607D8B', 'Blue Grey')
        ],
        
        ColorPalette.SOLARIZED: [
            ('#002B36', 'Base03'), ('#073642', 'Base02'), ('#586E75', 'Base01'),
            ('#657B83', 'Base00'), ('#839496', 'Base0'), ('#93A1A1', 'Base1'),
            ('#EEE8D5', 'Base2'), ('#FDF6E3', 'Base3'), ('#B58900', 'Yellow'),
            ('#CB4B16', 'Orange'), ('#DC322F', 'Red'), ('#D33682', 'Magenta'),
            ('#6C71C4', 'Violet'), ('#268BD2', 'Blue'), ('#2AA198', 'Cyan'),
            ('#859900', 'Green')
        ],
        
        ColorPalette.TERMINAL: [
            ('#000000', 'Black'), ('#800000', 'Dark Red'), ('#008000', 'Dark Green'),
            ('#808000', 'Dark Yellow'), ('#000080', 'Dark Blue'), ('#800080', 'Dark Magenta'),
            ('#008080', 'Dark Cyan'), ('#C0C0C0', 'Light Gray'), ('#808080', 'Dark Gray'),
            ('#FF0000', 'Red'), ('#00FF00', 'Green'), ('#FFFF00', 'Yellow'),
            ('#0000FF', 'Blue'), ('#FF00FF', 'Magenta'), ('#00FFFF', 'Cyan'),
            ('#FFFFFF', 'White')
        ]
    }
    
    @classmethod
    def get_palette(cls, palette_type: ColorPalette) -> List[ColorInfo]:
        """Get colors from a predefined palette."""
        colors = []
        for hex_value, name in cls.PALETTES.get(palette_type, []):
            color_info = ColorValidator.parse_color(hex_value)
            if color_info:
                color_info.name = name
                colors.append(color_info)
        return colors
    
    @classmethod
    def get_palette_choices(cls, palette_type: ColorPalette) -> List[Choice]:
        """Get questionary choices for a palette."""
        colors = cls.get_palette(palette_type)
        choices = []
        for color in colors:
            display = f"{color.preview} {color.name or color.hex_value}"
            choices.append(Choice(title=display, value=color))
        return choices


class ColorRenderer:
    """Renders colors with different visual representations."""
    
    @staticmethod
    def render_color_block(color: ColorInfo, width: int = 4) -> str:
        """Render a color as a block."""
        r, g, b = color.rgb
        bg_color = f"\033[48;2;{r};{g};{b}m"
        reset = "\033[0m"
        return f"{bg_color}{' ' * width}{reset}"
    
    @staticmethod
    def render_color_swatch(color: ColorInfo) -> str:
        """Render a color swatch with information."""
        block = ColorRenderer.render_color_block(color)
        info = f"HEX: {color.hex_value} RGB: {color.rgb} HSL: ({color.hsl[0]:.0f}°, {color.hsl[1]:.0f}%, {color.hsl[2]:.0f}%)"
        return f"{block} {info}"
    
    @staticmethod
    def render_palette_grid(colors: List[ColorInfo], columns: int = 8) -> str:
        """Render a palette as a grid."""
        lines = []
        for i in range(0, len(colors), columns):
            row_colors = colors[i:i+columns]
            blocks = [ColorRenderer.render_color_block(color) for color in row_colors]
            lines.append(' '.join(blocks))
        return '\n'.join(lines)


class EnhancedColorPickerAdapter:
    """
    Enhanced color picker with comprehensive color selection features.
    
    Features:
    - Multiple color formats (hex, rgb, hsl, named)
    - Predefined color palettes
    - Real-time color preview
    - Color history and favorites
    - Professional styling with themes
    - Validation and error handling
    """
    
    def __init__(
        self,
        message: str = "Select a color:",
        format_preference: ColorFormat = ColorFormat.HEX,
        allow_custom: bool = True,
        show_preview: bool = True,
        default_palette: ColorPalette = ColorPalette.BASIC,
        theme_variant: str = "professional_blue",
        **kwargs
    ):
        """
        Initialize the enhanced color picker.
        
        Args:
            message: Prompt message
            format_preference: Preferred color format for output
            allow_custom: Allow custom color input
            show_preview: Show color preview
            default_palette: Default palette to show
            theme_variant: Theme for styling
            **kwargs: Additional arguments
        """
        self.message = message
        self.format_preference = format_preference
        self.allow_custom = allow_custom
        self.show_preview = show_preview
        self.default_palette = default_palette
        self.theme_variant = theme_variant
        
        # Get theme and style
        self.theme = TUIEngineThemes.get_theme(theme_variant)
        self.style = QuestionaryStyleAdapter.convert_style(self.theme)
        
        # Color history and state
        self.color_history: List[ColorInfo] = []
        self.selected_color: Optional[ColorInfo] = None
        self.custom_palette: List[ColorInfo] = []
        
    def pick_color(self) -> Optional[ColorInfo]:
        """
        Interactive color selection process.
        
        Returns:
            Selected ColorInfo object or None if cancelled
        """
        try:
            # Show main menu
            choice = self._show_main_menu()
            
            if choice == "palette":
                return self._pick_from_palette()
            elif choice == "custom":
                return self._pick_custom_color()
            elif choice == "history":
                return self._pick_from_history()
            else:
                return None
                
        except KeyboardInterrupt:
            return None
    
    def _show_main_menu(self) -> Optional[str]:
        """Show the main color picker menu."""
        choices = [
            Choice(title="📋 Select from palette", value="palette"),
        ]
        
        if self.allow_custom:
            choices.append(Choice(title="🎨 Enter custom color", value="custom"))
        
        if self.color_history:
            choices.append(Choice(title="🕒 Recent colors", value="history"))
        
        choices.append(Choice(title="❌ Cancel", value="cancel"))
        
        return questionary.select(
            self.message,
            choices=choices,
            style=self.style
        ).ask()
    
    def _pick_from_palette(self) -> Optional[ColorInfo]:
        """Pick color from a predefined palette."""
        # First, choose palette
        palette_choices = [
            Choice(title="🎯 Basic colors", value=ColorPalette.BASIC),
            Choice(title="🌐 Web safe colors", value=ColorPalette.WEB_SAFE),
            Choice(title="🎨 Material colors", value=ColorPalette.MATERIAL),
            Choice(title="☀️ Solarized colors", value=ColorPalette.SOLARIZED),
            Choice(title="💻 Terminal colors", value=ColorPalette.TERMINAL),
        ]
        
        if self.custom_palette:
            palette_choices.insert(-1, Choice(title="⭐ Custom palette", value=ColorPalette.CUSTOM))
        
        palette_type = questionary.select(
            "Choose a color palette:",
            choices=palette_choices,
            default=self.default_palette,
            style=self.style
        ).ask()
        
        if not palette_type:
            return None
        
        # Get colors from selected palette
        if palette_type == ColorPalette.CUSTOM:
            colors = self.custom_palette
        else:
            colors = ColorPaletteManager.get_palette(palette_type)
        
        if not colors:
            print("No colors available in this palette.")
            return None
        
        # Show color selection
        choices = []
        for color in colors:
            display = f"{color.preview} {color.name or color.hex_value}"
            if self.show_preview:
                display += f" - {ColorRenderer.render_color_swatch(color)}"
            choices.append(Choice(title=display, value=color))
        
        selected_color = questionary.select(
            "Select a color:",
            choices=choices,
            style=self.style
        ).ask()
        
        if selected_color:
            self._add_to_history(selected_color)
            self.selected_color = selected_color
        
        return selected_color
    
    def _pick_custom_color(self) -> Optional[ColorInfo]:
        """Pick a custom color by entering color value."""
        format_choice = questionary.select(
            "Choose color format:",
            choices=[
                Choice(title="🔢 Hex (#RRGGBB)", value=ColorFormat.HEX),
                Choice(title="🎨 RGB (rgb(r,g,b))", value=ColorFormat.RGB),
                Choice(title="🌈 HSL (hsl(h,s%,l%))", value=ColorFormat.HSL),
                Choice(title="📝 Named color", value=ColorFormat.NAMED),
            ],
            style=self.style
        ).ask()
        
        if not format_choice:
            return None
        
        # Get color value based on format
        if format_choice == ColorFormat.HEX:
            value = questionary.text(
                "Enter hex color (e.g., #FF0000 or FF0000):",
                validate=lambda x: ColorValidator.validate_hex(x) or "Invalid hex color format",
                style=self.style
            ).ask()
        elif format_choice == ColorFormat.RGB:
            value = questionary.text(
                "Enter RGB color (e.g., rgb(255,0,0)):",
                validate=lambda x: ColorValidator.validate_rgb(x) or "Invalid RGB color format",
                style=self.style
            ).ask()
        elif format_choice == ColorFormat.HSL:
            value = questionary.text(
                "Enter HSL color (e.g., hsl(0,100%,50%)):",
                validate=lambda x: ColorValidator.validate_hsl(x) or "Invalid HSL color format",
                style=self.style
            ).ask()
        elif format_choice == ColorFormat.NAMED:
            available_colors = list(ColorValidator.NAMED_COLORS.keys())
            value = questionary.autocomplete(
                "Enter named color:",
                choices=available_colors,
                validate=lambda x: ColorValidator.validate_named(x) or "Unknown color name",
                style=self.style
            ).ask()
        
        if not value:
            return None
        
        # Parse the color
        color = ColorValidator.parse_color(value)
        if color:
            if self.show_preview:
                print(f"Preview: {ColorRenderer.render_color_swatch(color)}")
            
            # Confirm selection
            confirm = questionary.confirm(
                "Use this color?",
                style=self.style
            ).ask()
            
            if confirm:
                self._add_to_history(color)
                self.selected_color = color
                return color
        
        return None
    
    def _pick_from_history(self) -> Optional[ColorInfo]:
        """Pick a color from the history."""
        if not self.color_history:
            print("No colors in history.")
            return None
        
        choices = []
        for i, color in enumerate(reversed(self.color_history[-10:])):  # Show last 10
            display = f"{color.preview} {color.name or color.hex_value}"
            if self.show_preview:
                display += f" - {ColorRenderer.render_color_swatch(color)}"
            choices.append(Choice(title=display, value=color))
        
        return questionary.select(
            "Select from recent colors:",
            choices=choices,
            style=self.style
        ).ask()
    
    def _add_to_history(self, color: ColorInfo):
        """Add color to history."""
        # Remove if already exists
        self.color_history = [c for c in self.color_history if c.hex_value != color.hex_value]
        # Add to end
        self.color_history.append(color)
        # Keep only last 20
        self.color_history = self.color_history[-20:]
    
    def add_to_custom_palette(self, color: ColorInfo):
        """Add color to custom palette."""
        if color not in self.custom_palette:
            self.custom_palette.append(color)
    
    def get_selected_color(self, format_type: Optional[ColorFormat] = None) -> Optional[str]:
        """
        Get the selected color in the specified format.
        
        Args:
            format_type: Format to return (uses preference if None)
            
        Returns:
            Color string in the specified format
        """
        if not self.selected_color:
            return None
        
        format_type = format_type or self.format_preference
        
        if format_type == ColorFormat.HEX:
            return self.selected_color.hex_value
        elif format_type == ColorFormat.RGB:
            r, g, b = self.selected_color.rgb
            return f"rgb({r},{g},{b})"
        elif format_type == ColorFormat.HSL:
            h, s, l = self.selected_color.hsl
            return f"hsl({h:.0f},{s:.0f}%,{l:.0f}%)"
        elif format_type == ColorFormat.NAMED:
            return self.selected_color.name or self.selected_color.hex_value
        
        return self.selected_color.hex_value


class ColorPickerAdapter:
    """
    Backward-compatible ColorPicker adapter for TUI Engine.
    
    This adapter provides compatibility with existing TUI Engine code while
    offering enhanced functionality through the EnhancedColorPickerAdapter.
    
    For new code, consider using EnhancedColorPickerAdapter directly for
    access to all features and better type safety.
    """
    
    def __init__(
        self,
        widget: Optional[Any] = None,
        enhanced: bool = True,
        **kwargs
    ):
        """
        Initialize ColorPicker adapter.
        
        Args:
            widget: Original TUI Engine widget (for compatibility)
            enhanced: Whether to use enhanced features
            **kwargs: Additional arguments passed to enhanced adapter
        """
        self.widget = widget
        self.enhanced = enhanced
        
        if self.enhanced:
            # Use enhanced adapter
            self.adapter = EnhancedColorPickerAdapter(**kwargs)
        else:
            # Basic implementation for legacy compatibility
            self.message = kwargs.get('message', 'Select a color:')
            self.selected_color = None
    
    def pick_color(self) -> Optional[str]:
        """
        Pick a color and return as string.
        
        Returns:
            Color string in hex format
        """
        if self.enhanced:
            color_info = self.adapter.pick_color()
            return color_info.hex_value if color_info else None
        else:
            # Basic color selection
            basic_colors = [
                Choice(title="🔴 Red", value="#FF0000"),
                Choice(title="🟢 Green", value="#00FF00"),
                Choice(title="🔵 Blue", value="#0000FF"),
                Choice(title="🟡 Yellow", value="#FFFF00"),
                Choice(title="🟣 Purple", value="#800080"),
                Choice(title="🟠 Orange", value="#FFA500"),
                Choice(title="⚫ Black", value="#000000"),
                Choice(title="⚪ White", value="#FFFFFF"),
            ]
            
            return questionary.select(
                self.message,
                choices=basic_colors
            ).ask()
    
    def get_selected_color(self, format_type: str = "hex") -> Optional[str]:
        """Get selected color in specified format."""
        if self.enhanced:
            format_enum = ColorFormat(format_type) if format_type in [f.value for f in ColorFormat] else ColorFormat.HEX
            return self.adapter.get_selected_color(format_enum)
        else:
            return self.selected_color
    
    def set_palette(self, palette_name: str):
        """Set the color palette."""
        if self.enhanced:
            try:
                palette = ColorPalette(palette_name)
                self.adapter.default_palette = palette
            except ValueError:
                pass  # Invalid palette name
    
    def __repr__(self) -> str:
        """String representation."""
        if self.enhanced:
            return f"<ColorPickerAdapter enhanced=True adapter={self.adapter}>"
        else:
            return f"<ColorPickerAdapter enhanced=False widget={self.widget}>"


# Convenience functions for common color picker scenarios
def pick_color(
    message: str = "Select a color:",
    format_preference: ColorFormat = ColorFormat.HEX,
    theme_variant: str = "professional_blue"
) -> Optional[str]:
    """
    Quick color picker function.
    
    Args:
        message: Prompt message
        format_preference: Output format
        theme_variant: Theme to use
        
    Returns:
        Selected color string or None
    """
    picker = EnhancedColorPickerAdapter(
        message=message,
        format_preference=format_preference,
        theme_variant=theme_variant
    )
    
    color = picker.pick_color()
    return picker.get_selected_color() if color else None


def pick_from_palette(
    palette: ColorPalette = ColorPalette.BASIC,
    message: str = "Select a color:",
    theme_variant: str = "professional_blue"
) -> Optional[str]:
    """
    Pick a color from a specific palette.
    
    Args:
        palette: Palette to show
        message: Prompt message
        theme_variant: Theme to use
        
    Returns:
        Selected color string or None
    """
    picker = EnhancedColorPickerAdapter(
        message=message,
        default_palette=palette,
        allow_custom=False,
        theme_variant=theme_variant
    )
    
    # Skip main menu and go directly to palette
    colors = ColorPaletteManager.get_palette(palette)
    choices = []
    for color in colors:
        display = f"{color.preview} {color.name or color.hex_value}"
        choices.append(Choice(title=display, value=color))
    
    selected = questionary.select(
        message,
        choices=choices,
        style=picker.style
    ).ask()
    
    return selected.hex_value if selected else None


def pick_custom_color(
    format_preference: ColorFormat = ColorFormat.HEX,
    message: str = "Enter a color:",
    theme_variant: str = "professional_blue"
) -> Optional[str]:
    """
    Pick a custom color by entering the value.
    
    Args:
        format_preference: Input/output format
        message: Prompt message
        theme_variant: Theme to use
        
    Returns:
        Selected color string or None
    """
    picker = EnhancedColorPickerAdapter(
        message=message,
        format_preference=format_preference,
        theme_variant=theme_variant
    )
    
    # Go directly to custom color input
    color = picker._pick_custom_color()
    return picker.get_selected_color() if color else None


# Export all public classes and functions
__all__ = [
    'ColorFormat',
    'ColorPalette', 
    'ColorInfo',
    'ColorValidator',
    'ColorPaletteManager',
    'ColorRenderer',
    'EnhancedColorPickerAdapter',
    'ColorPickerAdapter',
    'pick_color',
    'pick_from_palette',
    'pick_custom_color'
]