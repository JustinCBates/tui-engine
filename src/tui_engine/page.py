from typing import Any, List, Optional

from .container import Container
from .events import EventBus
from .page_state import PageState


class Page:
    def __init__(self, title: str = "") -> None:
        self.title = title
        self.page_state = PageState()
        self.events = EventBus()
        
        # Fixed page sections - always vertical layout
        self.title_section: Optional[Container] = None
        self.header_section: Optional[Container] = None
        self.body_section: Container = Container("body", variant="page-body")
        self.footer_section: Optional[Container] = None

        # floats: optional overlay elements that can be rendered above the
        # main layout. Adapters may inspect this list and render them using
        # prompt-toolkit Float/FloatContainer or similar mechanisms.
        self.floats: List[Container] = []

    def set_title_section(self, element: Container) -> "Page":
        """Set the title section of the page."""
        self.title_section = element
        return self

    def set_header_section(self, element: Container) -> "Page":
        """Set the header section of the page."""
        self.header_section = element
        return self

    def set_footer_section(self, element: Container) -> "Page":
        """Set the footer section of the page."""
        self.footer_section = element
        return self

    def add(self, element: Container) -> "Page":
        """Add element to the body section."""
        self.body_section.add(element)
        return self

    def container(self, name: str, variant: str = "container", **kwargs: Any) -> Container:
        """Create a container in the body section."""
        # Accept **kwargs for forward-compatibility with factory-style callers.
        return self.body_section.child(name, variant=variant)

    def title_section_container(self, name: str, variant: str = "title", **kwargs: Any) -> Container:
        """Create or get a container in the title section."""
        if self.title_section is None:
            self.title_section = Container("title-section", variant="page-title-section")
        return self.title_section.child(name, variant=variant)

    def header_section_container(self, name: str, variant: str = "header", **kwargs: Any) -> Container:
        """Create or get a container in the header section."""
        if self.header_section is None:
            self.header_section = Container("header-section", variant="page-header-section")
        return self.header_section.child(name, variant=variant)

    def footer_section_container(self, name: str, variant: str = "footer", **kwargs: Any) -> Container:
        """Create or get a container in the footer section."""
        if self.footer_section is None:
            self.footer_section = Container("footer-section", variant="page-footer-section")
        return self.footer_section.child(name, variant=variant)

    def render(self, width: int = 80) -> List[str]:
        """Render page with fixed vertical structure: Title, Header, Body, Footer."""
        lines: List[str] = []
        
        # Page title (if set)
        if self.title:
            lines.append(self.title)
            lines.append("=" * min(len(self.title), width))
        
        # Title section (optional)
        if self.title_section:
            lines.extend(self.title_section.get_render_lines(width))
            lines.append("")  # Separator
        
        # Header section (optional)
        if self.header_section:
            lines.extend(self.header_section.get_render_lines(width))
            lines.append("")  # Separator
        
        # Body section (always present)
        lines.extend(self.body_section.get_render_lines(width))
        
        # Footer section (optional)
        if self.footer_section:
            lines.append("")  # Separator
            lines.extend(self.footer_section.get_render_lines(width))
        
        return lines

    def to_prompt_toolkit_layout(self):
        """Convert page to prompt-toolkit Layout with fixed vertical structure.
        
        Note: This will be called by the App class, not directly by users.
        The App manages the overall application lifecycle and focus.
        """
        from prompt_toolkit.layout import Layout, HSplit
        
        sections = []
        
        # Title section (optional)
        if self.title_section:
            title_frame = self.title_section.to_prompt_toolkit()
            sections.append(title_frame)
        
        # Header section (optional)
        if self.header_section:
            header_frame = self.header_section.to_prompt_toolkit()
            sections.append(header_frame)
        
        # Body section (always present, gets remaining space)
        body_frame = self.body_section.to_prompt_toolkit()
        sections.append(body_frame)
        
        # Footer section (optional)  
        if self.footer_section:
            footer_frame = self.footer_section.to_prompt_toolkit()
            sections.append(footer_frame)
        
        # Create vertical layout of sections
        root = HSplit(sections)
        
        return Layout(root)

    def run_application(self, fullscreen: bool = False, **adapter_opts: Any) -> None:
        """DEPRECATED: Use App.run() instead.
        
        In the new architecture, App manages application lifecycle,
        not individual Pages.
        """
        raise RuntimeError("Use App.run() instead. Page.run_application() is deprecated.")

    def add_float(self, element: Container, **placement: Any) -> "Page":
        """Register an overlay/float element for this page.

        This is a minimal API used by tests to ensure adapters can discover
        and render floating overlays. The method stores the provided element
        in the page.floats list and returns self for chaining.
        """
        try:
            # Store placement metadata (top/right/left/bottom/offset) on
            # the float element so adapters can position it when rendering.
            if placement:
                try:
                    for k, v in placement.items():
                        element.metadata.setdefault(k, v)
                except Exception:
                    pass
            self.floats.append(element)
            # Also attach to the body section so adapters that receive the
            # body section (instead of the Page object) can discover floats easily.
            try:
                if not hasattr(self.body_section, 'floats'):
                    self.body_section.floats = []
                self.body_section.floats.append(element)
            except Exception:
                pass
        except Exception:
            # Best-effort: if floats aren't supported, ignore silently.
            pass
        return self
