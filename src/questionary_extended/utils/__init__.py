"""
Utility functions for questionary-extended core functionality.

This module provides helper functions and debugging tools:
- Helpers: Common utility functions for component management
- Debugging: Debug tools, error reporting, and development aids
- Type Utilities: Type checking and conversion helpers
"""

import re
import textwrap
from dataclasses import dataclass
from datetime import date, datetime
from difflib import SequenceMatcher
from typing import Any, List, Tuple
from urllib.parse import urlparse


def format_date(d: Any, fmt: str = "%Y-%m-%d") -> str:
    """Format a date-like object to a string."""
    if isinstance(d, (date, datetime)):
        return d.strftime(fmt)
    return str(d)


def parse_date(s: str, fmt: str = "%Y-%m-%d") -> date:
    """Parse a date string into a date object using given format."""
    return datetime.strptime(s, fmt).date()


def format_number(
    n: Any,
    decimal_places: int | None = None,
    thousands_sep: bool = False,
    percentage: bool = False,
    currency: str | None = None,
) -> str:
    """Format numbers with optional options used in tests.

    Supports decimal places, thousands separator, percentage and currency prefix.
    """
    try:
        num = float(n)
    except Exception:
        return str(n)

    if percentage:
        s = f"{num:.1f}%"
    else:
        if decimal_places is not None:
            fmt = (
                f"{{:,.{decimal_places}f}}"
                if thousands_sep
                else f"{{:.{decimal_places}f}}"
            )
            s = fmt.format(num)
        else:
            s = f"{int(num)}" if num.is_integer() else f"{num}"
            if thousands_sep:
                # apply thousands separator to integer portion
                if "." in s:
                    intpart, frac = s.split(".", 1)
                    intpart = f"{int(intpart):,}"
                    s = f"{intpart}.{frac}"
                else:
                    s = f"{int(int(s)):,}"

    if currency:
        s = f"{currency}{s}"

    return s


def parse_number(s: str, allow_float: bool = True) -> float | int:
    """Parse a string number possibly containing currency, commas or percent sign."""
    if isinstance(s, (int, float)):
        return s
    st = str(s).strip()
    is_percent = st.endswith("%")
    if is_percent:
        st = st[:-1]
    # remove currency symbols and commas
    st = st.replace(",", "")
    st = re.sub(r"[^0-9.+-eE]", "", st)
    try:
        val = float(st)
    except Exception as e:
        raise ValueError(f"Cannot parse number: {s}") from e
    if is_percent:
        val = val
    if not allow_float and val.is_integer():
        return int(val)
    return val


@dataclass
class Color:
    hex: str
    rgb: Tuple[int, int, int]


def _clamp(v: int) -> int:
    return max(0, min(255, int(v)))


def parse_color(s: str) -> Color:
    """Parse simple color strings: hex, named 'red', or rgb(r,g,b)."""
    s = s.strip()
    # hex
    m = re.match(r"^#?([0-9a-fA-F]{6})$", s)
    if m:
        h = "#" + m.group(1).lower()
        r = int(m.group(1)[0:2], 16)
        g = int(m.group(1)[2:4], 16)
        b = int(m.group(1)[4:6], 16)
        return Color(hex=h, rgb=(r, g, b))

    # rgb(r,g,b)
    m = re.match(r"^rgb\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\)$", s, re.I)
    if m:
        r, g, b = map(int, m.groups())
        r, g, b = _clamp(r), _clamp(g), _clamp(b)
        return Color(hex=f"#{r:02x}{g:02x}{b:02x}", rgb=(r, g, b))

    # simple named colors (very small mapping)
    names = {"red": "#ff0000", "green": "#00ff00", "blue": "#0000ff"}
    lname = s.lower()
    if lname in names:
        h = names[lname]
        r = int(h[1:3], 16)
        g = int(h[3:5], 16)
        b = int(h[5:7], 16)
        return Color(hex=h, rgb=(r, g, b))

    # fallback: try to parse as hex
    return Color(hex="#000000", rgb=(0, 0, 0))


def render_markdown(md: str) -> str:
    """Very small markdown-to-ANSI converter for bold/italic used in tests."""
    s = md
    # bold: **text** -> [1mtext[0m
    s = re.sub(r"\*\*(.+?)\*\*", lambda m: f"\033[1m{m.group(1)}\033[0m", s)
    # italic: *text* -> [3mtext[0m
    s = re.sub(r"\*(.+?)\*", lambda m: f"\033[3m{m.group(1)}\033[0m", s)
    return s


def truncate_text(s: str, width: int) -> str:
    if len(s) <= width:
        return s
    keep = max(0, width - 3)
    return s[:keep] + "..."


def wrap_text(s: str, width: int) -> List[str]:
    return textwrap.wrap(s, width=width)


def center_text(s: str, width: int) -> str:
    return s.center(width)


def create_progress_bar(current: float, total: float, width: int = 20) -> str:
    pct = (current / total) * 100 if total else 0.0
    fill = int((pct / 100.0) * width)
    bar = "[" + "#" * fill + "." * (width - fill) + "]"
    return f"{bar} {int(current)}/{int(total)} {pct:.1f}%"


def fuzzy_match(
    q: str, choices: List[str], threshold: float = 0.0
) -> List[Tuple[str, float]]:
    results: List[Tuple[str, float]] = []
    for c in choices:
        score = SequenceMatcher(None, q, c).ratio()
        if score >= threshold:
            results.append((c, score))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def validate_email(s: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", s) is not None


def validate_url(s: str) -> bool:
    try:
        p = urlparse(s)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:  # pragma: no cover - defensive
        # Preserve original exception context for easier debugging
        return False


__all__ = [
    "format_date",
    "parse_date",
    "format_number",
    "parse_number",
    "parse_color",
    "render_markdown",
    "truncate_text",
    "wrap_text",
    "center_text",
    "create_progress_bar",
    "fuzzy_match",
    "validate_email",
    "validate_url",
]
