# TUI Engine API Documentation

Complete API reference for TUI Engine's questionary integration system.

## Table of Contents

1. [Themes System](#themes-system)
2. [Validation Framework](#validation-framework)
3. [Form Builder](#form-builder)
4. [Widget Integration](#widget-integration)
5. [Questionary Adapter](#questionary-adapter)
6. [Utilities](#utilities)
7. [Examples](#examples)

---

## Themes System

### TUIEngineThemes

Central theme management for consistent styling across all components.

#### Class Methods

##### `get_theme(theme_name: str) -> Optional[Style]`

Get a theme by name.

```python
from tui_engine.themes import TUIEngineThemes

# Get a specific theme
theme = TUIEngineThemes.get_theme('professional_blue')
```

**Parameters:**
- `theme_name` (str): Name of the theme to retrieve

**Returns:**
- `Style`: Questionary Style object or None if theme not found

**Available Themes:**
- `professional_blue`: Clean corporate styling
- `dark_mode`: Modern dark theme
- `high_contrast`: Accessibility-focused high contrast
- `classic_terminal`: Traditional terminal appearance
- `minimal`: Clean minimalist design

##### `list_themes() -> List[str]`

Get a list of all available theme names.

```python
themes = TUIEngineThemes.list_themes()
print(themes)  # ['professional_blue', 'dark_mode', 'high_contrast', 'classic_terminal', 'minimal']
```

**Returns:**
- `List[str]`: List of available theme names

##### `get_theme_description(theme_name: str) -> Optional[str]`

Get a description of a theme.

```python
description = TUIEngineThemes.get_theme_description('professional_blue')
print(description)  # "Professional blue theme with modern corporate styling..."
```

##### `create_custom_theme(base_theme: str, overrides: Dict[str, str]) -> Style`

Create a custom theme based on an existing theme with overrides.

```python
custom_theme = TUIEngineThemes.create_custom_theme(
    'professional_blue',
    {
        'question': 'fg:#ff6b6b bold',
        'answer': 'fg:#4ecdc4 bold'
    }
)
```

**Parameters:**
- `base_theme` (str): Base theme name
- `overrides` (Dict[str, str]): Style overrides

**Returns:**
- `Style`: Custom questionary Style object

##### `get_theme_preview(theme_name: str) -> str`

Get a preview string showing how the theme looks.

```python
preview = TUIEngineThemes.get_theme_preview('professional_blue')
print(preview)
```

---

## Validation Framework

### ValidationResult

Result of a validation operation.

#### Attributes

- `is_valid` (bool): Whether validation passed
- `message` (str): Validation message
- `level` (ValidationLevel): Severity level (SUCCESS, INFO, WARNING, ERROR)
- `field_name` (Optional[str]): Field that was validated
- `validator_type` (Optional[str]): Type of validator used

```python
from tui_engine.validation import ValidationResult, ValidationLevel

result = ValidationResult(
    is_valid=False,
    message="Email format is invalid",
    level=ValidationLevel.ERROR,
    field_name="email",
    validator_type="EmailValidator"
)
```

### BaseValidator

Abstract base class for all validators.

#### Methods

##### `validate(value: Any) -> ValidationResult`

Validate a value (abstract method).

##### `set_message(message: str) -> 'BaseValidator'`

Set custom validation message.

```python
validator = EmailValidator().set_message("Please enter a valid email address")
```

### Built-in Validators

#### EmailValidator

Validates email addresses using RFC 5322 compliant regex.

```python
from tui_engine.validation import EmailValidator

validator = EmailValidator()
result = validator.validate("user@example.com")
```

#### URLValidator

Validates URLs with support for various protocols.

```python
from tui_engine.validation import URLValidator

validator = URLValidator(allowed_schemes=['http', 'https'])
result = validator.validate("https://example.com")
```

#### PhoneValidator

Validates phone numbers with international format support.

```python
from tui_engine.validation import PhoneValidator

validator = PhoneValidator()
result = validator.validate("+1-555-123-4567")
```

#### NumberValidator

Validates numeric values with range constraints.

```python
from tui_engine.validation import NumberValidator

validator = NumberValidator(min_value=0, max_value=100)
result = validator.validate(42)
```

#### CreditCardValidator

Validates credit card numbers using Luhn algorithm.

```python
from tui_engine.validation import CreditCardValidator

validator = CreditCardValidator()
result = validator.validate("4532015112830366")
```

#### DateValidator

Validates dates with format and range constraints.

```python
from tui_engine.validation import DateValidator
from datetime import date

validator = DateValidator(
    date_format="%Y-%m-%d",
    min_date=date(2020, 1, 1),
    max_date=date(2030, 12, 31)
)
result = validator.validate("2023-06-15")
```

#### LengthValidator

Validates string length.

```python
from tui_engine.validation import LengthValidator

validator = LengthValidator(min_length=8, max_length=50)
result = validator.validate("password123")
```

#### PatternValidator

Validates against regular expression patterns.

```python
from tui_engine.validation import PatternValidator

validator = PatternValidator(r"^[A-Z]{3}-\d{4}$", "Format: ABC-1234")
result = validator.validate("DEF-5678")
```

#### RequiredValidator

Validates that a value is not empty.

```python
from tui_engine.validation import RequiredValidator

validator = RequiredValidator()
result = validator.validate("some value")
```

### ValidationChain

Fluent interface for chaining multiple validators.

```python
from tui_engine.validation import create_form_validator

validator = create_form_validator()
email_chain = validator.add_field("email")
email_chain.required().email().set_message("Please enter a valid email")

# Validate
results = validator.validate_field("email", "user@example.com")
```

#### Methods

##### `required(message: Optional[str] = None) -> 'ValidationChain'`

Add required validation.

##### `email(message: Optional[str] = None) -> 'ValidationChain'`

Add email validation.

##### `url(allowed_schemes: Optional[List[str]] = None, message: Optional[str] = None) -> 'ValidationChain'`

Add URL validation.

##### `phone(message: Optional[str] = None) -> 'ValidationChain'`

Add phone validation.

##### `number(min_value: Optional[float] = None, max_value: Optional[float] = None, message: Optional[str] = None) -> 'ValidationChain'`

Add number validation.

##### `length(min_length: Optional[int] = None, max_length: Optional[int] = None, message: Optional[str] = None) -> 'ValidationChain'`

Add length validation.

##### `pattern(pattern: str, message: Optional[str] = None) -> 'ValidationChain'`

Add pattern validation.

##### `credit_card(message: Optional[str] = None) -> 'ValidationChain'`

Add credit card validation.

##### `date_range(min_date: Optional[date] = None, max_date: Optional[date] = None, date_format: str = "%Y-%m-%d", message: Optional[str] = None) -> 'ValidationChain'`

Add date validation.

##### `custom(validator: BaseValidator) -> 'ValidationChain'`

Add custom validator.

### EnhancedValidator

Advanced form validation with field dependencies and caching.

```python
from tui_engine.validation import create_form_validator

validator = create_form_validator()

# Add field with validation chain
email_chain = validator.add_field("email")
email_chain.required().email()

# Validate specific field
results = validator.validate_field("email", "test@example.com")

# Validate all fields
all_results = validator.validate_all({
    "email": "test@example.com",
    "name": "John Doe"
})
```

#### Methods

##### `add_field(field_name: str) -> ValidationChain`

Add a field with validation chain.

##### `validate_field(field_name: str, value: Any) -> List[ValidationResult]`

Validate a specific field.

##### `validate_all(data: Dict[str, Any]) -> Dict[str, List[ValidationResult]]`

Validate all registered fields.

##### `is_valid(field_name: str, value: Any) -> bool`

Quick validation check.

##### `get_field_errors(field_name: str, value: Any) -> List[str]`

Get error messages for a field.

##### `clear_cache()`

Clear validation cache.

### ValidationTheme

Theme-aware validation styling.

```python
from tui_engine.validation import ValidationTheme

theme = ValidationTheme("professional_blue")
styled_error = theme.style_message("Error message", ValidationLevel.ERROR)
```

---

## Form Builder

### FieldType

Enumeration of supported field types.

```python
from tui_engine.form_builder import FieldType

# Available types
FieldType.TEXT          # Basic text input
FieldType.PASSWORD      # Password input with masking
FieldType.EMAIL         # Email input with validation
FieldType.URL           # URL input with validation
FieldType.PHONE         # Phone number input
FieldType.NUMBER        # Numeric input
FieldType.INTEGER       # Integer input
FieldType.SELECT        # Single selection dropdown
FieldType.MULTI_SELECT  # Multiple selection
FieldType.CHECKBOX      # Checkbox input
FieldType.CONFIRM       # Yes/No confirmation
FieldType.PATH          # File/directory path
FieldType.FILE          # File selection
FieldType.DIRECTORY     # Directory selection
FieldType.DATE          # Date input
FieldType.TIME          # Time input
FieldType.DATETIME      # Date and time input
FieldType.CREDIT_CARD   # Credit card input
FieldType.COLOR         # Color picker
FieldType.PROGRESS      # Progress indicator
FieldType.EDITOR        # Multi-line text editor
FieldType.AUTOCOMPLETE  # Autocomplete input
FieldType.PRESS         # Key press detection
FieldType.RANGE         # Range slider
```

### FieldDefinition

Defines a form field with validation and styling.

```python
from tui_engine.form_builder import FieldDefinition, FieldType

field = FieldDefinition(
    name="email",
    field_type=FieldType.EMAIL,
    label="Email Address",
    required=True,
    placeholder="Enter your email",
    help_text="We'll never share your email",
    validation_message="Please enter a valid email address"
)
```

#### Parameters

- `name` (str): Unique field identifier
- `field_type` (FieldType): Type of field
- `label` (Optional[str]): Display label
- `required` (bool): Whether field is required
- `placeholder` (Optional[str]): Placeholder text
- `help_text` (Optional[str]): Help description
- `validation_message` (Optional[str]): Custom validation message
- `choices` (Optional[Dict[str, str]]): Options for select fields
- `default_value` (Optional[Any]): Default field value
- `min_value` (Optional[Union[int, float]]): Minimum numeric value
- `max_value` (Optional[Union[int, float]]): Maximum numeric value
- `min_length` (Optional[int]): Minimum string length
- `max_length` (Optional[int]): Maximum string length
- `pattern` (Optional[str]): Regex pattern for validation
- `readonly` (bool): Whether field is read-only
- `disabled` (bool): Whether field is disabled
- `hidden` (bool): Whether field is hidden
- `condition` (Optional[Dict[str, Any]]): Conditional display logic
- `file_extensions` (Optional[List[str]]): Allowed file extensions
- `multiple` (bool): Allow multiple values
- `step` (Optional[Union[int, float]]): Step for numeric inputs
- `language` (Optional[str]): Language for editor fields

### FormSchema

Complete form definition with metadata.

```python
from tui_engine.form_builder import FormSchema

schema = FormSchema(
    name="registration",
    title="User Registration",
    description="Create your account",
    version="1.0",
    theme="professional_blue",
    multi_step=True,
    validate_on_change=True
)
```

### FormBuilder

Main class for building dynamic forms.

```python
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType

# Create builder
builder = FormBuilder(theme="professional_blue")

# Create form schema
schema = builder.create_form("contact", "Contact Form")

# Add fields
email_field = FieldDefinition("email", FieldType.EMAIL, required=True)
builder.add_field("contact", email_field)

# Build form instance
form = builder.build_form("contact")
```

#### Methods

##### `__init__(theme: str = "professional_blue")`

Initialize form builder with theme.

##### `create_form(name: str, title: str, **kwargs) -> FormSchema`

Create a new form schema.

**Parameters:**
- `name` (str): Form identifier
- `title` (str): Form display title
- `**kwargs`: Additional form options

**Returns:**
- `FormSchema`: Form schema instance

##### `add_field(form_name: str, field_def: FieldDefinition) -> 'FormBuilder'`

Add a field to a form.

##### `build_form(form_name: str) -> DynamicForm`

Build a dynamic form instance.

##### `save_schema(form_name: str) -> str`

Serialize form schema to JSON.

##### `load_schema(json_data: str) -> FormSchema`

Load form schema from JSON.

### DynamicForm

Runtime form instance with state management.

```python
# Create form (using FormBuilder)
form = builder.build_form("contact")

# Set field values
form.set_field_value("email", "user@example.com")
form.set_field_value("name", "John Doe")

# Get field values
email = form.get_field_value("email")

# Validate form
is_valid = form.validate_form()

# Get validation errors
errors = form.get_validation_errors()

# Export/import data
data = form.export_data()
form.import_data(data)

# Reset form
form.reset()

# Submit form
result = form.submit()
```

#### Methods

##### `set_field_value(field_name: str, value: Any)`

Set a field value.

##### `get_field_value(field_name: str) -> Any`

Get a field value.

##### `validate_form() -> bool`

Validate entire form.

##### `validate_field(field_name: str) -> bool`

Validate specific field.

##### `get_validation_errors() -> List[str]`

Get all validation error messages.

##### `export_data() -> Dict[str, Any]`

Export form data as dictionary.

##### `import_data(data: Dict[str, Any])`

Import form data from dictionary.

##### `reset()`

Reset form to initial state.

##### `submit() -> Dict[str, Any]`

Submit form and get result.

##### `render_form() -> str`

Render form as text representation.

#### Properties

- `visible_fields` (List[str]): Currently visible field names
- `current_step` (int): Current step in multi-step form
- `submitted` (bool): Whether form has been submitted

### Utility Functions

#### `create_registration_form(theme: str = "professional_blue") -> DynamicForm`

Create a pre-configured user registration form.

```python
from tui_engine.form_builder import create_registration_form

form = create_registration_form("professional_blue")
```

#### `create_contact_form(theme: str = "professional_blue") -> DynamicForm`

Create a pre-configured contact form.

```python
from tui_engine.form_builder import create_contact_form

form = create_contact_form("dark_mode")
```

#### `create_settings_form(theme: str = "professional_blue") -> DynamicForm`

Create a pre-configured settings form.

```python
from tui_engine.form_builder import create_settings_form

form = create_settings_form("high_contrast")
```

### Conditional Logic

Forms support conditional field display based on other field values.

```python
# Field with condition
conditional_field = FieldDefinition(
    name="company_name",
    field_type=FieldType.TEXT,
    condition={
        "field": "user_type",
        "operator": "equals",
        "value": "business"
    }
)
```

#### Supported Operators

- `equals`: Field value equals specified value
- `not_equals`: Field value does not equal specified value  
- `greater_than`: Field value is greater than specified value
- `less_than`: Field value is less than specified value
- `greater_equal`: Field value is greater than or equal to specified value
- `less_equal`: Field value is less than or equal to specified value
- `in`: Field value is in list of specified values
- `not_in`: Field value is not in list of specified values
- `contains`: Field value contains specified substring
- `empty`: Field value is empty
- `not_empty`: Field value is not empty

---

## Widget Integration

TUI Engine integrates with questionary widgets through a unified interface.

### Widget Types

Each FieldType maps to specific widget implementations:

- **Text Widgets**: `TEXT`, `PASSWORD`, `EMAIL`, `URL`, `PHONE`
- **Selection Widgets**: `SELECT`, `MULTI_SELECT`, `CHECKBOX`, `CONFIRM` 
- **Input Widgets**: `NUMBER`, `INTEGER`, `DATE`, `TIME`, `DATETIME`
- **File Widgets**: `FILE`, `DIRECTORY`, `PATH`
- **Special Widgets**: `CREDIT_CARD`, `COLOR`, `PROGRESS`, `EDITOR`
- **Interactive Widgets**: `AUTOCOMPLETE`, `PRESS`, `RANGE`

### Widget Configuration

Widgets are automatically configured based on FieldDefinition:

```python
# Widget inherits validation, styling, and behavior from field definition
field = FieldDefinition(
    name="email",
    field_type=FieldType.EMAIL,
    required=True,
    placeholder="Enter email",
    validation_message="Invalid email format"
)

# Widget created automatically with these settings
widget = renderer.create_widget(field, form_data)
```

---

## Questionary Adapter

### QuestionaryStyleAdapter

Converts TUI Engine themes to questionary-compatible styles.

```python
from tui_engine.questionary_adapter import QuestionaryStyleAdapter

# Create adapter for specific theme
adapter = QuestionaryStyleAdapter("professional_blue")

# Use with questionary
import questionary
answer = questionary.text("Your name:", style=adapter.style).ask()
```

#### Methods

##### `__init__(theme_name: str)`

Initialize adapter with theme.

##### `get_style() -> Style`

Get questionary Style object.

#### Properties

- `style` (Style): Questionary Style object for the theme

---

## Utilities

### Helper Functions

#### `create_form_validator() -> EnhancedValidator`

Create a new form validator instance.

```python
from tui_engine.validation import create_form_validator

validator = create_form_validator()
```

---

## Examples

### Complete Form Example

```python
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType
from tui_engine.themes import TUIEngineThemes

# Create form builder
builder = FormBuilder("professional_blue")

# Create form schema
schema = builder.create_form(
    "survey", 
    "Customer Survey",
    description="Help us improve our service"
)

# Add fields with validation
fields = [
    FieldDefinition(
        "name", 
        FieldType.TEXT, 
        label="Full Name",
        required=True,
        min_length=2
    ),
    FieldDefinition(
        "email", 
        FieldType.EMAIL, 
        label="Email Address",
        required=True,
        placeholder="you@example.com"
    ),
    FieldDefinition(
        "satisfaction", 
        FieldType.SELECT,
        label="How satisfied are you?",
        choices={
            "1": "Very Unsatisfied",
            "2": "Unsatisfied", 
            "3": "Neutral",
            "4": "Satisfied",
            "5": "Very Satisfied"
        },
        required=True
    ),
    FieldDefinition(
        "feedback",
        FieldType.EDITOR,
        label="Additional Feedback",
        condition={
            "field": "satisfaction",
            "operator": "in", 
            "value": ["1", "2", "3"]
        },
        language="text"
    )
]

# Add all fields
for field in fields:
    builder.add_field("survey", field)

# Build form
form = builder.build_form("survey")

# Set some values
form.set_field_value("name", "John Doe")
form.set_field_value("email", "john@example.com")
form.set_field_value("satisfaction", "2")

# This will make feedback field visible due to conditional logic
form.set_field_value("feedback", "The service could be faster")

# Validate
if form.validate_form():
    # Submit
    result = form.submit()
    print("Survey submitted successfully!")
else:
    # Show errors
    errors = form.get_validation_errors()
    for error in errors:
        print(f"Error: {error}")

# Export data
survey_data = form.export_data()
print(survey_data)
```

### Theme Switching Example

```python
from tui_engine.themes import TUIEngineThemes
from tui_engine.form_builder import create_registration_form

# List available themes
themes = TUIEngineThemes.list_themes()
print("Available themes:", themes)

# Create forms with different themes
forms = {}
for theme_name in themes:
    forms[theme_name] = create_registration_form(theme_name)
    print(f"Created registration form with {theme_name} theme")

# Use specific themed form
form = forms["dark_mode"]
form.set_field_value("email", "user@example.com")
```

### Custom Validation Example

```python
from tui_engine.validation import BaseValidator, ValidationResult, ValidationLevel

class PasswordStrengthValidator(BaseValidator):
    """Custom password strength validator."""
    
    def validate(self, value: Any) -> ValidationResult:
        if not isinstance(value, str):
            return ValidationResult(
                is_valid=False,
                message="Password must be a string",
                level=ValidationLevel.ERROR
            )
        
        score = 0
        if len(value) >= 8:
            score += 1
        if any(c.isupper() for c in value):
            score += 1
        if any(c.islower() for c in value):
            score += 1
        if any(c.isdigit() for c in value):
            score += 1
        if any(c in "!@#$%^&*" for c in value):
            score += 1
        
        if score >= 4:
            return ValidationResult(
                is_valid=True,
                message="Strong password",
                level=ValidationLevel.SUCCESS
            )
        elif score >= 2:
            return ValidationResult(
                is_valid=True,
                message="Medium strength password",
                level=ValidationLevel.WARNING
            )
        else:
            return ValidationResult(
                is_valid=False,
                message="Password too weak",
                level=ValidationLevel.ERROR
            )

# Use custom validator
from tui_engine.validation import create_form_validator

validator = create_form_validator()
password_chain = validator.add_field("password")
password_chain.required().custom(PasswordStrengthValidator())

# Validate password
results = validator.validate_field("password", "MyStr0ng!Pass")
for result in results:
    print(f"{result.level.name}: {result.message}")
```

### Multi-Step Form Example

```python
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType

builder = FormBuilder("professional_blue")

# Create multi-step form
schema = builder.create_form(
    "onboarding",
    "Employee Onboarding", 
    multi_step=True,
    steps=[
        {"name": "personal", "title": "Personal Information"},
        {"name": "work", "title": "Work Information"}, 
        {"name": "it", "title": "IT Setup"}
    ]
)

# Step 1: Personal info
personal_fields = [
    FieldDefinition("first_name", FieldType.TEXT, required=True),
    FieldDefinition("last_name", FieldType.TEXT, required=True),
    FieldDefinition("email", FieldType.EMAIL, required=True)
]

# Step 2: Work info  
work_fields = [
    FieldDefinition("department", FieldType.SELECT, 
                   choices={"eng": "Engineering", "sales": "Sales"}, 
                   required=True),
    FieldDefinition("start_date", FieldType.DATE, required=True)
]

# Step 3: IT setup
it_fields = [
    FieldDefinition("laptop", FieldType.SELECT,
                   choices={"mac": "MacBook", "windows": "Windows"})
]

# Add all fields
for field in personal_fields + work_fields + it_fields:
    builder.add_field("onboarding", field)

# Build and use form
form = builder.build_form("onboarding")

# Navigate steps
print(f"Current step: {form.current_step}")
# Fill step data and move to next step
```

This comprehensive API documentation covers all major components and provides practical examples for developers to integrate TUI Engine's questionary system into their applications.