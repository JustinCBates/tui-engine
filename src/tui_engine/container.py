from typing import Any, List, Optional

from .element import Element
from .interfaces import IElement


class Container(IElement):
    def __init__(self, name: str, variant: str = "container", *, layout_hint: str = "vertical"):
        super().__init__(name, variant=variant)
        self.children: List[IElement] = []
        self.layout_hint = layout_hint
        self.focus_scope: bool = False
        self.include_hidden_in_validity: bool = False
        
        # Prompt-toolkit integration properties
        self.title: str = ""
        self.show_border: bool = True
        self.align: str = "left"  # "left", "center", "right"

    def add(self, child: IElement) -> "Container":
        child.parent = self
        self.children.append(child)
        self.mark_dirty()
        return self

    def remove(self, child: IElement) -> None:
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            self.mark_dirty()

    def child(self, name: str, variant: str = "container", **kwargs: Any) -> "Container":
        # kwargs are accepted for forward-compatibility with factory-style
        # constructors; keep them typed as Any to avoid mypy disallow_untyped_defs
        # errors while preserving runtime flexibility.
        c = Container(name, variant=variant)
        self.add(c)
        return c
    
    def set_title(self, title: str) -> "Container":
        """Set the title shown in the container border."""
        self.title = title
        return self

    def set_border(self, show_border: bool) -> "Container":
        """Set whether to show a border around this container."""
        self.show_border = show_border
        return self

    def set_layout_direction(self, direction: str) -> "Container":
        """Set layout direction: 'vertical' or 'horizontal'."""
        if direction not in ["vertical", "horizontal"]:
            raise ValueError(f"Invalid layout direction: {direction}. Use 'vertical' or 'horizontal'.")
        self.layout_hint = direction
        return self

    def set_align(self, align: str) -> "Container":
        """Set alignment for horizontal layouts: 'left', 'center', or 'right'."""
        if align not in ["left", "center", "right"]:
            raise ValueError(f"Invalid alignment: {align}. Use 'left', 'center', or 'right'.")
        self.align = align
        return self

    # NOTE: previously this class exposed convenience constructors for
    # concrete widgets (text/input/button). Those were removed to keep
    # `Container` strictly structural. Use the factories in
    # `tui_engine.widgets` and `container.add(...)` to attach widgets.

    def get_focusable_children(self) -> List[IElement]:
        return [c for c in self.children if getattr(c, "focusable", False)]

    def get_render_lines(self, width: int = 80) -> List[str]:
        lines: List[str] = []
        # simple header for container
        if self.variant and self.variant != "container":
            lines.append(f"[{self.variant.upper()}] {self.name}")
        for child in self.children:
            if not getattr(child, "visible", True):
                continue
            child_lines = child.get_render_lines(width)
            for ln in child_lines:
                lines.append("  " + ln)
        return lines

    def to_prompt_toolkit(self):
        """Convert container to prompt-toolkit widget structure."""
        from prompt_toolkit.layout import HSplit, VSplit
        from prompt_toolkit.layout.dimension import Dimension
        from prompt_toolkit.widgets import Frame
        from prompt_toolkit.layout.containers import Window
        
        # Convert children to prompt-toolkit widgets
        child_widgets = []
        for child in self.children:
            if not getattr(child, "visible", True):
                continue
                
            if hasattr(child, 'to_prompt_toolkit'):
                child_widgets.append(child.to_prompt_toolkit())
            else:
                # Fallback: create simple text display for basic elements
                from prompt_toolkit.widgets import Label
                lines = child.get_render_lines(80)
                text = "\n".join(lines) if lines else ""
                if text:
                    child_widgets.append(Label(text))
        
        # Create layout based on direction
        if not child_widgets:
            content = Window(width=Dimension(weight=1), height=Dimension(weight=1))
        elif self.layout_hint == "vertical":
            content = HSplit(child_widgets)
        else:  # horizontal
            # For horizontal layout, we can use alignment
            if self.align == "center":
                content = VSplit([
                    Window(width=Dimension(weight=1)),  # Left spacer
                    *child_widgets,  # Unpack the child widgets directly
                    Window(width=Dimension(weight=1))   # Right spacer
                ])
            elif self.align == "right":
                content = VSplit([
                    Window(width=Dimension(weight=1)),  # Left spacer
                    *child_widgets  # Unpack the child widgets directly
                ])
            else:  # left (default)
                content = VSplit(child_widgets)
        
        # Wrap in frame if border requested
        if self.show_border:
            title = self.title or self.name
            return Frame(content, title=title)
        else:
            return content
