from typing import Any, Optional, Dict, Callable
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.filters import Condition

from .page import Page


class App:
    """TUI Application manager that handles pages, events, focus, and application lifecycle."""
    
    def __init__(self, title: str = "TUI Application"):
        self.title = title
        self.current_page: Optional[Page] = None
        self.pages: Dict[str, Page] = {}
        self.key_bindings = KeyBindings()
        self.style = Style.from_dict({
            "frame.border": "fg:#00aaff",
            "frame.label": "fg:#00aaff",
        })
        
        # Setup default key bindings
        self._setup_default_keybindings()

    def add_page(self, name: str, page: Page) -> "App":
        """Add a page to the application."""
        self.pages[name] = page
        if self.current_page is None:
            self.current_page = page
        return self

    def set_current_page(self, name: str) -> "App":
        """Set the current active page."""
        if name in self.pages:
            self.current_page = self.pages[name]
        else:
            raise KeyError(f"Page '{name}' not found")
        return self

    def page(self, name: str, title: str = "") -> Page:
        """Create and add a new page to the application."""
        page = Page(title=title)
        self.add_page(name, page)
        return page

    def run(self, fullscreen: bool = True, **kwargs: Any) -> None:
        """Run the TUI application."""
        if self.current_page is None:
            raise RuntimeError("No pages defined. Add at least one page before running.")
        
        # Create a function that returns the current layout
        def get_layout():
            return self.current_page.to_prompt_toolkit_layout()
        
        # Create and run application with dynamic layout
        app = Application(
            layout=get_layout(),
            key_bindings=self.key_bindings,
            style=self.style,
            full_screen=fullscreen,
            **kwargs
        )
        
        # Store reference to the app for layout updates
        self._current_app = app
        
        app.run()

    def _setup_default_keybindings(self) -> None:
        """Setup default key bindings for the application."""
        @self.key_bindings.add("tab")
        def _(event) -> None:
            event.app.layout.focus_next()

        @self.key_bindings.add("s-tab")
        def _(event) -> None:
            event.app.layout.focus_previous()

        @self.key_bindings.add("enter")
        def _(event) -> None:
            """Handle Enter key - move focus for single-line inputs."""
            try:
                focused_control = event.app.layout.current_control
                current_window = event.app.layout.current_window
                
                # Check if it's a BufferControl (TextArea)
                from prompt_toolkit.layout.controls import BufferControl
                if isinstance(focused_control, BufferControl):
                    # Check if it's single-line by looking at the content
                    if hasattr(current_window, 'content') and hasattr(current_window.content, 'multiline'):
                        # Only move focus if it's a single-line input
                        if not current_window.content.multiline:
                            event.app.layout.focus_next()
                    else:
                        # If we can't determine multiline status, try to move focus anyway
                        # This covers basic single-line inputs
                        event.app.layout.focus_next()
            except Exception:
                # If anything goes wrong, just ignore the Enter key
                pass

        @self.key_bindings.add("c-c")
        def _(event) -> None:
            event.app.exit()

    def add_keybinding(self, key: str, handler: Callable) -> "App":
        """Add a custom key binding to the application."""
        self.key_bindings.add(key)(handler)
        return self

    def set_style(self, style_dict: dict) -> "App":
        """Set custom styling for the application."""
        self.style = Style.from_dict(style_dict)
        return self

    def get_current_page(self) -> Optional[Page]:
        """Get the currently active page."""
        return self.current_page

    def has_page(self, name: str) -> bool:
        """Check if a page with the given name exists."""
        return name in self.pages

    def remove_page(self, name: str) -> "App":
        """Remove a page from the application."""
        if name in self.pages:
            page = self.pages[name]
            del self.pages[name]
            
            # If we removed the current page, switch to another one or set to None
            if self.current_page == page:
                self.current_page = next(iter(self.pages.values())) if self.pages else None
        
        return self

    def list_pages(self) -> list[str]:
        """Get a list of all page names."""
        return list(self.pages.keys())