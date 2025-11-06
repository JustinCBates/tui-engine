"""
Dynamic Form Builder for TUI Engine

This module provides a comprehensive form building system that uses the ValidationSystem
to create dynamic, interactive forms with conditional fields, validation, and professional styling.

Features:
- Schema-based form definition
- Dynamic field generation
- Conditional field logic
- Comprehensive validation integration
- Professional themes
- Multi-step form support
- Export/import capabilities
- Real-time validation feedback
"""

from typing import Dict, List, Any, Optional, Callable, Union, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
import json
import copy
from datetime import datetime

from .validation import (
    EnhancedValidator, ValidationChain, ValidationResult, ValidationLevel,
    ValidatorRegistry, ValidationTheme, create_form_validator
)
from .themes import TUIEngineThemes
from .questionary_adapter import QuestionaryStyleAdapter

# For now, we'll create a simplified widget interface
# In a real implementation, these would import from the actual widget adapters


class FieldType(Enum):
    """Supported field types."""
    TEXT = "text"
    PASSWORD = "password"
    EMAIL = "email"
    NUMBER = "number"
    INTEGER = "integer"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    CHECKBOX = "checkbox"
    CONFIRM = "confirm"
    PATH = "path"
    FILE = "file"
    DIRECTORY = "directory"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    COLOR = "color"
    AUTOCOMPLETE = "autocomplete"
    EDITOR = "editor"
    URL = "url"
    PHONE = "phone"
    CREDIT_CARD = "credit_card"


@dataclass
class FieldDefinition:
    """Definition of a form field."""
    name: str
    type: FieldType
    label: Optional[str] = None
    description: Optional[str] = None
    required: bool = False
    default: Any = None
    placeholder: Optional[str] = None
    
    # Field-specific options
    options: List[Any] = field(default_factory=list)  # For select fields
    choices: Dict[str, str] = field(default_factory=dict)  # For select with labels
    multiple: bool = False  # For multi-select
    min_value: Optional[Union[int, float]] = None  # For numbers
    max_value: Optional[Union[int, float]] = None  # For numbers
    min_length: Optional[int] = None  # For text fields
    max_length: Optional[int] = None  # For text fields
    pattern: Optional[str] = None  # Regex pattern
    file_extensions: List[str] = field(default_factory=list)  # For file fields
    directory_only: bool = False  # For path fields
    date_format: str = "%Y-%m-%d"  # For date fields
    time_format: str = "%H:%M:%S"  # For time fields
    autocomplete_source: Optional[Callable] = None  # For autocomplete
    language: str = "text"  # For editor
    
    # Conditional logic
    condition: Optional[Dict[str, Any]] = None  # Show/hide condition
    depends_on: List[str] = field(default_factory=list)  # Field dependencies
    
    # Validation
    validators: List[str] = field(default_factory=list)  # Validator names
    custom_validator: Optional[Callable] = None
    validation_message: Optional[str] = None
    
    # Styling
    width: Optional[int] = None
    help_text: Optional[str] = None
    group: Optional[str] = None  # Field grouping
    
    def __post_init__(self):
        """Set default label if not provided."""
        if self.label is None:
            self.label = self.name.replace('_', ' ').title()


@dataclass
class FormSection:
    """A section/group of related fields."""
    name: str
    title: str
    description: Optional[str] = None
    fields: List[str] = field(default_factory=list)
    collapsible: bool = False
    collapsed: bool = False
    condition: Optional[Dict[str, Any]] = None


@dataclass
class FormSchema:
    """Complete form definition."""
    name: str
    title: str
    description: Optional[str] = None
    version: str = "1.0"
    theme: str = "professional_blue"
    
    fields: List[FieldDefinition] = field(default_factory=list)
    sections: List[FormSection] = field(default_factory=list)
    
    # Form behavior
    validate_on_change: bool = True
    show_progress: bool = False
    multi_step: bool = False
    steps: List[Dict[str, Any]] = field(default_factory=list)
    
    # Submission
    submit_label: str = "Submit"
    cancel_label: str = "Cancel"
    submit_handler: Optional[Callable] = None
    cancel_handler: Optional[Callable] = None
    
    # Metadata
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    author: Optional[str] = None
    
    def __post_init__(self):
        """Set timestamps."""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        self.modified_at = datetime.now().isoformat()


class ConditionalLogic:
    """Handles conditional field logic."""
    
    @staticmethod
    def evaluate_condition(condition: Dict[str, Any], form_data: Dict[str, Any]) -> bool:
        """
        Evaluate a conditional expression.
        
        Args:
            condition: Condition definition
            form_data: Current form data
            
        Returns:
            True if condition is met
        """
        if not condition:
            return True
        
        field_name = condition.get('field')
        operator = condition.get('operator', 'equals')
        value = condition.get('value')
        
        if field_name not in form_data:
            return False
        
        field_value = form_data[field_name]
        
        if operator == 'equals':
            return field_value == value
        elif operator == 'not_equals':
            return field_value != value
        elif operator == 'in':
            return field_value in value if isinstance(value, (list, tuple)) else False
        elif operator == 'not_in':
            return field_value not in value if isinstance(value, (list, tuple)) else True
        elif operator == 'greater_than':
            try:
                return float(field_value) > float(value)
            except (ValueError, TypeError):
                return False
        elif operator == 'less_than':
            try:
                return float(field_value) < float(value)
            except (ValueError, TypeError):
                return False
        elif operator == 'contains':
            return str(value).lower() in str(field_value).lower()
        elif operator == 'empty':
            return not field_value or (isinstance(field_value, str) and not field_value.strip())
        elif operator == 'not_empty':
            return bool(field_value and (not isinstance(field_value, str) or field_value.strip()))
        
        return False


class FormRenderer:
    """Renders forms using TUI Engine widgets."""
    
    def __init__(self, theme: str = "professional_blue"):
        """
        Initialize form renderer.
        
        Args:
            theme: Theme to use for styling
        """
        self.theme = theme
        self.validation_theme = ValidationTheme(theme)
        self.registry = ValidatorRegistry()
        
    def create_widget(self, field_def: FieldDefinition, form_data: Dict[str, Any]) -> Any:
        """
        Create a widget for a field definition.
        
        Args:
            field_def: Field definition
            form_data: Current form data
            
        Returns:
            Configured widget instance (simplified mock for now)
        """
        # For now, return a simple widget representation
        # In a real implementation, this would create actual TUI widgets
        widget_config = {
            'type': field_def.type.value,
            'name': field_def.name,
            'label': field_def.label or field_def.name,
            'theme': self.theme,
            'required': field_def.required,
            'default': field_def.default,
            'validators': []
        }
        
        # Add type-specific configuration
        if field_def.type == FieldType.SELECT:
            widget_config['choices'] = field_def.choices or {str(opt): str(opt) for opt in field_def.options}
            widget_config['multiple'] = field_def.multiple
        elif field_def.type == FieldType.NUMBER:
            widget_config['min_value'] = field_def.min_value
            widget_config['max_value'] = field_def.max_value
        elif field_def.type == FieldType.TEXT:
            widget_config['min_length'] = field_def.min_length
            widget_config['max_length'] = field_def.max_length
            widget_config['pattern'] = field_def.pattern
        elif field_def.type == FieldType.FILE:
            widget_config['file_extensions'] = field_def.file_extensions
        elif field_def.type == FieldType.DATETIME:
            widget_config['date_format'] = field_def.date_format
            widget_config['time_format'] = field_def.time_format
        elif field_def.type == FieldType.EDITOR:
            widget_config['language'] = field_def.language
        
        # Add validation rules
        if field_def.required:
            widget_config['validators'].append('required')
        
        for validator_name in field_def.validators:
            widget_config['validators'].append(validator_name)
        
        # Type-specific validation
        if field_def.type == FieldType.EMAIL:
            widget_config['validators'].append('email')
        elif field_def.type == FieldType.URL:
            widget_config['validators'].append('url')
        elif field_def.type == FieldType.PHONE:
            widget_config['validators'].append('phone')
        
        return MockWidget(widget_config)


class MockWidget:
    """Mock widget for testing purposes."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize mock widget with configuration."""
        self.config = config
        self.value = config.get('default', '')
        self.validators = []
        
    def add_validator(self, validator):
        """Add a validator to the widget."""
        if validator:
            self.validators.append(validator)
        return self
    
    def set_value(self, value):
        """Set widget value."""
        self.value = value
    
    def get_value(self):
        """Get widget value."""
        return self.value
    
    def validate(self):
        """Validate widget value."""
        # Simplified validation
        if self.config.get('required', False) and not self.value:
            return False
        return True
    
    def __repr__(self):
        return f"MockWidget({self.config['type']}, {self.config['name']})"


class FormBuilder:
    """Main form builder class."""
    
    def __init__(self, theme: str = "professional_blue"):
        """
        Initialize form builder.
        
        Args:
            theme: Default theme for forms
        """
        self.theme = theme
        self.renderer = FormRenderer(theme)
        self.validator = create_form_validator()
        self.conditional_logic = ConditionalLogic()
        
        # Form registry
        self.forms: Dict[str, FormSchema] = {}
        
    def create_form(self, name: str, title: str, **kwargs) -> FormSchema:
        """
        Create a new form schema.
        
        Args:
            name: Form identifier
            title: Form title
            **kwargs: Additional form options
            
        Returns:
            Form schema instance
        """
        # Extract theme to avoid duplicate keyword argument
        theme = kwargs.pop('theme', self.theme)
        
        schema = FormSchema(
            name=name,
            title=title,
            theme=theme,
            **kwargs
        )
        self.forms[name] = schema
        return schema
    
    def add_field(self, form_name: str, field_def: FieldDefinition) -> 'FormBuilder':
        """
        Add a field to a form.
        
        Args:
            form_name: Form identifier
            field_def: Field definition
            
        Returns:
            Self for chaining
        """
        if form_name not in self.forms:
            raise ValueError(f"Form '{form_name}' not found")
        
        self.forms[form_name].fields.append(field_def)
        return self
    
    def add_section(self, form_name: str, section: FormSection) -> 'FormBuilder':
        """
        Add a section to a form.
        
        Args:
            form_name: Form identifier
            section: Section definition
            
        Returns:
            Self for chaining
        """
        if form_name not in self.forms:
            raise ValueError(f"Form '{form_name}' not found")
        
        self.forms[form_name].sections.append(section)
        return self
    
    def build_form(self, form_name: str) -> 'DynamicForm':
        """
        Build a dynamic form instance.
        
        Args:
            form_name: Form identifier
            
        Returns:
            Dynamic form instance
        """
        if form_name not in self.forms:
            raise ValueError(f"Form '{form_name}' not found")
        
        schema = self.forms[form_name]
        return DynamicForm(schema, self.renderer, self.validator, self.conditional_logic)
    
    def load_schema(self, schema_data: Union[str, Dict[str, Any]]) -> FormSchema:
        """
        Load form schema from JSON or dict.
        
        Args:
            schema_data: JSON string or dictionary
            
        Returns:
            Form schema instance
        """
        if isinstance(schema_data, str):
            data = json.loads(schema_data)
        else:
            data = schema_data
        
        # Convert field definitions
        fields = []
        for field_data in data.get('fields', []):
            field_data['type'] = FieldType(field_data['type'])
            fields.append(FieldDefinition(**field_data))
        
        # Convert sections
        sections = []
        for section_data in data.get('sections', []):
            sections.append(FormSection(**section_data))
        
        # Create schema
        schema_data = {k: v for k, v in data.items() if k not in ['fields', 'sections']}
        schema = FormSchema(fields=fields, sections=sections, **schema_data)
        
        self.forms[schema.name] = schema
        return schema
    
    def save_schema(self, form_name: str) -> str:
        """
        Save form schema to JSON.
        
        Args:
            form_name: Form identifier
            
        Returns:
            JSON string
        """
        if form_name not in self.forms:
            raise ValueError(f"Form '{form_name}' not found")
        
        schema = self.forms[form_name]
        
        # Convert to dictionary
        data = {
            'name': schema.name,
            'title': schema.title,
            'description': schema.description,
            'version': schema.version,
            'theme': schema.theme,
            'validate_on_change': schema.validate_on_change,
            'show_progress': schema.show_progress,
            'multi_step': schema.multi_step,
            'steps': schema.steps,
            'submit_label': schema.submit_label,
            'cancel_label': schema.cancel_label,
            'created_at': schema.created_at,
            'modified_at': schema.modified_at,
            'author': schema.author,
            'fields': [],
            'sections': []
        }
        
        # Convert fields
        for field_def in schema.fields:
            field_data = {
                'name': field_def.name,
                'type': field_def.type.value,
                'label': field_def.label,
                'description': field_def.description,
                'required': field_def.required,
                'default': field_def.default,
                'placeholder': field_def.placeholder,
                'options': field_def.options,
                'choices': field_def.choices,
                'multiple': field_def.multiple,
                'min_value': field_def.min_value,
                'max_value': field_def.max_value,
                'min_length': field_def.min_length,
                'max_length': field_def.max_length,
                'pattern': field_def.pattern,
                'file_extensions': field_def.file_extensions,
                'directory_only': field_def.directory_only,
                'date_format': field_def.date_format,
                'time_format': field_def.time_format,
                'language': field_def.language,
                'condition': field_def.condition,
                'depends_on': field_def.depends_on,
                'validators': field_def.validators,
                'validation_message': field_def.validation_message,
                'width': field_def.width,
                'help_text': field_def.help_text,
                'group': field_def.group
            }
            data['fields'].append(field_data)
        
        # Convert sections
        for section in schema.sections:
            section_data = {
                'name': section.name,
                'title': section.title,
                'description': section.description,
                'fields': section.fields,
                'collapsible': section.collapsible,
                'collapsed': section.collapsed,
                'condition': section.condition
            }
            data['sections'].append(section_data)
        
        return json.dumps(data, indent=2)
    
    def list_forms(self) -> List[str]:
        """Get list of available form names."""
        return list(self.forms.keys())
    
    def get_form_info(self, form_name: str) -> Dict[str, Any]:
        """
        Get information about a form.
        
        Args:
            form_name: Form identifier
            
        Returns:
            Form information
        """
        if form_name not in self.forms:
            raise ValueError(f"Form '{form_name}' not found")
        
        schema = self.forms[form_name]
        return {
            'name': schema.name,
            'title': schema.title,
            'description': schema.description,
            'field_count': len(schema.fields),
            'section_count': len(schema.sections),
            'theme': schema.theme,
            'created_at': schema.created_at,
            'modified_at': schema.modified_at
        }


class DynamicForm:
    """A dynamic form instance."""
    
    def __init__(self, schema: FormSchema, renderer: FormRenderer, 
                 validator: EnhancedValidator, conditional_logic: ConditionalLogic):
        """
        Initialize dynamic form.
        
        Args:
            schema: Form schema
            renderer: Form renderer
            validator: Form validator
            conditional_logic: Conditional logic handler
        """
        self.schema = schema
        self.renderer = renderer
        self.validator = validator
        self.conditional_logic = conditional_logic
        
        # Form state
        self.data: Dict[str, Any] = {}
        self.widgets: Dict[str, Any] = {}
        self.visible_fields: List[str] = []
        self.current_step = 0
        self.submitted = False
        
        # Initialize form
        self._setup_form()
    
    def _setup_form(self):
        """Setup form widgets and validation."""
        # Create widgets for all fields
        for field_def in self.schema.fields:
            widget = self.renderer.create_widget(field_def, self.data)
            self.widgets[field_def.name] = widget
            
            # Setup validation chain
            chain = self.validator.add_field(field_def.name)
            
            if field_def.required:
                chain.required(field_def.validation_message or f"{field_def.label} is required")
            
            # Add built-in validators
            for validator_name in field_def.validators:
                validator_rule = self.renderer.registry.get(validator_name)
                if validator_rule:
                    chain.add_rule(validator_rule)
            
            # Add field-specific validation based on type
            if field_def.type == FieldType.EMAIL:
                chain.email()
            elif field_def.type == FieldType.URL:
                chain.url()
            elif field_def.type == FieldType.PHONE:
                chain.phone()
            
            # Length validation
            if field_def.min_length is not None:
                chain.min_length(field_def.min_length)
            if field_def.max_length is not None:
                chain.max_length(field_def.max_length)
            
            # Number range validation using custom validators
            if field_def.type in [FieldType.NUMBER, FieldType.INTEGER]:
                if field_def.min_value is not None:
                    min_val = field_def.min_value
                    chain.custom(
                        lambda x: float(x) >= min_val if x and str(x).replace('.', '').replace('-', '').isdigit() else False,
                        f"Value must be at least {min_val}",
                        f"min_value_{min_val}"
                    )
                if field_def.max_value is not None:
                    max_val = field_def.max_value
                    chain.custom(
                        lambda x: float(x) <= max_val if x and str(x).replace('.', '').replace('-', '').isdigit() else False,
                        f"Value must be no more than {max_val}",
                        f"max_value_{max_val}"
                    )
        
        # Update visible fields
        self._update_visible_fields()
    
    def _update_visible_fields(self):
        """Update which fields are visible based on conditions."""
        self.visible_fields = []
        
        for field_def in self.schema.fields:
            if self.conditional_logic.evaluate_condition(field_def.condition, self.data):
                self.visible_fields.append(field_def.name)
    
    def set_field_value(self, field_name: str, value: Any) -> bool:
        """
        Set a field value and update form state.
        
        Args:
            field_name: Field name
            value: Field value
            
        Returns:
            True if validation passed
        """
        self.data[field_name] = value
        
        # Update visible fields (conditional logic)
        self._update_visible_fields()
        
        # Validate if enabled
        if self.schema.validate_on_change:
            results = self.validator.validate_field(field_name, value)
            return all(r.is_valid for r in results)
        
        return True
    
    def get_field_value(self, field_name: str) -> Any:
        """Get a field value."""
        return self.data.get(field_name)
    
    def validate_form(self) -> bool:
        """
        Validate the entire form.
        
        Returns:
            True if all validations pass
        """
        # Store current data in validator
        for field_name, value in self.data.items():
            if field_name in self.visible_fields:
                self.validator.set_field_value(field_name, value)
        
        return self.validator.is_valid()
    
    def get_validation_errors(self) -> Dict[str, List[ValidationResult]]:
        """Get validation errors for all fields."""
        return self.validator.get_errors()
    
    def get_field_errors(self, field_name: str) -> List[ValidationResult]:
        """Get validation errors for a specific field."""
        errors = self.validator.get_errors(field_name)
        return errors.get(field_name, [])
    
    def render_field(self, field_name: str) -> str:
        """
        Render a field as a string.
        
        Args:
            field_name: Field name
            
        Returns:
            Rendered field representation
        """
        if field_name not in self.widgets:
            return f"Field '{field_name}' not found"
        
        if field_name not in self.visible_fields:
            return f"Field '{field_name}' is hidden"
        
        widget = self.widgets[field_name]
        value = self.data.get(field_name, "")
        errors = self.get_field_errors(field_name)
        
        # Format field representation
        field_def = next((f for f in self.schema.fields if f.name == field_name), None)
        if not field_def:
            return f"Field definition for '{field_name}' not found"
        
        result = f"📝 {field_def.label or field_name}"
        if field_def.required:
            result += " *"
        result += f": {value}"
        
        if errors:
            result += f" ❌ ({len(errors)} errors)"
        else:
            result += " ✅"
        
        return result
    
    def render_form(self) -> str:
        """
        Render the entire form as a string.
        
        Returns:
            Rendered form representation
        """
        lines = []
        lines.append(f"📋 {self.schema.title}")
        if self.schema.description:
            lines.append(f"   {self.schema.description}")
        lines.append("")
        
        # Group fields by section
        if self.schema.sections:
            for section in self.schema.sections:
                if self.conditional_logic.evaluate_condition(section.condition, self.data):
                    lines.append(f"📂 {section.title}")
                    if section.description:
                        lines.append(f"   {section.description}")
                    
                    for field_name in section.fields:
                        if field_name in self.visible_fields:
                            lines.append(f"  {self.render_field(field_name)}")
                    lines.append("")
        else:
            # No sections, show all visible fields
            for field_name in self.visible_fields:
                lines.append(self.render_field(field_name))
        
        # Show validation summary
        if self.data:
            valid_count = sum(1 for f in self.visible_fields if not self.get_field_errors(f))
            total_count = len(self.visible_fields)
            error_count = sum(len(self.get_field_errors(f)) for f in self.visible_fields)
            
            lines.append("")
            lines.append(f"📊 Status: {valid_count}/{total_count} fields valid")
            if error_count > 0:
                lines.append(f"❌ {error_count} validation errors")
            else:
                lines.append("✅ Form is valid")
        
        return "\n".join(lines)
    
    def submit(self) -> Dict[str, Any]:
        """
        Submit the form.
        
        Returns:
            Form submission result
        """
        if not self.validate_form():
            errors = self.get_validation_errors()
            return {
                'success': False,
                'errors': errors,
                'message': f"Form has {sum(len(errs) for errs in errors.values())} validation errors"
            }
        
        self.submitted = True
        
        # Call submit handler if provided
        if self.schema.submit_handler:
            try:
                result = self.schema.submit_handler(self.data)
                return {
                    'success': True,
                    'data': self.data,
                    'result': result,
                    'message': 'Form submitted successfully'
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'message': f'Submission failed: {e}'
                }
        
        return {
            'success': True,
            'data': self.data,
            'message': 'Form submitted successfully'
        }
    
    def reset(self):
        """Reset form to initial state."""
        self.data.clear()
        self.submitted = False
        self.current_step = 0
        # Don't reset validator chains, just clear the data and cache
        self.validator.cache.clear()
        self.validator.form_data.clear()
        self._update_visible_fields()
    
    def export_data(self) -> Dict[str, Any]:
        """Export form data with metadata."""
        return {
            'schema_name': self.schema.name,
            'schema_version': self.schema.version,
            'data': self.data.copy(),  # Return a copy, not a reference!
            'submitted': self.submitted,
            'timestamp': datetime.now().isoformat(),
            'visible_fields': self.visible_fields.copy()  # Also copy this list
        }
    
    def import_data(self, data: Dict[str, Any]) -> bool:
        """
        Import form data.
        
        Args:
            data: Data to import
            
        Returns:
            True if successful
        """
        try:
            if 'data' in data and isinstance(data['data'], dict):
                # Import data directly
                imported_data = data['data']
                self.data.clear()
                self.data.update(imported_data)
                
                # Sync data with validator using set_field_value method
                for field_name, value in self.data.items():
                    self.validator.set_field_value(field_name, value)
            
            if 'submitted' in data:
                self.submitted = data.get('submitted', False)
            
            # Update visible fields AFTER setting all data
            self._update_visible_fields()
            
            return True
        except Exception as e:
            print(f"Import error: {e}")  # Debug
            import traceback
            traceback.print_exc()
            return False


# Convenience functions
def create_simple_form(title: str, fields: List[Dict[str, Any]], **kwargs) -> DynamicForm:
    """
    Create a simple form from field specifications.
    
    Args:
        title: Form title
        fields: List of field specifications
        **kwargs: Additional form options
        
    Returns:
        Dynamic form instance
    """
    builder = FormBuilder()
    form_name = title.lower().replace(' ', '_')
    
    schema = builder.create_form(form_name, title, **kwargs)
    
    for field_spec in fields:
        field_type = FieldType(field_spec['type'])
        field_def = FieldDefinition(
            name=field_spec['name'],
            type=field_type,
            **{k: v for k, v in field_spec.items() if k not in ['name', 'type']}
        )
        builder.add_field(form_name, field_def)
    
    return builder.build_form(form_name)


def create_registration_form(theme: str = "professional_blue") -> DynamicForm:
    """Create a user registration form."""
    return create_simple_form(
        "User Registration",
        [
            {'name': 'username', 'type': 'text', 'required': True, 'min_length': 3, 'max_length': 20},
            {'name': 'email', 'type': 'email', 'required': True},
            {'name': 'password', 'type': 'password', 'required': True, 'min_length': 8},
            {'name': 'confirm_password', 'type': 'password', 'required': True},
            {'name': 'full_name', 'type': 'text', 'required': True},
            {'name': 'phone', 'type': 'phone', 'required': False},
            {'name': 'terms_accepted', 'type': 'checkbox', 'required': True, 'label': 'I accept the terms and conditions'}
        ],
        theme=theme
    )


def create_contact_form(theme: str = "professional_blue") -> DynamicForm:
    """Create a contact form."""
    return create_simple_form(
        "Contact Us",
        [
            {'name': 'name', 'type': 'text', 'required': True},
            {'name': 'email', 'type': 'email', 'required': True},
            {'name': 'subject', 'type': 'select', 'required': True, 
             'choices': {'general': 'General Inquiry', 'support': 'Support', 'sales': 'Sales', 'other': 'Other'}},
            {'name': 'message', 'type': 'editor', 'required': True, 'language': 'text'},
            {'name': 'newsletter', 'type': 'checkbox', 'label': 'Subscribe to newsletter'}
        ],
        theme=theme
    )


def create_settings_form(theme: str = "professional_blue") -> DynamicForm:
    """Create a settings form."""
    return create_simple_form(
        "Application Settings",
        [
            {'name': 'app_name', 'type': 'text', 'required': True, 'default': 'My App'},
            {'name': 'theme', 'type': 'select', 'required': True, 'default': 'professional_blue',
             'choices': {'professional_blue': 'Professional Blue', 'elegant_dark': 'Elegant Dark', 
                        'vibrant_green': 'Vibrant Green', 'warm_orange': 'Warm Orange', 'minimalist_gray': 'Minimalist Gray'}},
            {'name': 'auto_save', 'type': 'checkbox', 'default': True},
            {'name': 'backup_interval', 'type': 'number', 'min_value': 1, 'max_value': 60, 'default': 5},
            {'name': 'log_level', 'type': 'select', 'required': True, 'default': 'info',
             'choices': {'debug': 'Debug', 'info': 'Info', 'warning': 'Warning', 'error': 'Error'}},
            {'name': 'data_directory', 'type': 'directory', 'required': True},
            {'name': 'language', 'type': 'select', 'default': 'en',
             'choices': {'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German'}}
        ],
        theme=theme
    )