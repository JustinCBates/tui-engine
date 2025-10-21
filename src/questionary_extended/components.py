"""
Core components used throughout questionary-extended.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union


class ColumnType(Enum):
    """Types of table columns."""

    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    EMAIL = "email"
    URL = "url"
    SELECT = "select"
    BOOLEAN = "boolean"


@dataclass
class Choice:
    """Enhanced choice with additional metadata."""

    title: str
    value: Any = None
    disabled: bool = False
    checked: bool = False
    icon: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.value is None:
            self.value = self.title


@dataclass
class Separator:
    """Visual separator for choice lists."""

    title: str = ""
    line_char: str = "-"


@dataclass
class Column:
    """Table column definition."""

    name: str
    type: ColumnType = ColumnType.TEXT
    width: int = 20
    required: bool = False
    default: Any = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    choices: Optional[List[str]] = None
    validator: Optional[Callable] = None
    formatter: Optional[Callable] = None


@dataclass
class TableRow:
    """Table row data."""

    data: Dict[str, Any]
    index: int = 0
    selected: bool = False


@dataclass
class TreeNode:
    """Tree structure node."""

    name: str
    value: Any = None
    children: List["TreeNode"] = field(default_factory=list)
    expanded: bool = False
    icon: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.value is None:
            self.value = self.name

    def add_child(self, node: "TreeNode") -> "TreeNode":
        """Add a child node."""
        self.children.append(node)
        return self

    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return len(self.children) == 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any], name: str = "root") -> "TreeNode":
        """Create tree from nested dictionary."""
        node = cls(name=name)

        for key, value in data.items():
            if isinstance(value, dict):
                child = cls.from_dict(value, key)
                node.add_child(child)
            elif isinstance(value, list):
                for item in value:
                    child = cls(name=str(item), value=item)
                    node.add_child(child)
            else:
                child = cls(name=key, value=value)
                node.add_child(child)

        return node


@dataclass
class ProgressStep:
    """Progress tracking step."""

    name: str
    description: str
    question: Optional[Dict[str, Any]] = None
    completed: bool = False
    skipped: bool = False
    result: Any = None

    def to_question_dict(self) -> Dict[str, Any]:
        """Convert to questionary question format."""
        if self.question:
            return {"name": self.name, "message": self.description, **self.question}
        return {
            "type": "confirm",
            "name": self.name,
            "message": f"Complete step: {self.description}",
            "default": True,
        }


@dataclass
class ValidationResult:
    """Result of input validation."""

    valid: bool
    error_message: Optional[str] = None
    formatted_value: Any = None


@dataclass
class FormField:
    """Form field definition."""

    name: str
    type: str
    message: str
    required: bool = False
    default: Any = None
    validator: Optional[Callable] = None
    when: Optional[Callable] = None
    choices: Optional[List[Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Tag:
    """Tag for multi-tag selection."""

    name: str
    color: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


@dataclass
class ColorInfo:
    """Color information with multiple format support."""

    hex: str
    rgb: tuple[int, int, int]
    hsl: tuple[int, int, int]
    name: Optional[str] = None

    @classmethod
    def from_hex(cls, hex_color: str) -> "ColorInfo":
        """Create from hex color."""
        # Remove # if present
        hex_color = hex_color.lstrip("#")

        # Convert hex to RGB
        rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        # Convert RGB to HSL (simplified)
        r, g, b = [x / 255.0 for x in rgb]
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val

        # Lightness
        l = (max_val + min_val) / 2

        if diff == 0:
            h = s = 0
        else:
            # Saturation
            s = (
                diff / (2 - max_val - min_val)
                if l > 0.5
                else diff / (max_val + min_val)
            )

            # Hue
            if max_val == r:
                h = ((g - b) / diff + (6 if g < b else 0)) / 6
            elif max_val == g:
                h = ((b - r) / diff + 2) / 6
            else:
                h = ((r - g) / diff + 4) / 6

        hsl = (int(h * 360), int(s * 100), int(l * 100))

        return cls(hex=f"#{hex_color}", rgb=rgb, hsl=hsl)
