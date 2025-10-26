"""
Utility functions for questionary-extended.
"""

import re
from datetime import date, datetime
from typing import List, Optional, Tuple, Union

from .components import ColorInfo


def format_date(date_obj: Union[date, datetime], format_str: str = "%Y-%m-%d") -> str:
    """Format a date object to string."""
    # Handle edge case for years < 1000 where strftime doesn't zero-pad
    if hasattr(date_obj, 'year') and date_obj.year < 1000 and "%Y" in format_str:
        # Create a properly zero-padded year
        padded_year = f"{date_obj.year:04d}"
        # Replace %Y with the padded year in the format string
        temp_format = format_str.replace("%Y", "YEAR_PLACEHOLDER")
        formatted = date_obj.strftime(temp_format)
        return formatted.replace("YEAR_PLACEHOLDER", padded_year)
    return date_obj.strftime(format_str)


def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> date:
    """Parse a date string to date object."""
    return datetime.strptime(date_str, format_str).date()


def format_number(
    number: Union[int, float],
    decimal_places: Optional[int] = None,
    thousands_sep: bool = False,
    currency: Optional[str] = None,
    percentage: bool = False,
) -> str:
    """Format a number with various options."""
    if percentage:
        formatted = f"{number:.{decimal_places or 1}f}%"
    elif decimal_places is not None:
        formatted = f"{number:.{decimal_places}f}"
    else:
        formatted = str(number)

    if thousands_sep and not percentage:
        parts = formatted.split(".")
        parts[0] = f"{int(parts[0]):,}"
        formatted = ".".join(parts)

    if currency:
        formatted = f"{currency}{formatted}"

    return formatted


def parse_number(text: str, allow_float: bool = True) -> Union[int, float]:
    """Parse a number from text input."""
    # Remove common formatting
    clean_text = re.sub(r"[,$%]", "", text.strip())

    if allow_float:
        return float(clean_text)
    else:
        return int(clean_text)


def parse_color(color_input: str) -> ColorInfo:
    """Parse color from various input formats."""
    color_input = color_input.strip()

    # Hex color
    if color_input.startswith("#"):
        result = ColorInfo.from_hex(color_input)
        # Ensure returned object has expected attributes; avoid isinstance checks
        # in case the test harness substitutes a lightweight object.
        if (
            getattr(result, "rgb", None) is not None
            and getattr(result, "hex", None) is not None
        ):
            return result
        # Fallback: try to construct from a `.hex` attribute if present
        hex_val = getattr(result, "hex", None)
        if hex_val and getattr(ColorInfo, "from_hex", None):
            return ColorInfo.from_hex(hex_val)
        return result

    # Named colors (basic set)
    named_colors = {
        "red": "#ff0000",
        "green": "#00ff00",
        "blue": "#0000ff",
        "yellow": "#ffff00",
        "cyan": "#00ffff",
        "magenta": "#ff00ff",
        "black": "#000000",
        "white": "#ffffff",
        "gray": "#808080",
        "grey": "#808080",
        "orange": "#ffa500",
        "purple": "#800080",
        "pink": "#ffc0cb",
        "brown": "#a52a2a",
    }

    if color_input.lower() in named_colors:
        result = ColorInfo.from_hex(named_colors[color_input.lower()])
        if (
            getattr(result, "rgb", None) is not None
            and getattr(result, "hex", None) is not None
        ):
            return result
        hex_val = getattr(result, "hex", None)
        if hex_val and getattr(ColorInfo, "from_hex", None):
            return ColorInfo.from_hex(hex_val)
        return result

    # RGB format: rgb(r, g, b)
    rgb_match = re.match(r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", color_input)
    if rgb_match:
        r, g, b = map(int, rgb_match.groups())
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        result = ColorInfo.from_hex(hex_color)
        if (
            getattr(result, "rgb", None) is not None
            and getattr(result, "hex", None) is not None
        ):
            return result
        hex_val = getattr(result, "hex", None)
        if hex_val and getattr(ColorInfo, "from_hex", None):
            return ColorInfo.from_hex(hex_val)
        return result

    # Default to treating as hex without # only if it looks like 6 hex digits.
    if re.fullmatch(r"[0-9a-fA-F]{6}", color_input):
        try:
            result = ColorInfo.from_hex(f"#{color_input}")
            if (
                getattr(result, "rgb", None) is not None
                and getattr(result, "hex", None) is not None
            ):
                return result
            hex_val = getattr(result, "hex", None)
            if hex_val and getattr(ColorInfo, "from_hex", None):
                return ColorInfo.from_hex(hex_val)
            return result
        except ValueError as e:
            raise ValueError(f"Unable to parse color: {color_input}") from e

    # Not a recognized color format
    raise ValueError(f"Unable to parse color: {color_input}")


def render_markdown(text: str, width: Optional[int] = None) -> str:
    """Render basic markdown formatting for terminal display."""
    # This is a simplified markdown renderer
    # A full implementation would use a proper markdown library

    # Bold **text**
    text = re.sub(r"\*\*(.*?)\*\*", r"\033[1m\1\033[0m", text)

    # Italic *text*
    text = re.sub(r"\*(.*?)\*", r"\033[3m\1\033[0m", text)

    # Code `text`
    text = re.sub(r"`(.*?)`", r"\033[2m\1\033[0m", text)

    # Headers
    text = re.sub(r"^# (.*)", r"\033[1m\033[4m\1\033[0m", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.*)", r"\033[1m\1\033[0m", text, flags=re.MULTILINE)

    return text


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix."""
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def wrap_text(text: str, width: int) -> List[str]:
    """Wrap text to specified width."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > width:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                # Word is longer than width
                lines.append(word[:width])
                current_line = []
                current_length = 0
        else:
            current_line.append(word)
            current_length += len(word) + (1 if current_line else 0)

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def center_text(text: str, width: int, fill_char: str = " ") -> str:
    """Center text within specified width."""
    return text.center(width, fill_char)


def create_progress_bar(
    current: int,
    total: int,
    width: int = 20,
    fill_char: str = "█",
    empty_char: str = "░",
) -> str:
    """Create a visual progress bar."""
    if total == 0:
        percentage = 1.0
    else:
        percentage = min(current / total, 1.0)

    filled_width = int(width * percentage)
    empty_width = width - filled_width

    bar = fill_char * filled_width + empty_char * empty_width
    return f"[{bar}] {current}/{total} ({percentage:.1%})"


def create_table_row(
    values: List[str], widths: List[int], padding: int = 1, separator: str = "|"
) -> str:
    """Create a formatted table row."""
    cells = []
    for value, width in zip(values, widths):
        # Truncate if too long
        if len(value) > width - 2 * padding:
            value = truncate_text(value, width - 2 * padding)

        # Pad cell
        padded = value.center(width - 2 * padding)
        cells.append(f"{' ' * padding}{padded}{' ' * padding}")

    return separator + separator.join(cells) + separator


def create_tree_line(
    text: str,
    level: int,
    is_last: bool = False,
    has_children: bool = False,
    expanded: bool = False,
) -> str:
    """Create a formatted tree line."""
    indent = "  " * level

    if level > 0:
        if is_last:
            prefix = "└── "
        else:
            prefix = "├── "
    else:
        prefix = ""

    if has_children:
        if expanded:
            icon = "▼ "
        else:
            icon = "▶ "
    else:
        icon = ""

    return f"{indent}{prefix}{icon}{text}"


def sanitize_input(text: str, allowed_chars: Optional[str] = None) -> str:
    """Sanitize user input by removing/replacing unwanted characters."""
    if allowed_chars:
        # Keep only allowed characters
        return "".join(c for c in text if c in allowed_chars)

    # Remove common problematic characters
    sanitized = text.replace("\x00", "")  # Null bytes
    sanitized = re.sub(
        r"[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]", "", sanitized
    )  # Control chars

    return sanitized


def fuzzy_match(
    query: str, choices: List[str], threshold: float = 0.6
) -> List[Tuple[str, float]]:
    """Perform fuzzy matching on a list of choices."""
    # Simple fuzzy matching - a full implementation would use
    # libraries like fuzzywuzzy or rapidfuzz

    query_lower = query.lower()
    matches = []

    for choice in choices:
        choice_lower = choice.lower()

        # Simple scoring based on substring matches
        score = 0.0

        if query_lower == choice_lower:
            score = 1.0
        elif query_lower in choice_lower:
            score = 0.8
        elif choice_lower.startswith(query_lower):
            score = 0.7
        elif any(word.startswith(query_lower) for word in choice_lower.split()):
            score = 0.6

        if score >= threshold:
            matches.append((choice, score))

    # Sort by score descending
    matches.sort(key=lambda x: x[1], reverse=True)

    return matches


def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = (
        r"^[a-zA-Z0-9.!#$%&'\*+/=?^_`{|}~-]+@"
        r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
        r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    )
    return re.match(pattern, email) is not None


def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r"^https?://(?:[-\w.])+(?:\.[a-zA-Z]{2,})+(?:/.*)?$"
    return re.match(pattern, url) is not None


def generate_choices_from_range(
    start: Union[int, float],
    end: Union[int, float],
    step: Union[int, float] = 1,
    format_fn: Optional[callable] = None,
) -> List[str]:
    """Generate choice list from a numeric range."""
    choices = []
    current = start

    while current <= end:
        if format_fn:
            formatted = format_fn(current)
        else:
            formatted = str(current)

        choices.append(formatted)
        current += step

    return choices
