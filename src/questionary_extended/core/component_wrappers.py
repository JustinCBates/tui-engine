"""
Component wrappers for questionary-extended.

This module provides enhanced wrappers around questionary components,
maintaining full API compatibility while adding new capabilities.
"""

import uuid
import sys
import time
import re
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING
from .debug_mode import is_debug_mode
from .interfaces import RenderableComponent, SpaceRequirement, BufferDelta, ElementChangeEvent

if TYPE_CHECKING:
    from .form_navigation import SpatialFormNavigator


class Component(RenderableComponent):
    """
    Base wrapper class for questionary components.

    Provides enhanced functionality while maintaining questionary compatibility:
    - Enhanced validation with multiple validators
    - State integration and event hooks
    - Interface compliance with ComponentInterface and Renderable
    """

    def __init__(self, name: str, component_type: str, form_navigator: Optional["SpatialFormNavigator"] = None, **kwargs: Any) -> None:
        """
        Initialize a component wrapper.

        Args:
            name: Component name for state management
            component_type: Type of questionary component (text, select, etc.)
            form_navigator: Optional form navigator for tab navigation support
            **kwargs: Component configuration options
        """
        self._name = name
        self._component_type = component_type
        self.config = kwargs
        self.when_condition: Optional[str] = kwargs.get("when")
        self.validators: List[Callable[..., Any]] = []
        self._visible: bool = True  # Default visibility
        self._needs_render: bool = True
        self._last_rendered_lines: List[str] = []
        self._change_listeners: List[Callable[[ElementChangeEvent], None]] = []
        
        # Form navigation
        self._form_navigator = form_navigator
        if form_navigator and self.is_interactive():
            form_navigator.register_interactive_component(self)
        
        # Interactive component state
        self._is_active: bool = False  # Whether this component is currently active for input
        self._current_value: Any = kwargs.get("default", "")
        self._prompt_text: str = kwargs.get("message", f"Enter {name}:")
        self._prompt_position: Optional[int] = None  # Buffer position for interactive prompt

        # Extract questionary-compatible config
        self.questionary_config = {
            k: v for k, v in kwargs.items() if k not in ["when", "enhanced_validation"]
        }

    # =================================================================
    # SECTION CHILD INTERFACE METHODS (REQUIRED BY SectionChildInterface)
    # =================================================================
    
    def get_name(self) -> str:
        """Return the unique name of this element (for SectionChildInterface)."""
        return self.name
    
    def get_content(self) -> List[str]:
        """Return the rendered content lines (for SectionChildInterface)."""
        return self.get_render_lines()
    
    # =================================================================
    # SPATIAL AWARENESS METHODS (REQUIRED BY ElementInterface)
    # =================================================================
    
    def calculate_space_requirements(self) -> SpaceRequirement:
        """Calculate space requirements for this component."""
        if not self._visible:
            return SpaceRequirement(min_lines=0, current_lines=0, max_lines=0, preferred_lines=0)
        
        if self.is_interactive():
            # Interactive components need space for prompt and input area
            base_lines = 1  # Prompt line
            
            if self._component_type in ["text", "password"]:
                lines_needed = 1  # Single line input
            elif self._component_type == "select":
                lines_needed = 1  # Will expand dynamically if needed
            elif self._component_type == "confirm":
                lines_needed = 1
            elif self._component_type == "checkbox":
                options = self.config.get("choices", [])
                lines_needed = min(len(options), 5)  # Max 5 visible options
            else:
                lines_needed = 1
            
            total_lines = base_lines + lines_needed
            return SpaceRequirement(
                min_lines=base_lines,
                current_lines=total_lines,
                max_lines=total_lines + 2,  # Extra space for validation messages
                preferred_lines=total_lines
            )
        else:
            # Display-only components
            lines = self.get_render_lines()
            line_count = len(lines)
            return SpaceRequirement(
                min_lines=line_count,
                current_lines=line_count,
                max_lines=line_count,
                preferred_lines=line_count
            )
    
    def calculate_buffer_changes(self, target_lines: int) -> BufferDelta:
        """Calculate buffer changes needed for target line count."""
        current_lines = self.get_render_lines()
        current_count = len(current_lines)
        
        if target_lines == current_count:
            # No change needed
            return BufferDelta(
                line_updates=[],
                space_change=0
            )
        elif target_lines < current_count:
            # Need to compress
            compressed = self.compress_to_lines(target_lines)
            updates = [(i, line) for i, line in enumerate(compressed)]
            return BufferDelta(
                line_updates=updates,
                space_change=target_lines - current_count
            )
        else:
            # Have more space available - expand if possible
            updates = [(i, line) for i, line in enumerate(current_lines)]
            return BufferDelta(
                line_updates=updates,
                space_change=0  # We don't expand beyond natural size
            )
    
    def can_compress_to(self, target_lines: int) -> bool:
        """Check if component can compress to target line count."""
        if target_lines <= 0:
            return False
        
        space_req = self.calculate_space_requirements()
        return target_lines >= space_req.min_lines
    
    def compress_to_lines(self, target_lines: int) -> List[str]:
        """Compress component content to specific line count."""
        current_lines = self.get_render_lines()
        
        if target_lines >= len(current_lines):
            return current_lines
        
        if target_lines <= 0:
            return []
        
        if self._component_type == "text_section":
            # For text sections, show truncated content
            if target_lines == 1:
                return [f"📄 {self._name} (truncated)"]
            else:
                # Return first lines with ellipsis
                result = current_lines[:target_lines-1]
                result.append("...")
                return result
        else:
            # For other components, just truncate
            return current_lines[:target_lines]
    
    # =================================================================
    # EVENT SYSTEM METHODS (REQUIRED BY ElementInterface)
    # =================================================================
    
    def fire_change_event(self, change_type: str, space_delta: int = 0, **metadata: Any) -> None:
        """Fire change event to notify listeners."""
        event = ElementChangeEvent(
            element_name=self.name,
            element_type=self.element_type,
            change_type=change_type,
            space_delta=space_delta,
            metadata=metadata
        )
        
        for listener in self._change_listeners:
            try:
                listener(event)
            except Exception:
                # Don't let listener exceptions break the component
                pass
    
    def register_change_listener(self, listener: Callable[[ElementChangeEvent], None]) -> None:
        """Register listener for change events."""
        if listener not in self._change_listeners:
            self._change_listeners.append(listener)

    # =================================================================
    # ELEMENT INTERFACE IMPLEMENTATION
    # =================================================================

    # ElementInterface implementation
    @property
    def name(self) -> str:
        """Unique identifier for this component."""
        return self._name
    
    @property
    def element_type(self) -> str:
        """Type of element (always 'component')."""
        return "component"
    
    @property
    def visible(self) -> bool:
        """Whether this component is currently visible."""
        return self._visible
    
    def show(self) -> None:
        """Make this component visible."""
        if not self._visible:
            self._visible = True
            self._needs_render = True
    
    def hide(self) -> None:
        """Hide this component."""
        if self._visible:
            self._visible = False
            self._needs_render = True

    # ComponentInterface implementation
    @property
    def component_type(self) -> str:
        """Specific type of component (text_input, select, text_display, etc.)."""
        return self._component_type
    
    def is_interactive(self) -> bool:
        """Whether this component requires user interaction."""
        # Display-only components are not interactive
        return self._component_type not in ["text_display", "text_section", "text_status"]

    # Renderable implementation
    def get_render_lines(self) -> List[str]:
        """Get the lines this component should output."""
        if not self._visible:
            return []
        
        # Handle display-only components
        if self._component_type == "text_display":
            content = self.config.get("content", "")
            return [str(content)] if content else []
        
        elif self._component_type == "text_status":
            content = self.config.get("content", "")
            status_type = self.config.get("status_type", "info")
            
            # Simple status formatting
            if status_type == "error":
                prefix = "❌"
            elif status_type == "success":
                prefix = "✅"
            elif status_type == "warning":
                prefix = "⚠️"
            else:  # info
                prefix = "ℹ️"
            
            return [f"{prefix} {content}"] if content else []
        
        elif self._component_type == "text_section":
            content = self.config.get("content", "")
            return [f"📄 {content}"] if content else []
        
        # For interactive components, render prompt and current state
        elif self.is_interactive():
            lines = []
            
            # Add the prompt text with activity indicator
            if self._is_active:
                lines.append(f"? {self._prompt_text}")
            else:
                lines.append(f"  {self._prompt_text}")
            
            # Add current value display (if any)
            if self._current_value:
                if self._component_type == "password":
                    lines.append(f"  {'*' * len(str(self._current_value))}")
                elif self._component_type == "confirm":
                    lines.append(f"  {'Yes' if self._current_value else 'No'}")
                else:
                    lines.append(f"  {self._current_value}")
            else:
                if self._component_type == "confirm":
                    lines.append(f"  [Yes/No]")
                else:
                    lines.append(f"  [Enter {self._component_type}]")
            
            return lines
        
        # Fallback for unknown components
        else:
            return [f"[{self._component_type.upper()}: {self._name}]"]
    
    def has_changes(self) -> bool:
        """Check if this component needs re-rendering."""
        return self._needs_render
    
    def render_delta(self, relative_start: int = 0) -> int:
        """Render this component's changes at relative position."""
        if not self._visible:
            return 0
        
        current_lines = self.get_render_lines()
        
        # Clear previous content if different
        if self._last_rendered_lines != current_lines:
            # Clear old lines
            for i in range(len(self._last_rendered_lines)):
                line_pos = relative_start + i
                print(f"\\x1b[{line_pos + 1};1H\\x1b[2K", end="")
            
            # Render new content
            for i, line in enumerate(current_lines):
                line_pos = relative_start + i
                print(f"\\x1b[{line_pos + 1};1H{line}", end="")
            
            self._last_rendered_lines = current_lines.copy()
        
        self._needs_render = False
        return len(current_lines)

    def mark_dirty(self) -> None:
        """Mark this component as needing re-render."""
        self._needs_render = True

    # =================================================================
    # INTERACTIVE COMPONENT METHODS
    # =================================================================
    
    def activate_for_input(self, buffer_position: int) -> None:
        """Activate this component for interactive input at the given buffer position."""
        self._is_active = True
        self._prompt_position = buffer_position
        self.mark_dirty()
        try:
            _set_active_interactive_component(self)
        except Exception:
            pass
        
        # Fire change event to notify parent containers
        self.fire_change_event("state", metadata={"activated": True, "position": buffer_position})
    
    def deactivate(self) -> None:
        """Deactivate this component."""
        self._is_active = False
        self.mark_dirty()
        
        # Fire change event
        self.fire_change_event("state", metadata={"activated": False})
        try:
            _clear_active_interactive_component()
        except Exception:
            pass
    
    def set_value(self, value: Any) -> None:
        """Set the current value of this component."""
        old_value = self._current_value
        self._current_value = value
        
        if old_value != value:
            self.mark_dirty()
            self.fire_change_event("content", metadata={"old_value": old_value, "new_value": value})
    
    def get_value(self) -> Any:
        """Get the current value of this component."""
        return self._current_value
    
    def render_interactive_prompt(self) -> Any:
        """
        Render the actual interactive prompt using questionary.
        
        This method should be called by the form navigation system
        when this component is active.
        """
        if not self.is_interactive() or not self._is_active:
            return self._current_value
        
        # Import questionary here to avoid circular dependencies
        try:
            import questionary
            
            # Create the appropriate questionary prompt
            if self._component_type == "text":
                prompt = questionary.text(
                    message=self._prompt_text,
                    default=str(self._current_value) if self._current_value else ""
                )
            elif self._component_type == "password":
                prompt = questionary.password(
                    message=self._prompt_text
                )
            elif self._component_type == "confirm":
                prompt = questionary.confirm(
                    message=self._prompt_text,
                    default=bool(self._current_value) if self._current_value else True
                )
            elif self._component_type == "select":
                choices = self.config.get("choices", [])
                prompt = questionary.select(
                    message=self._prompt_text,
                    choices=choices,
                    default=self._current_value if self._current_value in choices else None
                )
            else:
                # Fallback to text input
                prompt = questionary.text(
                    message=self._prompt_text,
                    default=str(self._current_value) if self._current_value else ""
                )
            
            # Execute the prompt and update value
            # Wrap stdout/stderr to capture any ANSI sequences prompts may emit
            orig_stdout = sys.stdout
            orig_stderr = sys.stderr
            proxy_out = _AnsiStreamProxy(orig_stdout, 'stdout')
            proxy_err = _AnsiStreamProxy(orig_stderr, 'stderr')
            sys.stdout = proxy_out
            sys.stderr = proxy_err
            try:
                result = prompt.ask()
            finally:
                # Restore original streams
                sys.stdout = orig_stdout
                sys.stderr = orig_stderr
                # If we captured anything, emit debug info
                try:
                    if _prompt_clear_events and is_debug_mode():
                        for ev in _prompt_clear_events[-5:]:
                            print(f"DEBUG: Prompt injected ANSI on {ev['stream']}: {ev['matches']}")
                except Exception:
                    pass
            if is_debug_mode():
                try:
                    print(f"DEBUG: after prompt.ask(), result={repr(result)}")
                except Exception:
                    pass
            # After the prompt completes, if there's a recorded prompt-clear
            # timestamp, propagate it to the owning page (if any) so the page
            # can decide whether to reassert its content.
            try:
                from .component_wrappers import get_last_prompt_clear_ts
                last_ts = get_last_prompt_clear_ts()
                if last_ts:
                    # Walk up parent pointers to find owning PageBase
                    owning = None
                    try:
                        parent = getattr(self, '_parent', None)
                        while parent is not None:
                            # Prefer duck-typing: if parent exposes mark_prompt_cleared,
                            # treat it as the owning page. This avoids import/time issues.
                            if hasattr(parent, 'mark_prompt_cleared'):
                                owning = parent
                                break
                            if is_debug_mode():
                                try:
                                    print(f"DEBUG: traversing parent {type(parent)}")
                                except Exception:
                                    pass
                            parent = getattr(parent, '_parent', None)
                    except Exception:
                        owning = None

                    if owning is not None:
                        try:
                            owning.mark_prompt_cleared(last_ts)
                            # Immediately request a refresh so the page reasserts
                            # its content after the prompt returns. This covers
                            # cases where the prompt wrote directly to the TTY
                            # and the spatial delta would otherwise be empty.
                            try:
                                owning.refresh()
                            except Exception:
                                pass
                        except Exception:
                            pass
            except Exception:
                pass
            if result is not None:
                self.set_value(result)
            
            return result
            
        except ImportError:
            # Fallback if questionary not available
            print(f"{self._prompt_text} ", end="")
            result = input()
            self.set_value(result)
            # Propagate prompt-clear timestamp to owning page as above
            try:
                from .component_wrappers import get_last_prompt_clear_ts
                last_ts = get_last_prompt_clear_ts()
                if last_ts:
                    owning = None
                    try:
                        parent = getattr(self, '_parent', None)
                        while parent is not None:
                            if hasattr(parent, 'mark_prompt_cleared'):
                                owning = parent
                                break
                            parent = getattr(parent, '_parent', None)
                    except Exception:
                        owning = None

                    if owning is not None:
                        try:
                            owning.mark_prompt_cleared(last_ts)
                            try:
                                owning.refresh()
                            except Exception:
                                pass
                        except Exception:
                            pass
            except Exception:
                pass
            return result    # CardChildInterface and AssemblyChildInterface implementation
    def is_completed(self) -> bool:
        """Whether this component has completed its required input/validation."""
        # Display components are always completed
        if not self.is_interactive():
            return True
        
        # For interactive components, check if they have a value
        # This is a simplified implementation
        return True  # For now, assume all are completed
    
    def is_valid(self) -> bool:
        """Whether this component's current state is valid."""
        # Run all validators if any
        if not self.validators:
            return True
        
        # For now, assume valid (would need actual value to validate)
        return True

    def add_validator(self, validator: Callable[..., Any]) -> None:
        """Add a validator function."""
        self.validators.append(validator)

    def is_visible(self, state: Dict[str, Any]) -> bool:
        """Check if component should be visible based on 'when' condition."""
        # Direct visibility check (no dynamic attribute access needed)
        if not self._visible:
            return False

        if not self.when_condition:
            return True

        # TODO: implement expression evaluation of `when` conditions safely
        # For now, default to visible to avoid accidental hiding while the
        # expression evaluator is implemented.
        return True

    def create_questionary_component(self) -> Any:
        """Create the underlying questionary component."""
        
        # Handle display-only components separately
        if self.component_type in ["text_display", "text_section", "text_status"]:
            # These are display-only components, not questionary prompts
            return self
        
        # Use DI system for clean, fast, testable resolution
        from src.tui_engine.questionary_factory import get_questionary
        questionary_module = get_questionary()
        
        if questionary_module is None:
            raise ImportError("questionary is not available")
        
        # Validate supported component types early
        supported = {
            "text", "select", "confirm", "password", 
            "checkbox", "autocomplete", "path"
        }
        if self.component_type not in supported:
            raise ValueError(f"Unsupported component type: {self.component_type}")
        
        # Get component factory from DI-resolved questionary module
        if not hasattr(questionary_module, self.component_type):
            raise ValueError(f"Questionary module missing component type: {self.component_type}")
            
        component_func = getattr(questionary_module, self.component_type)
        if not callable(component_func):
            raise ValueError(f"Component type {self.component_type} is not callable")

        try:
            # Use questionary_config which excludes non-questionary options
            return component_func(**self.questionary_config)
        except Exception as exc:
            # Handle console availability issues in CI/headless environments
            if (
                hasattr(exc, "__class__")
                and exc.__class__.__name__ == "NoConsoleScreenBufferError"
            ):
                raise RuntimeError("No console available for questionary") from exc
            raise


# Convenience wrapper functions matching questionary API
def text_prompt(name: str, message: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a text input component that prompts user for text input."""
    if message is None:
        message = f"{name.replace('_', ' ').title()}:"
    return Component(name, "text", message=message, **kwargs)


def text_display(content: str, name: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a display-only text component (like print() but page-controlled)."""
    if name is None:
        name = f"display_{uuid.uuid4().hex[:8]}"  # Generate truly unique name
    return Component(name, "text_display", content=content, **kwargs)


def text_section(content: str, title: Optional[str] = None, name: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a multi-line text block component."""
    if name is None:
        name = f"section_{uuid.uuid4().hex[:8]}"
    return Component(name, "text_section", content=content, title=title, **kwargs)


def text_status(content: str, status_type: str = "info", name: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a status/progress message component."""
    if name is None:
        name = f"status_{uuid.uuid4().hex[:8]}"
    return Component(name, "text_status", content=content, status_type=status_type, **kwargs)


def select_prompt(
    name: str,
    message: Optional[str] = None,
    choices: Optional[List[str]] = None,
    **kwargs: Any,
) -> Component:
    """Create a selection component that prompts user to choose from options."""
    if message is None:
        message = f"Choose {name.replace('_', ' ')}:"
    if choices is None:
        choices = []
    return Component(name, "select", message=message, choices=choices, **kwargs)


def confirm_prompt(name: str, message: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a confirmation component that prompts user for yes/no."""
    if message is None:
        message = f"Confirm {name.replace('_', ' ')}?"
    return Component(name, "confirm", message=message, **kwargs)


def password_prompt(name: str, message: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a password input component that prompts user for secure text."""
    if message is None:
        message = f"{name.replace('_', ' ').title()}:"
    return Component(name, "password", message=message, **kwargs)


def checkbox_prompt(
    name: str,
    message: Optional[str] = None,
    choices: Optional[List[str]] = None,
    **kwargs: Any,
) -> Component:
    """Create a checkbox component that prompts user for multiple selections."""
    if message is None:
        message = f"Select {name.replace('_', ' ')}:"
    if choices is None:
        choices = []
    return Component(name, "checkbox", message=message, choices=choices, **kwargs)


def autocomplete_prompt(
    name: str,
    message: Optional[str] = None,
    choices: Optional[List[str]] = None,
    **kwargs: Any,
) -> Component:
    """Create an autocomplete component that prompts user with suggested options."""
    if message is None:
        message = f"Choose {name.replace('_', ' ')}:"
    if choices is None:
        choices = []
    return Component(name, "autocomplete", message=message, choices=choices, **kwargs)


def path_prompt(name: str, message: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a path selection component that prompts user for file/directory path."""
    if message is None:
        message = f"{name.replace('_', ' ').title()}:"
    return Component(name, "path", message=message, **kwargs)


__all__ = [
    "Component",
    # Interactive prompt components (require user input)
    "text_prompt",
    "select_prompt", 
    "confirm_prompt",
    "password_prompt",
    "checkbox_prompt",
    "autocomplete_prompt",
    "path_prompt",
    # Display components (show information only)
    "text_display",
    "text_section",
    "text_status",
]

# Internal collector for prompt-injected ANSI sequences (e.g., clears, alternate-screen)
_prompt_clear_events: List[Dict[str, Any]] = []

# Timestamp (float epoch) of the most recent prompt-injected clear event.
# Updated by the _AnsiStreamProxy when it detects matching sequences.
_last_prompt_clear_ts: float = 0.0


def get_prompt_clear_events() -> List[Dict[str, Any]]:
    """Return a copy of captured prompt clear events.

    Each event is a dict with keys: timestamp, stream ('stdout'/'stderr'), and matches (list of matched ANSI fragments).
    """
    return list(_prompt_clear_events)


# Active interactive component (set when a component is activated for input)
_active_interactive_component = None


def _set_active_interactive_component(comp: Any) -> None:
    global _active_interactive_component
    _active_interactive_component = comp


def _clear_active_interactive_component() -> None:
    global _active_interactive_component
    _active_interactive_component = None



def get_last_prompt_clear_ts() -> float:
    """Return the epoch timestamp of the last captured prompt clear (0.0 if none)."""
    return float(_last_prompt_clear_ts)


def set_last_prompt_clear_ts(ts: float) -> None:
    """Set the last prompt clear timestamp (used by tests or external triggers)."""
    global _last_prompt_clear_ts
    try:
        _last_prompt_clear_ts = float(ts)
    except Exception:
        _last_prompt_clear_ts = time.time()


class _AnsiStreamProxy:
    """Proxy for stdout/stderr that records ANSI clear-like sequences while forwarding writes.

    This is intentionally lightweight: it forwards all calls to the underlying
    stream so prompt-toolkit/questionary behaviour is preserved, while also
    scanning for common clear/alternate-screen ANSI sequences and recording
    them for diagnostics.
    """
    _ansi_re = re.compile(r"\x1b\[[\d;?]*[A-Za-z]")

    def __init__(self, stream, which: str):
        self._stream = stream
        self._which = which

    def write(self, data):
        try:
            if data and isinstance(data, str):
                # Look for ANSI CSI sequences that commonly clear or switch screen
                matches = [m.group(0) for m in self._ansi_re.finditer(data)]
                filtered = [m for m in matches if any(tok in m for tok in ['2J', 'H', 'K', '?1049'])]
                if filtered:
                    ev = {
                        'timestamp': time.time(),
                        'stream': self._which,
                        'matches': filtered,
                        'sample': data[:200]
                    }
                    _prompt_clear_events.append(ev)
                    # Update last prompt clear timestamp for consumers
                    try:
                        global _last_prompt_clear_ts
                        _last_prompt_clear_ts = ev['timestamp']
                    except Exception:
                        pass
                    # If there's an active interactive component, attempt to
                    # attribute this clear to its owning page immediately so
                    # the page can respond without waiting for the prompt
                    # to finish.
                    try:
                        global _active_interactive_component
                        comp = _active_interactive_component
                        if comp is not None:
                            parent = getattr(comp, '_parent', None)
                            while parent is not None:
                                if hasattr(parent, 'mark_prompt_cleared'):
                                    try:
                                        parent.mark_prompt_cleared(ev['timestamp'])
                                    except Exception:
                                        pass
                                    break
                                parent = getattr(parent, '_parent', None)
                    except Exception:
                        pass
        except Exception:
            # Be conservative: never raise from the proxy
            pass

        return self._stream.write(data)

    def flush(self):
        try:
            return self._stream.flush()
        except Exception:
            return None

    def isatty(self):
        try:
            return self._stream.isatty()
        except Exception:
            return False

    # Provide attributes commonly accessed by prompt-toolkit
    def __getattr__(self, name):
        return getattr(self._stream, name)

