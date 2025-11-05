# Questionary Integration Plan for TUI Engine

## Overview

This document outlines the plan to integrate Questionary into the TUI Engine project to enhance styling consistency, focus management, and input validation capabilities while preserving the superior multi-container layout architecture that TUI Engine provides.

**CRITICAL REQUIREMENT**: Maintain the ability to create new custom components using prompt-toolkit + Questionary integration.

## Current State Analysis

### TUI Engine Strengths
- **Multi-container layout system**: Superior to Questionary's single-question approach
- **Real-time navigation**: Dynamic container visibility switching
- **Component architecture**: Reusable, composable UI components  
- **State management**: Complex validation tracking and data collection
- **Multi-page support**: App class supports multiple pages
- **Layout rebuilding**: Dynamic prompt-toolkit layout updates
- **Custom component creation**: Ability to create new components using prompt-toolkit primitives

### Areas for Enhancement (from Questionary)
- **Validation system**: More sophisticated validation with cursor positioning
- **Styling consistency**: Comprehensive theme system with presets
- **Focus management**: Better handling of focus transitions and edge cases
- **Input types**: Specialized inputs (password, select, confirm, etc.)
- **Error display**: Professional validation error presentation

## Integration Strategy: Selective Enhancement with Custom Component Support

### Core Principle: Component Extension Framework

The integration must preserve and enhance the ability to create custom components by providing:

1. **Base component classes** that integrate Questionary features
2. **Prompt-toolkit primitive access** for advanced customization
3. **Questionary widget factories** for common patterns
4. **Hybrid component capabilities** mixing TUI Engine layouts with Questionary inputs

### Priority 1: Consistent Styling System (CRITICAL)
**Goal**: Replace current styling with Questionary's comprehensive theme system while supporting custom component styling.

**Implementation**:
```python
# src/tui_engine/themes.py
from questionary import Style
from prompt_toolkit.styles import Style as PTKStyle

class TUIEngineThemes:
    """Centralized theme management supporting both Questionary and custom components."""
    
    PROFESSIONAL_BLUE = Style([
        # Questionary base styles
        ('qmark', 'fg:#1e88e5 bold'),
        ('question', 'fg:#1976d2 bold'),
        ('answer', 'fg:#4caf50 bold'),
        ('pointer', 'fg:#1e88e5 bold'),
        ('highlighted', 'bg:#e3f2fd fg:#0d47a1 bold'),
        ('selected', 'fg:#1976d2'),
        ('separator', 'fg:#90caf9'),
        ('instruction', 'fg:#424242'),
        ('text', 'fg:#212121'),
        ('disabled', 'fg:#9e9e9e italic'),
        
        # TUI Engine extensions for custom components
        ('title', 'bg:#1e88e5 fg:#ffffff bold'),
        ('error', 'fg:#f44336 bold'),
        ('success', 'fg:#4caf50 bold'),
        ('warning', 'fg:#ff9800 bold'),
        ('info', 'fg:#2196f3 italic'),
        ('status', 'bg:#e3f2fd fg:#0d47a1 bold'),
        ('border', 'fg:#90caf9'),
        ('container_title', 'fg:#1976d2 bold'),
        
        # Custom component style classes
        ('custom.widget', 'fg:#424242'),
        ('custom.widget.focused', 'bg:#e3f2fd fg:#0d47a1 bold'),
        ('custom.widget.disabled', 'fg:#9e9e9e italic'),
        ('custom.widget.error', 'fg:#f44336 bold'),
        ('custom.widget.success', 'fg:#4caf50 bold'),
    ])
    
    @classmethod
    def get_questionary_style(cls, theme_name: str) -> Style:
        """Get Questionary Style object."""
        return getattr(cls, theme_name.upper(), cls.PROFESSIONAL_BLUE)
    
    @classmethod
    def get_prompt_toolkit_style(cls, theme_name: str) -> PTKStyle:
        """Get prompt-toolkit Style object for custom components."""
        questionary_style = cls.get_questionary_style(theme_name)
        # Convert Questionary Style to prompt-toolkit Style
        return PTKStyle(questionary_style.style)
    
    @classmethod
    def extend_theme(cls, base_theme: str, custom_styles: list) -> Style:
        """Extend an existing theme with custom styles for new components."""
        base = cls.get_questionary_style(base_theme)
        extended_styles = base.style + custom_styles
        return Style(extended_styles)
```

### Priority 2: Custom Component Framework
**Goal**: Provide a framework for creating custom components that leverage both TUI Engine and Questionary capabilities.

**Implementation**:
```python
# src/tui_engine/custom_component_base.py
from typing import Any, Optional, Callable
from prompt_toolkit.widgets import TextArea, Button
from prompt_toolkit.layout.containers import Window, HSplit, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from questionary import PromptSession, Style
from .component_base import ComponentBase

class CustomComponentBase(ComponentBase):
    """
    Base class for creating custom components that integrate TUI Engine,
    prompt-toolkit, and Questionary capabilities.
    """
    
    def __init__(self, name: str, variant: str = "custom"):
        super().__init__(name, variant)
        self.questionary_session: Optional[PromptSession] = None
        self.prompt_toolkit_widgets: list = []
        self.questionary_style: Optional[Style] = None
        
    def set_questionary_style(self, style: Style):
        """Set Questionary style for this component."""
        self.questionary_style = style
        return self
        
    def create_questionary_session(self, **kwargs) -> PromptSession:
        """Create a Questionary session for this component."""
        self.questionary_session = PromptSession(
            style=self.questionary_style,
            **kwargs
        )
        return self.questionary_session
        
    def add_prompt_toolkit_widget(self, widget: Any):
        """Add a raw prompt-toolkit widget to this component."""
        self.prompt_toolkit_widgets.append(widget)
        return self
        
    def create_hybrid_layout(self, questionary_widget: Any, ptk_widgets: list) -> Any:
        """Create a hybrid layout mixing Questionary and prompt-toolkit widgets."""
        from prompt_toolkit.layout import HSplit, VSplit
        
        # Combine Questionary widget with custom prompt-toolkit widgets
        if self.layout_direction == "horizontal":
            return HSplit([questionary_widget] + ptk_widgets)
        else:
            return VSplit([questionary_widget] + ptk_widgets)
    
    def to_prompt_toolkit(self) -> Any:
        """
        Convert to prompt-toolkit widget.
        Override this method to create custom component layouts.
        """
        raise NotImplementedError("Custom components must implement to_prompt_toolkit()")

# Example: Custom Slider Component
class SliderComponent(CustomComponentBase):
    """
    Custom slider component combining Questionary styling with 
    custom prompt-toolkit slider implementation.
    """
    
    def __init__(self, name: str, min_value: int = 0, max_value: int = 100, step: int = 1):
        super().__init__(name, "slider")
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.current_value = min_value
        
    def to_prompt_toolkit(self) -> Window:
        """Create custom slider using prompt-toolkit primitives."""
        from prompt_toolkit.layout.controls import FormattedTextControl
        from prompt_toolkit.layout.containers import Window
        from prompt_toolkit.key_binding import KeyBindings
        
        # Create slider display
        def get_slider_text():
            # Create visual slider representation
            total_steps = (self.max_value - self.min_value) // self.step
            current_step = (self.current_value - self.min_value) // self.step
            progress = current_step / total_steps if total_steps > 0 else 0
            
            # Create slider bar (20 characters wide)
            bar_width = 20
            filled = int(progress * bar_width)
            bar = '█' * filled + '░' * (bar_width - filled)
            
            # Apply Questionary styling
            if self.questionary_style:
                return [
                    ('class:question', f'{self.name}: '),
                    ('class:answer', f'{self.current_value}'),
                    ('class:text', f' [{bar}] '),
                    ('class:instruction', f'({self.min_value}-{self.max_value})')
                ]
            else:
                return f'{self.name}: {self.current_value} [{bar}] ({self.min_value}-{self.max_value})'
        
        # Create key bindings for slider interaction
        kb = KeyBindings()
        
        @kb.add('left')
        def _(event):
            if self.current_value > self.min_value:
                self.current_value = max(self.min_value, self.current_value - self.step)
                event.app.invalidate()
        
        @kb.add('right')
        def _(event):
            if self.current_value < self.max_value:
                self.current_value = min(self.max_value, self.current_value + self.step)
                event.app.invalidate()
        
        # Create window with formatted text control
        control = FormattedTextControl(
            text=get_slider_text,
            key_bindings=kb,
            focusable=True
        )
        
        return Window(content=control, height=1)

# Example: Custom Multi-Column List Component  
class MultiColumnListComponent(CustomComponentBase):
    """
    Custom multi-column list component using prompt-toolkit tables
    with Questionary styling.
    """
    
    def __init__(self, name: str, columns: list, data: list):
        super().__init__(name, "multi_column_list")
        self.columns = columns
        self.data = data
        self.selected_row = 0
        
    def to_prompt_toolkit(self) -> Window:
        """Create multi-column list using prompt-toolkit."""
        from prompt_toolkit.layout.controls import FormattedTextControl
        from prompt_toolkit.layout.containers import Window
        from prompt_toolkit.key_binding import KeyBindings
        
        def get_table_text():
            lines = []
            
            # Header
            header = ' | '.join(f'{col:15}' for col in self.columns)
            if self.questionary_style:
                lines.append([('class:question', header)])
                lines.append([('class:separator', '-' * len(header))])
            else:
                lines.append(header)
                lines.append('-' * len(header))
            
            # Data rows
            for i, row in enumerate(self.data):
                row_text = ' | '.join(f'{str(cell):15}' for cell in row)
                if i == self.selected_row:
                    if self.questionary_style:
                        lines.append([('class:highlighted', row_text)])
                    else:
                        lines.append(f'> {row_text}')
                else:
                    if self.questionary_style:
                        lines.append([('class:text', row_text)])
                    else:
                        lines.append(f'  {row_text}')
            
            return lines
        
        # Navigation key bindings
        kb = KeyBindings()
        
        @kb.add('up')
        def _(event):
            if self.selected_row > 0:
                self.selected_row -= 1
                event.app.invalidate()
        
        @kb.add('down')
        def _(event):
            if self.selected_row < len(self.data) - 1:
                self.selected_row += 1
                event.app.invalidate()
        
        control = FormattedTextControl(
            text=get_table_text,
            key_bindings=kb,
            focusable=True
        )
        
        return Window(content=control)
```

### Priority 3: Questionary Component Factory
**Goal**: Provide easy-to-use factories for creating Questionary-based components within TUI Engine layouts.

**Implementation**:
```python
# src/tui_engine/questionary_factory.py
import questionary
from questionary import Style
from .custom_component_base import CustomComponentBase

class QuestionaryComponentFactory:
    """
    Factory for creating TUI Engine components that wrap Questionary prompts.
    Enables easy integration of Questionary's rich input types within TUI Engine layouts.
    """
    
    @staticmethod
    def create_select_component(name: str, choices: list, message: str = "", style: Style = None) -> 'SelectComponent':
        """Create a select dropdown component using Questionary's select."""
        return SelectComponent(name, choices, message, style)
    
    @staticmethod
    def create_checkbox_component(name: str, choices: list, message: str = "", style: Style = None) -> 'CheckboxComponent':
        """Create a checkbox component using Questionary's checkbox."""
        return CheckboxComponent(name, choices, message, style)
    
    @staticmethod
    def create_confirm_component(name: str, message: str = "", style: Style = None) -> 'ConfirmComponent':
        """Create a yes/no confirmation component using Questionary's confirm."""
        return ConfirmComponent(name, message, style)
    
    @staticmethod
    def create_password_component(name: str, message: str = "", style: Style = None) -> 'PasswordComponent':
        """Create a password input component using Questionary's password."""
        return PasswordComponent(name, message, style)

class SelectComponent(CustomComponentBase):
    """Select dropdown component wrapping Questionary's select prompt."""
    
    def __init__(self, name: str, choices: list, message: str = "", style: Style = None):
        super().__init__(name, "select")
        self.choices = choices
        self.message = message or f"Select {name}:"
        self.selected_value = None
        if style:
            self.set_questionary_style(style)
    
    def to_prompt_toolkit(self):
        """Convert to prompt-toolkit widget using Questionary's select."""
        # Extract Questionary's internal prompt-toolkit components
        questionary_prompt = questionary.select(
            self.message,
            choices=self.choices,
            style=self.questionary_style
        )
        
        # Get the underlying prompt-toolkit layout
        return questionary_prompt._get_prompt_session().layout.container

class CheckboxComponent(CustomComponentBase):
    """Checkbox component wrapping Questionary's checkbox prompt."""
    
    def __init__(self, name: str, choices: list, message: str = "", style: Style = None):
        super().__init__(name, "checkbox")
        self.choices = choices
        self.message = message or f"Select {name} (multiple):"
        self.selected_values = []
        if style:
            self.set_questionary_style(style)
    
    def to_prompt_toolkit(self):
        """Convert to prompt-toolkit widget using Questionary's checkbox."""
        questionary_prompt = questionary.checkbox(
            self.message,
            choices=self.choices,
            style=self.questionary_style
        )
        
        return questionary_prompt._get_prompt_session().layout.container
```

### Priority 4: Component Extension Guidelines
**Goal**: Provide clear guidelines and examples for creating custom components.

**Custom Component Creation Patterns**:

1. **Pure Prompt-Toolkit Components**: For maximum customization
2. **Questionary-Wrapped Components**: For standard inputs with Questionary styling
3. **Hybrid Components**: Combining both approaches
4. **Composite Components**: Complex widgets built from multiple sub-components

**Example: Advanced Custom Component**:
```python
# Example: Custom Date Picker Component
class DatePickerComponent(CustomComponentBase):
    """
    Advanced date picker component demonstrating full customization capabilities.
    Combines custom prompt-toolkit widgets with Questionary styling.
    """
    
    def __init__(self, name: str, initial_date=None):
        super().__init__(name, "date_picker")
        self.selected_date = initial_date or datetime.date.today()
        self.view_mode = "day"  # day, month, year
        
    def to_prompt_toolkit(self):
        """Create sophisticated date picker interface."""
        from prompt_toolkit.layout import HSplit, VSplit
        from prompt_toolkit.layout.containers import Window
        from prompt_toolkit.layout.controls import FormattedTextControl
        from prompt_toolkit.key_binding import KeyBindings
        
        # Create calendar grid, navigation controls, etc.
        # This demonstrates full control over component creation
        
        # Header with month/year display
        header = Window(
            content=FormattedTextControl(self._get_header_text),
            height=1
        )
        
        # Calendar grid
        calendar_grid = Window(
            content=FormattedTextControl(
                text=self._get_calendar_text,
                key_bindings=self._get_calendar_keybindings(),
                focusable=True
            ),
            height=8
        )
        
        # Footer with instructions
        footer = Window(
            content=FormattedTextControl(self._get_footer_text),
            height=1
        )
        
        return HSplit([header, calendar_grid, footer])
    
    def _get_header_text(self):
        """Generate header text with Questionary styling."""
        month_year = self.selected_date.strftime("%B %Y")
        if self.questionary_style:
            return [
                ('class:question', 'Select Date: '),
                ('class:answer', month_year)
            ]
        else:
            return f'Select Date: {month_year}'
    
    def _get_calendar_text(self):
        """Generate calendar grid with styling."""
        # Implementation for calendar display
        # Shows how to create complex custom layouts
        pass
    
    def _get_calendar_keybindings(self):
        """Create key bindings for calendar navigation."""
        kb = KeyBindings()
        
        @kb.add('left')
        def _(event):
            # Navigate calendar
            pass
            
        @kb.add('right')  
        def _(event):
            # Navigate calendar
            pass
            
        return kb
```

## Integration Phases with Custom Component Support

### Phase 1: Foundation with Custom Component Framework (Week 1)
**Status**: Ready to implement
**Risk**: Low
**Tasks**:
1. Create `src/tui_engine/themes.py` with comprehensive styling
2. Create `src/tui_engine/custom_component_base.py` 
3. Create `src/tui_engine/questionary_factory.py`
4. Document custom component creation patterns
5. Create example custom components

**Files to create/modify**:
- `src/tui_engine/themes.py` - Comprehensive theme system
- `src/tui_engine/custom_component_base.py` - Base class for custom components
- `src/tui_engine/questionary_factory.py` - Questionary component factories
- `src/tui_engine/app.py` - Style system integration
- `docs/custom_component_guide.md` - Custom component creation guide

### Phase 2: Enhanced Validation with Custom Validator Support (Week 2)
**Status**: Planned  
**Risk**: Medium
**Tasks**:
1. Create enhanced validation system supporting custom validators
2. Implement validation adapters for existing and custom components
3. Add cursor positioning for validation errors
4. Create validation examples for custom components

### Phase 3: Focus Management with Custom Component Support (Week 3)
**Status**: Planned
**Risk**: Medium-High
**Tasks**:
1. Implement focus management that works with custom components
2. Ensure custom components integrate properly with navigation
3. Test focus behavior with complex custom layouts

### Phase 4: Advanced Custom Component Examples (Week 4)
**Status**: Future enhancement
**Risk**: Low
**Tasks**:
1. Create library of advanced custom components
2. Document best practices and patterns
3. Create component gallery and examples

## Custom Component Requirements Checklist

✅ **Base Framework**
- [ ] `CustomComponentBase` class with Questionary integration
- [ ] Access to raw prompt-toolkit widgets and controls
- [ ] Questionary style integration for custom components
- [ ] Hybrid layout capabilities (mix Questionary + prompt-toolkit)

✅ **Component Factories**  
- [ ] Questionary component wrappers (select, checkbox, confirm, etc.)
- [ ] Easy integration with TUI Engine layouts
- [ ] Style consistency across component types

✅ **Advanced Capabilities**
- [ ] Key binding integration for custom components
- [ ] Event handling and validation support
- [ ] Multi-widget composite components
- [ ] Complex layout support (tables, grids, calendars, etc.)

✅ **Documentation & Examples**
- [ ] Custom component creation guide
- [ ] Example implementations (slider, date picker, table, etc.)
- [ ] Best practices and patterns
- [ ] Integration with existing TUI Engine features

## Risk Assessment for Custom Components

### Low Risk Items
- Base component framework (extends existing patterns)
- Questionary component factories (wrapper approach)
- Theme system extension (additive functionality)

### Medium Risk Items
- Complex custom component integration with focus management
- Validation system integration with custom components
- Event handling between custom and standard components

### High Risk Items
- None identified (framework approach maintains flexibility)

### Mitigation Strategies
1. **Incremental development**: Start with simple custom components
2. **Comprehensive testing**: Test custom components with existing features
3. **Clear interfaces**: Well-defined base classes and contracts
4. **Extensive documentation**: Detailed guides and examples

## Success Criteria for Custom Component Support

### Phase 1 Success
- ✅ Can create custom components using `CustomComponentBase`
- ✅ Custom components integrate with Questionary styling
- ✅ Can mix prompt-toolkit widgets with Questionary components
- ✅ Comprehensive theme system supports custom styling

### Phase 2 Success  
- ✅ Custom components support validation integration
- ✅ Custom validators work with both standard and custom components
- ✅ Error display works consistently across component types

### Phase 3 Success
- ✅ Custom components integrate seamlessly with focus management
- ✅ Navigation works properly between custom and standard components
- ✅ Complex multi-widget components handle focus correctly

### Overall Success
- ✅ **Maintained and enhanced custom component creation capabilities**
- ✅ Easy integration of Questionary features in custom components
- ✅ Rich library of component patterns and examples
- ✅ Professional styling consistency across all component types
- ✅ Superior flexibility for advanced use cases

## Future Custom Component Opportunities

### Advanced Component Library
1. **Data visualization components**: Charts, graphs, progress indicators
2. **Table components**: Sortable tables, data grids, tree views
3. **Input components**: Date pickers, time selectors, file browsers
4. **Layout components**: Tabs, accordions, split panes
5. **Interactive components**: Sliders, color pickers, range selectors

### Integration Examples
1. **Database browser**: Custom table components with real-time data
2. **File manager**: Tree view with file operations
3. **Configuration editor**: Complex form with conditional fields
4. **Dashboard**: Multiple custom components in coordinated layout
5. **Game interfaces**: Interactive gaming UI components

## Conclusion

This integration plan ensures that TUI Engine not only gains the benefits of Questionary's mature input handling and styling system but also maintains and enhances its flexibility for creating custom components. The framework approach provides:

1. **Backward compatibility**: All existing functionality is preserved
2. **Forward flexibility**: Rich framework for custom component creation  
3. **Best of both worlds**: Questionary polish + TUI Engine power + Custom component freedom
4. **Comprehensive styling**: Consistent themes across all component types
5. **Advanced capabilities**: Support for any conceivable UI component

The integration maintains TUI Engine's core strength as a flexible, powerful framework while adding the professional polish and rich input capabilities that Questionary provides.