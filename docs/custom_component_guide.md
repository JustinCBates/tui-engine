# Custom Component Creation Guide for TUI Engine

## Overview

This guide demonstrates how to create custom components in TUI Engine that leverage both prompt-toolkit primitives and Questionary styling for maximum flexibility and professional appearance.

## Component Architecture Layers

TUI Engine provides multiple layers for component creation, from simple to highly customized:

```
Layer 4: Composite Components (Multi-widget assemblies)
    ↓
Layer 3: Hybrid Components (Questionary + Custom prompt-toolkit)  
    ↓
Layer 2: Questionary-Wrapped Components (Standard inputs with styling)
    ↓
Layer 1: Pure Prompt-Toolkit Components (Maximum customization)
    ↓
Base: ComponentBase (TUI Engine foundation)
```

## Layer 1: Pure Prompt-Toolkit Components

For maximum control and customization, create components directly using prompt-toolkit primitives.

### Example: Custom Gauge Component

```python
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from tui_engine.custom_component_base import CustomComponentBase

class GaugeComponent(CustomComponentBase):
    """A custom gauge/meter component with prompt-toolkit primitives."""
    
    def __init__(self, name: str, min_val: float = 0, max_val: float = 100, 
                 current_val: float = 0, width: int = 30):
        super().__init__(name, "gauge")
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = current_val
        self.width = width
        
    def to_prompt_toolkit(self) -> Window:
        """Create gauge using pure prompt-toolkit."""
        
        def get_gauge_text():
            # Calculate gauge fill
            if self.max_val == self.min_val:
                progress = 0
            else:
                progress = (self.current_val - self.min_val) / (self.max_val - self.min_val)
                progress = max(0, min(1, progress))  # Clamp to 0-1
            
            filled_width = int(progress * self.width)
            empty_width = self.width - filled_width
            
            # Create gauge bar
            gauge_bar = '█' * filled_width + '░' * empty_width
            
            # Apply styling if available
            if self.questionary_style:
                return [
                    ('class:question', f'{self.name}: '),
                    ('class:answer', f'{self.current_val:.1f}'),
                    ('class:text', f' [{gauge_bar}] '),
                    ('class:instruction', f'({self.min_val}-{self.max_val})')
                ]
            else:
                return f'{self.name}: {self.current_val:.1f} [{gauge_bar}] ({self.min_val}-{self.max_val})'
        
        # Create interactive key bindings
        kb = KeyBindings()
        
        @kb.add('plus')
        @kb.add('=')
        def increase(event):
            step = (self.max_val - self.min_val) / 20  # 5% steps
            self.current_val = min(self.max_val, self.current_val + step)
            event.app.invalidate()
        
        @kb.add('minus')
        @kb.add('_')
        def decrease(event):
            step = (self.max_val - self.min_val) / 20
            self.current_val = max(self.min_val, self.current_val - step)
            event.app.invalidate()
            
        # Create the control
        control = FormattedTextControl(
            text=get_gauge_text,
            key_bindings=kb,
            focusable=True
        )
        
        return Window(content=control, height=1)
    
    def get_value(self) -> float:
        """Get current gauge value."""
        return self.current_val
    
    def set_value(self, value: float):
        """Set gauge value."""
        self.current_val = max(self.min_val, min(self.max_val, value))
```

### Example: Custom Tree View Component

```python
class TreeViewComponent(CustomComponentBase):
    """A tree view component for hierarchical data."""
    
    def __init__(self, name: str, tree_data: dict):
        super().__init__(name, "tree_view")
        self.tree_data = tree_data
        self.expanded_nodes = set()
        self.selected_path = []
        self.scroll_offset = 0
        
    def to_prompt_toolkit(self) -> Window:
        """Create tree view using prompt-toolkit."""
        
        def get_tree_text():
            lines = []
            self._render_tree_node(self.tree_data, lines, [], 0)
            
            # Apply scroll offset
            visible_lines = lines[self.scroll_offset:self.scroll_offset + 10]
            return visible_lines
        
        def _render_tree_node(self, node, lines, path, depth):
            """Recursively render tree nodes."""
            indent = "  " * depth
            
            if isinstance(node, dict):
                for key, value in node.items():
                    current_path = path + [key]
                    is_selected = current_path == self.selected_path
                    is_expanded = tuple(current_path) in self.expanded_nodes
                    
                    # Node symbol
                    if isinstance(value, dict):
                        symbol = "📂" if is_expanded else "📁"
                    else:
                        symbol = "📄"
                    
                    # Apply styling
                    if self.questionary_style:
                        style_class = 'highlighted' if is_selected else 'text'
                        lines.append([(f'class:{style_class}', f'{indent}{symbol} {key}')])
                    else:
                        prefix = "> " if is_selected else "  "
                        lines.append(f'{prefix}{indent}{symbol} {key}')
                    
                    # Render children if expanded
                    if is_expanded and isinstance(value, dict):
                        self._render_tree_node(value, lines, current_path, depth + 1)
        
        # Navigation key bindings
        kb = KeyBindings()
        
        @kb.add('up')
        def _(event):
            self._navigate_up()
            event.app.invalidate()
            
        @kb.add('down')
        def _(event):
            self._navigate_down()
            event.app.invalidate()
            
        @kb.add('right')
        @kb.add('enter')
        def _(event):
            self._expand_current()
            event.app.invalidate()
            
        @kb.add('left')
        def _(event):
            self._collapse_current()
            event.app.invalidate()
        
        control = FormattedTextControl(
            text=get_tree_text,
            key_bindings=kb,
            focusable=True
        )
        
        return Window(content=control, height=12)
    
    def _navigate_up(self):
        """Navigate to previous item."""
        # Implementation for tree navigation
        pass
        
    def _navigate_down(self):
        """Navigate to next item."""
        # Implementation for tree navigation
        pass
        
    def _expand_current(self):
        """Expand current node."""
        if self.selected_path:
            self.expanded_nodes.add(tuple(self.selected_path))
            
    def _collapse_current(self):
        """Collapse current node."""
        if self.selected_path:
            path_tuple = tuple(self.selected_path)
            if path_tuple in self.expanded_nodes:
                self.expanded_nodes.remove(path_tuple)
```

## Layer 2: Questionary-Wrapped Components

Use Questionary's built-in components within TUI Engine layouts for professional, standardized inputs.

### Example: Enhanced Select Component

```python
import questionary
from tui_engine.custom_component_base import CustomComponentBase

class EnhancedSelectComponent(CustomComponentBase):
    """Select component using Questionary's select with TUI Engine integration."""
    
    def __init__(self, name: str, choices: list, message: str = None, 
                 default: str = None, instruction: str = None):
        super().__init__(name, "enhanced_select")
        self.choices = choices
        self.message = message or f"Select {name}:"
        self.default = default
        self.instruction = instruction
        self.selected_value = default
        
    def to_prompt_toolkit(self):
        """Create select using Questionary."""
        
        # Create Questionary select prompt
        select_prompt = questionary.select(
            message=self.message,
            choices=self.choices,
            default=self.default,
            instruction=self.instruction,
            style=self.questionary_style
        )
        
        # Extract the prompt-toolkit layout from Questionary
        # This gives us the fully-styled, interactive select component
        return select_prompt._get_prompt_session().layout.container
        
    def get_value(self):
        """Get selected value."""
        return self.selected_value
        
    def set_choices(self, new_choices: list):
        """Update available choices."""
        self.choices = new_choices
        # Trigger re-render
        return self
```

### Example: Autocomplete Input Component

```python
class AutocompleteInputComponent(CustomComponentBase):
    """Text input with autocomplete using Questionary."""
    
    def __init__(self, name: str, completions: list, message: str = None):
        super().__init__(name, "autocomplete_input")
        self.completions = completions
        self.message = message or f"Enter {name}:"
        self.current_value = ""
        
    def to_prompt_toolkit(self):
        """Create autocomplete input using Questionary."""
        from questionary import autocomplete
        
        autocomplete_prompt = autocomplete(
            message=self.message,
            choices=self.completions,
            style=self.questionary_style,
            validate=self._validate_input
        )
        
        return autocomplete_prompt._get_prompt_session().layout.container
        
    def _validate_input(self, text):
        """Custom validation for autocomplete input."""
        # Add custom validation logic
        if len(text) < 2:
            return False
        return True
```

## Layer 3: Hybrid Components

Combine Questionary components with custom prompt-toolkit widgets for complex, professional interfaces.

### Example: Form Field with Custom Validation Display

```python
from prompt_toolkit.layout import HSplit, VSplit
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl

class ValidatedFormFieldComponent(CustomComponentBase):
    """Hybrid component: Questionary input + custom validation display."""
    
    def __init__(self, name: str, field_type: str = "text", validators: list = None):
        super().__init__(name, "validated_form_field")
        self.field_type = field_type
        self.validators = validators or []
        self.current_value = ""
        self.validation_errors = []
        
    def to_prompt_toolkit(self):
        """Create hybrid layout with Questionary input + custom validation."""
        
        # Create Questionary input component
        if self.field_type == "text":
            input_prompt = questionary.text(
                message=f"{self.name}:",
                style=self.questionary_style
            )
        elif self.field_type == "password":
            input_prompt = questionary.password(
                message=f"{self.name}:",
                style=self.questionary_style
            )
        # Add other field types as needed
        
        input_widget = input_prompt._get_prompt_session().layout.container
        
        # Create custom validation display
        def get_validation_text():
            if not self.validation_errors:
                return []
            
            error_lines = []
            for error in self.validation_errors:
                if self.questionary_style:
                    error_lines.append([('class:error', f"  ⚠ {error}")])
                else:
                    error_lines.append(f"  ⚠ {error}")
            return error_lines
        
        validation_widget = Window(
            content=FormattedTextControl(text=get_validation_text),
            height=lambda: len(self.validation_errors)
        )
        
        # Combine in vertical layout
        return HSplit([
            input_widget,
            validation_widget
        ])
        
    def validate(self, value: str):
        """Run validation and update error display."""
        self.validation_errors = []
        for validator in self.validators:
            error = validator(value)
            if error:
                self.validation_errors.append(error)
        
        # Trigger re-render to show/hide errors
        return len(self.validation_errors) == 0
```

### Example: Dashboard Widget with Multiple Components

```python
class DashboardWidgetComponent(CustomComponentBase):
    """Complex hybrid component combining multiple UI elements."""
    
    def __init__(self, name: str, title: str, data_source: callable):
        super().__init__(name, "dashboard_widget")
        self.title = title
        self.data_source = data_source
        self.refresh_interval = 5  # seconds
        self.show_details = False
        
    def to_prompt_toolkit(self):
        """Create dashboard widget with multiple sub-components."""
        from prompt_toolkit.layout import HSplit, VSplit
        
        # Title bar with custom styling
        title_widget = Window(
            content=FormattedTextControl(
                text=self._get_title_text
            ),
            height=1
        )
        
        # Main data display (custom gauge or chart)
        gauge = GaugeComponent(
            name="Progress", 
            current_val=self._get_current_value(),
            max_val=100
        )
        data_widget = gauge.to_prompt_toolkit()
        
        # Control buttons using Questionary
        control_prompt = questionary.select(
            message="Action:",
            choices=["Refresh", "Details", "Settings"],
            style=self.questionary_style
        )
        control_widget = control_prompt._get_prompt_session().layout.container
        
        # Status indicator (custom)
        status_widget = Window(
            content=FormattedTextControl(text=self._get_status_text),
            height=1
        )
        
        # Combine all widgets
        return HSplit([
            title_widget,
            VSplit([data_widget, control_widget]),
            status_widget
        ])
        
    def _get_title_text(self):
        """Generate styled title text."""
        if self.questionary_style:
            return [('class:container_title', f"📊 {self.title}")]
        else:
            return f"📊 {self.title}"
            
    def _get_current_value(self):
        """Get current data value."""
        return self.data_source() if self.data_source else 0
        
    def _get_status_text(self):
        """Generate status indicator."""
        status = "🟢 Online" if self._is_healthy() else "🔴 Error"
        if self.questionary_style:
            style_class = 'success' if self._is_healthy() else 'error'
            return [(f'class:{style_class}', status)]
        else:
            return status
            
    def _is_healthy(self):
        """Check if data source is healthy."""
        try:
            self.data_source()
            return True
        except:
            return False
```

## Layer 4: Composite Components

Build complex assemblies from multiple components for sophisticated interfaces.

### Example: File Browser Component

```python
class FileBrowserComponent(CustomComponentBase):
    """Composite file browser with tree view, preview, and actions."""
    
    def __init__(self, name: str, root_path: str = "."):
        super().__init__(name, "file_browser")
        self.root_path = root_path
        self.current_path = root_path
        
        # Sub-components
        self.tree_view = TreeViewComponent("file_tree", self._build_file_tree())
        self.preview_panel = TextPreviewComponent("preview")
        self.action_panel = self._create_action_panel()
        
    def to_prompt_toolkit(self):
        """Create composite file browser layout."""
        from prompt_toolkit.layout import HSplit, VSplit
        
        # Main layout: tree view | preview panel
        main_panel = VSplit([
            self.tree_view.to_prompt_toolkit(),
            Window(width=1, char='│'),  # Separator
            self.preview_panel.to_prompt_toolkit()
        ])
        
        # Bottom action panel
        action_panel = self.action_panel.to_prompt_toolkit()
        
        # Status bar
        status_bar = Window(
            content=FormattedTextControl(text=self._get_status_text),
            height=1
        )
        
        return HSplit([
            main_panel,
            Window(height=1, char='─'),  # Separator
            action_panel,
            status_bar
        ])
        
    def _build_file_tree(self):
        """Build file tree structure."""
        import os
        tree = {}
        # Build tree structure from filesystem
        return tree
        
    def _create_action_panel(self):
        """Create action buttons panel."""
        return questionary.select(
            message="Action:",
            choices=["Open", "Copy", "Move", "Delete", "Rename"],
            style=self.questionary_style
        )
        
    def _get_status_text(self):
        """Generate status bar text."""
        return f"Path: {self.current_path} | Selected: {self.tree_view.get_selected()}"

class TextPreviewComponent(CustomComponentBase):
    """Text file preview component."""
    
    def __init__(self, name: str):
        super().__init__(name, "text_preview")
        self.content = ""
        
    def to_prompt_toolkit(self):
        """Create text preview window."""
        from prompt_toolkit.widgets import TextArea
        
        text_area = TextArea(
            text=self.content,
            read_only=True,
            multiline=True,
            wrap_lines=True
        )
        
        return text_area
        
    def set_content(self, content: str):
        """Update preview content."""
        self.content = content
```

## Best Practices for Custom Components

### 1. Component Naming and Organization

```python
# Good: Clear, descriptive names
class DatabaseTableBrowserComponent(CustomComponentBase):
    pass

class ChartVisualizationComponent(CustomComponentBase):
    pass

# Organize by functionality
# src/tui_engine/components/
#   ├── data/
#   │   ├── table_browser.py
#   │   └── chart_visualization.py
#   ├── input/
#   │   ├── date_picker.py
#   │   └── autocomplete_input.py
#   └── layout/
#       ├── dashboard_widget.py
#       └── tabbed_container.py
```

### 2. State Management

```python
class StatefulComponent(CustomComponentBase):
    """Example of proper state management in custom components."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self._state = {
            'value': None,
            'is_focused': False,
            'is_dirty': False,
            'validation_errors': []
        }
        
    def get_state(self) -> dict:
        """Get current component state."""
        return self._state.copy()
        
    def set_state(self, new_state: dict):
        """Update component state."""
        self._state.update(new_state)
        self._mark_dirty()
        
    def _mark_dirty(self):
        """Mark component for re-render."""
        self._state['is_dirty'] = True
        # Trigger app invalidation if needed
```

### 3. Event Handling

```python
class EventHandlingComponent(CustomComponentBase):
    """Example of event handling in custom components."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.event_handlers = {}
        
    def on(self, event_name: str, handler: callable):
        """Register event handler."""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)
        
    def emit(self, event_name: str, *args, **kwargs):
        """Emit event to all registered handlers."""
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                handler(self, *args, **kwargs)
                
    def to_prompt_toolkit(self):
        """Example with event emission."""
        kb = KeyBindings()
        
        @kb.add('enter')
        def _(event):
            self.emit('value_selected', self.get_value())
            
        # ... rest of implementation
```

### 4. Testing Custom Components

```python
# tests/test_custom_components.py
import pytest
from unittest.mock import Mock
from your_app.components import GaugeComponent

class TestGaugeComponent:
    def test_gauge_creation(self):
        """Test basic gauge component creation."""
        gauge = GaugeComponent("test_gauge", min_val=0, max_val=100, current_val=50)
        assert gauge.name == "test_gauge"
        assert gauge.current_val == 50
        
    def test_gauge_value_clamping(self):
        """Test that gauge values are properly clamped."""
        gauge = GaugeComponent("test", 0, 100, 150)  # Over max
        gauge.set_value(150)
        assert gauge.get_value() <= 100
        
    def test_gauge_prompt_toolkit_integration(self):
        """Test that gauge creates valid prompt-toolkit widgets."""
        gauge = GaugeComponent("test", 0, 100, 50)
        widget = gauge.to_prompt_toolkit()
        
        # Verify it's a valid prompt-toolkit component
        from prompt_toolkit.layout.containers import Window
        assert isinstance(widget, Window)
        
    def test_gauge_with_questionary_styling(self):
        """Test gauge with Questionary styling applied."""
        from questionary import Style
        
        style = Style([('class:answer', 'fg:#00ff00')])
        gauge = GaugeComponent("test", 0, 100, 50)
        gauge.set_questionary_style(style)
        
        # Test that styling is applied
        assert gauge.questionary_style == style
```

## Performance Considerations

### 1. Efficient Rendering

```python
class OptimizedComponent(CustomComponentBase):
    """Example of performance-optimized component."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self._cached_content = None
        self._last_render_time = None
        self._render_interval = 0.1  # Minimum time between renders
        
    def to_prompt_toolkit(self):
        """Optimized rendering with caching."""
        import time
        
        current_time = time.time()
        
        # Only re-render if enough time has passed
        if (self._last_render_time is None or 
            current_time - self._last_render_time > self._render_interval):
            
            self._cached_content = self._render_content()
            self._last_render_time = current_time
            
        return self._cached_content
        
    def _render_content(self):
        """Actual rendering implementation."""
        # Expensive rendering logic here
        pass
```

### 2. Memory Management

```python
class MemoryEfficientComponent(CustomComponentBase):
    """Example of memory-efficient component."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self._observers = []  # Weak references to avoid memory leaks
        
    def add_observer(self, observer):
        """Add observer with weak reference."""
        import weakref
        self._observers.append(weakref.ref(observer))
        
    def notify_observers(self, event_data):
        """Notify observers, cleaning up dead references."""
        alive_observers = []
        for observer_ref in self._observers:
            observer = observer_ref()
            if observer is not None:
                observer.handle_event(event_data)
                alive_observers.append(observer_ref)
        self._observers = alive_observers
```

## Integration Examples

### Using Custom Components in TUI Engine Applications

```python
# Example: Using custom components in a TUI Engine app
from tui_engine import App, Page, Container
from your_components import GaugeComponent, FileBrowserComponent, DashboardWidgetComponent

def create_monitoring_dashboard():
    """Create a monitoring dashboard with custom components."""
    
    app = App()
    page = Page("System Monitor")
    
    # Create main container
    main_container = Container("dashboard")
    main_container.set_layout_direction("horizontal")
    
    # Add custom gauge components
    cpu_gauge = GaugeComponent("CPU Usage", 0, 100, 75)
    memory_gauge = GaugeComponent("Memory", 0, 16, 8.5)  # GB
    disk_gauge = GaugeComponent("Disk Space", 0, 1000, 750)  # GB
    
    # Add custom dashboard widget
    system_widget = DashboardWidgetComponent(
        "system_status", 
        "System Status",
        lambda: get_system_metrics()
    )
    
    # Add custom file browser
    log_browser = FileBrowserComponent("logs", "/var/log")
    
    # Create layout with custom components
    left_panel = Container("metrics")
    left_panel.add(cpu_gauge)
    left_panel.add(memory_gauge) 
    left_panel.add(disk_gauge)
    left_panel.add(system_widget)
    
    right_panel = Container("files")
    right_panel.add(log_browser)
    
    main_container.add(left_panel)
    main_container.add(right_panel)
    
    page.body_section.add(main_container)
    app.add_page("monitor", page)
    
    # Apply Questionary styling to all components
    from tui_engine.themes import TUIEngineThemes
    app.set_style(TUIEngineThemes.PROFESSIONAL_BLUE)
    
    return app

def get_system_metrics():
    """Mock function to get system metrics."""
    import random
    return random.randint(0, 100)

# Run the application
if __name__ == "__main__":
    app = create_monitoring_dashboard()
    app.run()
```

## Conclusion

TUI Engine's custom component framework provides unlimited flexibility for creating sophisticated terminal user interfaces. By combining the power of prompt-toolkit primitives with Questionary's styling system, you can create professional, interactive components for any use case.

Key benefits:
- **Full control**: Direct access to prompt-toolkit widgets and controls
- **Professional styling**: Questionary's comprehensive theme system
- **Easy integration**: Components work seamlessly within TUI Engine layouts
- **Scalable architecture**: From simple widgets to complex composite components
- **Best practices**: Established patterns for state management, events, and performance

Whether you need simple custom inputs or complex data visualization components, TUI Engine provides the foundation and flexibility to build exactly what your application requires.