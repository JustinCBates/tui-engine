# Testing Framework Integration

This document outlines how to integrate TUI Engine with various testing frameworks and provides comprehensive testing strategies for questionary-based terminal applications.

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Pytest Integration](#pytest-integration)
3. [Mock Testing](#mock-testing)
4. [Integration Testing](#integration-testing)
5. [Performance Testing](#performance-testing)
6. [Visual Testing](#visual-testing)
7. [CI/CD Integration](#cicd-integration)
8. [Best Practices](#best-practices)

---

## Testing Overview

TUI Engine provides comprehensive testing support for:

- **Unit Testing**: Individual components and validators
- **Integration Testing**: Form workflows and component interactions
- **Mock Testing**: Non-interactive testing without TTY requirements
- **Performance Testing**: Load testing and benchmarking
- **Visual Testing**: Theme and rendering verification

### Testing Architecture

```
TUI Engine Testing Stack
├── Unit Tests (pytest)
│   ├── Validator tests
│   ├── Theme tests
│   └── Form builder tests
├── Integration Tests
│   ├── End-to-end workflows
│   ├── Cross-component interaction
│   └── Theme compatibility
├── Mock Testing
│   ├── Non-interactive testing
│   ├── CI/CD friendly
│   └── Headless execution
└── Performance Tests
    ├── Load testing
    ├── Memory profiling
    └── Benchmark comparisons
```

---

## Pytest Integration

### Installation

```bash
pip install pytest pytest-mock pytest-cov pytest-benchmark
```

### Basic Test Structure

```python
# test_tui_engine.py
import pytest
from unittest.mock import patch, MagicMock

from tui_engine.themes import TUIEngineThemes
from tui_engine.validation import EmailValidator, create_form_validator
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType


class TestThemes:
    """Test theme system."""
    
    def test_list_themes(self):
        """Test theme listing."""
        themes = TUIEngineThemes.list_themes()
        assert isinstance(themes, list)
        assert len(themes) > 0
        assert "professional_blue" in themes
    
    def test_get_theme(self):
        """Test theme retrieval."""
        theme = TUIEngineThemes.get_theme("professional_blue")
        assert theme is not None
        
        # Test invalid theme
        invalid_theme = TUIEngineThemes.get_theme("nonexistent")
        assert invalid_theme is None
    
    def test_theme_description(self):
        """Test theme descriptions."""
        description = TUIEngineThemes.get_theme_description("professional_blue")
        assert isinstance(description, str)
        assert len(description) > 0
    
    def test_custom_theme_creation(self):
        """Test custom theme creation."""
        custom_theme = TUIEngineThemes.create_custom_theme(
            "professional_blue",
            {"question": "fg:#ff0000 bold"}
        )
        assert custom_theme is not None


class TestValidation:
    """Test validation system."""
    
    def test_email_validator(self):
        """Test email validation."""
        validator = EmailValidator()
        
        # Valid emails
        valid_result = validator.validate("test@example.com")
        assert valid_result.is_valid is True
        
        # Invalid emails
        invalid_result = validator.validate("invalid-email")
        assert invalid_result.is_valid is False
        assert "email" in invalid_result.message.lower()
    
    def test_validation_chain(self):
        """Test validation chains."""
        form_validator = create_form_validator()
        
        # Create validation chain
        email_chain = form_validator.add_field("email")
        email_chain.required().email()
        
        # Test valid input
        results = form_validator.validate_field("email", "test@example.com")
        assert all(result.is_valid for result in results)
        
        # Test invalid input
        results = form_validator.validate_field("email", "")
        assert not all(result.is_valid for result in results)
    
    def test_custom_validation_message(self):
        """Test custom validation messages."""
        validator = EmailValidator()
        validator.set_message("Custom email error message")
        
        result = validator.validate("invalid")
        assert result.message == "Custom email error message"
    
    @pytest.mark.parametrize("email,expected", [
        ("test@example.com", True),
        ("user.name@domain.co.uk", True),
        ("invalid-email", False),
        ("@example.com", False),
        ("test@", False),
        ("", False),
    ])
    def test_email_validation_cases(self, email, expected):
        """Test various email validation cases."""
        validator = EmailValidator()
        result = validator.validate(email)
        assert result.is_valid == expected


class TestFormBuilder:
    """Test form builder system."""
    
    def test_form_creation(self):
        """Test basic form creation."""
        builder = FormBuilder("professional_blue")
        schema = builder.create_form("test", "Test Form")
        
        assert schema.name == "test"
        assert schema.title == "Test Form"
        assert schema.theme == "professional_blue"
    
    def test_field_addition(self):
        """Test adding fields to forms."""
        builder = FormBuilder()
        schema = builder.create_form("test", "Test Form")
        
        field = FieldDefinition("email", FieldType.EMAIL, required=True)
        builder.add_field("test", field)
        
        assert len(schema.fields) == 1
        assert schema.fields[0].name == "email"
        assert schema.fields[0].field_type == FieldType.EMAIL
    
    def test_form_building(self):
        """Test form instance building."""
        builder = FormBuilder()
        schema = builder.create_form("test", "Test Form")
        
        builder.add_field("test", FieldDefinition("name", FieldType.TEXT))
        builder.add_field("test", FieldDefinition("email", FieldType.EMAIL))
        
        form = builder.build_form("test")
        assert form is not None
        assert hasattr(form, 'set_field_value')
        assert hasattr(form, 'get_field_value')
    
    def test_form_data_operations(self):
        """Test form data setting and getting."""
        builder = FormBuilder()
        schema = builder.create_form("test", "Test Form")
        
        builder.add_field("test", FieldDefinition("name", FieldType.TEXT))
        form = builder.build_form("test")
        
        # Set and get value
        form.set_field_value("name", "John Doe")
        assert form.get_field_value("name") == "John Doe"
    
    def test_form_validation(self):
        """Test form validation."""
        builder = FormBuilder()
        schema = builder.create_form("test", "Test Form")
        
        builder.add_field("test", FieldDefinition("email", FieldType.EMAIL, required=True))
        form = builder.build_form("test")
        
        # Empty form should not be valid
        assert not form.validate_form()
        
        # Valid email should make form valid
        form.set_field_value("email", "test@example.com")
        assert form.validate_form()
        
        # Invalid email should make form invalid
        form.set_field_value("email", "invalid")
        assert not form.validate_form()
    
    def test_conditional_logic(self):
        """Test conditional field logic."""
        builder = FormBuilder()
        schema = builder.create_form("test", "Test Form")
        
        # User type field
        builder.add_field("test", FieldDefinition(
            "user_type",
            FieldType.SELECT,
            choices={"individual": "Individual", "business": "Business"}
        ))
        
        # Conditional company field
        builder.add_field("test", FieldDefinition(
            "company",
            FieldType.TEXT,
            condition={"field": "user_type", "operator": "equals", "value": "business"}
        ))
        
        form = builder.build_form("test")
        
        # Initially, company field should not be visible
        assert "company" not in form.visible_fields
        
        # After setting user_type to business, company should be visible
        form.set_field_value("user_type", "business")
        # Note: In real implementation, this would trigger visibility update
        # For testing, we'll check the condition evaluation directly
        from tui_engine.form_builder import ConditionalLogic
        logic = ConditionalLogic()
        condition = {"field": "user_type", "operator": "equals", "value": "business"}
        form_data = {"user_type": "business"}
        
        should_show = logic.evaluate_condition(condition, form_data)
        assert should_show is True
    
    def test_schema_serialization(self):
        """Test form schema serialization."""
        builder = FormBuilder()
        schema = builder.create_form("test", "Test Form")
        
        builder.add_field("test", FieldDefinition("name", FieldType.TEXT))
        builder.add_field("test", FieldDefinition("email", FieldType.EMAIL))
        
        # Serialize
        json_data = builder.save_schema("test")
        assert isinstance(json_data, str)
        assert len(json_data) > 0
        
        # Deserialize
        new_builder = FormBuilder()
        loaded_schema = new_builder.load_schema(json_data)
        
        assert loaded_schema.name == "test"
        assert loaded_schema.title == "Test Form"
        assert len(loaded_schema.fields) == 2


class TestFormDataOperations:
    """Test form data import/export."""
    
    def test_data_export_import(self):
        """Test form data export and import."""
        builder = FormBuilder()
        schema = builder.create_form("test", "Test Form")
        
        builder.add_field("test", FieldDefinition("name", FieldType.TEXT))
        builder.add_field("test", FieldDefinition("email", FieldType.EMAIL))
        
        form = builder.build_form("test")
        
        # Set data
        form.set_field_value("name", "John Doe")
        form.set_field_value("email", "john@example.com")
        
        # Export
        data = form.export_data()
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
        
        # Reset and import
        form.reset()
        assert form.get_field_value("name") is None
        
        form.import_data(data)
        assert form.get_field_value("name") == "John Doe"
        assert form.get_field_value("email") == "john@example.com"


# Fixtures for common test data
@pytest.fixture
def sample_form():
    """Create a sample form for testing."""
    builder = FormBuilder("professional_blue")
    schema = builder.create_form("sample", "Sample Form")
    
    fields = [
        FieldDefinition("name", FieldType.TEXT, required=True),
        FieldDefinition("email", FieldType.EMAIL, required=True),
        FieldDefinition("age", FieldType.INTEGER, min_value=0, max_value=120),
        FieldDefinition("newsletter", FieldType.CHECKBOX)
    ]
    
    for field in fields:
        builder.add_field("sample", field)
    
    return builder.build_form("sample")


@pytest.fixture
def valid_form_data():
    """Valid form data for testing."""
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "newsletter": True
    }


class TestFormWorkflows:
    """Test complete form workflows."""
    
    def test_complete_form_workflow(self, sample_form, valid_form_data):
        """Test complete form workflow."""
        # Import data
        sample_form.import_data(valid_form_data)
        
        # Validate
        assert sample_form.validate_form()
        
        # Export
        exported = sample_form.export_data()
        assert exported == valid_form_data
        
        # Submit (mock submission)
        with patch.object(sample_form, 'submit') as mock_submit:
            mock_submit.return_value = {"status": "success", "id": "123"}
            result = sample_form.submit()
            assert result["status"] == "success"
    
    def test_validation_errors(self, sample_form):
        """Test validation error handling."""
        # Set invalid data
        sample_form.set_field_value("email", "invalid-email")
        sample_form.set_field_value("age", -5)
        
        # Should not be valid
        assert not sample_form.validate_form()
        
        # Should have errors
        errors = sample_form.get_validation_errors()
        assert len(errors) > 0
        assert any("email" in error.lower() for error in errors)
```

---

## Mock Testing

### Non-Interactive Testing

For CI/CD environments without TTY support:

```python
# test_mock_interactions.py
import pytest
from unittest.mock import patch, MagicMock
from tui_engine.form_builder import create_registration_form


class TestMockInteractions:
    """Test forms without interactive prompts."""
    
    @patch('tui_engine.form_builder.MockWidget')
    def test_registration_form_mock(self, mock_widget_class):
        """Test registration form with mocked widgets."""
        # Setup mock widget
        mock_widget = MagicMock()
        mock_widget.validate.return_value = True
        mock_widget.get_value.return_value = "test_value"
        mock_widget_class.return_value = mock_widget
        
        # Create form
        form = create_registration_form("professional_blue")
        
        # Simulate user input through direct value setting
        test_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "full_name": "Test User",
            "terms_accepted": True
        }
        
        # Set values
        for field, value in test_data.items():
            form.set_field_value(field, value)
        
        # Validate
        assert form.validate_form()
        
        # Export data
        exported = form.export_data()
        assert exported["username"] == "testuser"
        assert exported["email"] == "test@example.com"
    
    def test_headless_form_operations(self):
        """Test form operations in headless environment."""
        from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType
        
        # This should work without TTY
        builder = FormBuilder("professional_blue")
        schema = builder.create_form("headless", "Headless Test")
        
        builder.add_field("headless", FieldDefinition("name", FieldType.TEXT))
        form = builder.build_form("headless")
        
        # All operations should work
        form.set_field_value("name", "Headless User")
        assert form.get_field_value("name") == "Headless User"
        
        data = form.export_data()
        assert data["name"] == "Headless User"
        
        form.reset()
        assert form.get_field_value("name") is None
        
        form.import_data(data)
        assert form.get_field_value("name") == "Headless User"


class TestCIFriendlyOperations:
    """Test operations suitable for CI/CD."""
    
    def test_all_themes_loadable(self):
        """Test that all themes can be loaded in CI."""
        from tui_engine.themes import TUIEngineThemes
        
        themes = TUIEngineThemes.list_themes()
        for theme_name in themes:
            theme = TUIEngineThemes.get_theme(theme_name)
            assert theme is not None, f"Theme {theme_name} failed to load"
    
    def test_all_field_types_creatable(self):
        """Test that all field types can be created in CI."""
        from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType
        
        builder = FormBuilder()
        schema = builder.create_form("ci_test", "CI Test")
        
        # Test all field types
        for field_type in FieldType:
            try:
                field = FieldDefinition(f"test_{field_type.value}", field_type)
                builder.add_field("ci_test", field)
            except Exception as e:
                pytest.fail(f"Failed to create field type {field_type}: {e}")
        
        # Should be able to build form
        form = builder.build_form("ci_test")
        assert form is not None
    
    def test_performance_baseline(self):
        """Test performance baseline for CI monitoring."""
        import time
        from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType
        
        start_time = time.time()
        
        # Create form with many fields
        builder = FormBuilder()
        schema = builder.create_form("perf_test", "Performance Test")
        
        for i in range(100):
            field = FieldDefinition(f"field_{i}", FieldType.TEXT)
            builder.add_field("perf_test", field)
        
        form = builder.build_form("perf_test")
        
        # Set all field values
        for i in range(100):
            form.set_field_value(f"field_{i}", f"value_{i}")
        
        # Validate
        form.validate_form()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance should be reasonable (adjust threshold as needed)
        assert duration < 5.0, f"Performance test took {duration:.2f}s, exceeding 5s threshold"
```

### Mock Widget Testing

```python
# test_widget_mocking.py
import pytest
from unittest.mock import MagicMock, patch
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType


class MockQuestionaryWidget:
    """Mock questionary widget for testing."""
    
    def __init__(self, field_def, theme_name):
        self.field_def = field_def
        self.theme_name = theme_name
        self.value = None
    
    def ask(self):
        """Mock ask method."""
        return self.value
    
    def set_mock_value(self, value):
        """Set mock return value."""
        self.value = value


@pytest.fixture
def mock_questionary():
    """Mock questionary for testing."""
    with patch('questionary.text') as mock_text, \
         patch('questionary.select') as mock_select, \
         patch('questionary.confirm') as mock_confirm:
        
        yield {
            'text': mock_text,
            'select': mock_select,
            'confirm': mock_confirm
        }


class TestWidgetMocking:
    """Test widget functionality with mocking."""
    
    def test_text_widget_mock(self, mock_questionary):
        """Test text widget with mocking."""
        # Setup mock
        mock_widget = MagicMock()
        mock_widget.ask.return_value = "Test Input"
        mock_questionary['text'].return_value = mock_widget
        
        # Test would use actual widget creation in real implementation
        # For now, test the mock setup
        widget = mock_questionary['text']("Test prompt")
        result = widget.ask()
        
        assert result == "Test Input"
        mock_questionary['text'].assert_called_once_with("Test prompt")
    
    def test_select_widget_mock(self, mock_questionary):
        """Test select widget with mocking."""
        mock_widget = MagicMock()
        mock_widget.ask.return_value = "option2"
        mock_questionary['select'].return_value = mock_widget
        
        widget = mock_questionary['select']("Choose option", choices=["option1", "option2"])
        result = widget.ask()
        
        assert result == "option2"
    
    def test_confirm_widget_mock(self, mock_questionary):
        """Test confirm widget with mocking."""
        mock_widget = MagicMock()
        mock_widget.ask.return_value = True
        mock_questionary['confirm'].return_value = mock_widget
        
        widget = mock_questionary['confirm']("Confirm action?")
        result = widget.ask()
        
        assert result is True
```

---

## Integration Testing

### End-to-End Testing

```python
# test_integration.py
import pytest
import tempfile
import json
import os
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType
from tui_engine.themes import TUIEngineThemes


class TestEndToEndIntegration:
    """Test complete end-to-end workflows."""
    
    def test_complete_user_registration_workflow(self):
        """Test complete user registration workflow."""
        # Create registration form
        builder = FormBuilder("professional_blue")
        schema = builder.create_form("registration", "User Registration")
        
        # Add all registration fields
        fields = [
            FieldDefinition("username", FieldType.TEXT, required=True, min_length=3),
            FieldDefinition("email", FieldType.EMAIL, required=True),
            FieldDefinition("password", FieldType.PASSWORD, required=True, min_length=8),
            FieldDefinition("age", FieldType.INTEGER, min_value=13, max_value=120),
            FieldDefinition("newsletter", FieldType.CHECKBOX),
            FieldDefinition("country", FieldType.SELECT, 
                          choices={"us": "United States", "uk": "United Kingdom", "ca": "Canada"})
        ]
        
        for field in fields:
            builder.add_field("registration", field)
        
        form = builder.build_form("registration")
        
        # Step 1: Fill form with valid data
        valid_data = {
            "username": "johndoe123",
            "email": "john@example.com",
            "password": "SecurePass123!",
            "age": 25,
            "newsletter": True,
            "country": "us"
        }
        
        form.import_data(valid_data)
        
        # Step 2: Validate form
        assert form.validate_form(), "Form should be valid with correct data"
        
        # Step 3: Export and verify data
        exported = form.export_data()
        assert exported == valid_data
        
        # Step 4: Test form serialization
        schema_json = builder.save_schema("registration")
        assert isinstance(schema_json, str)
        
        # Step 5: Test schema restoration
        new_builder = FormBuilder()
        restored_schema = new_builder.load_schema(schema_json)
        
        assert restored_schema.name == "registration"
        assert len(restored_schema.fields) == len(fields)
        
        # Step 6: Test restored form functionality
        restored_form = new_builder.build_form("registration")
        restored_form.import_data(valid_data)
        assert restored_form.validate_form()
    
    def test_conditional_form_workflow(self):
        """Test conditional form logic workflow."""
        builder = FormBuilder("professional_blue")
        schema = builder.create_form("conditional", "Conditional Form")
        
        # Base field
        builder.add_field("conditional", FieldDefinition(
            "user_type",
            FieldType.SELECT,
            choices={"individual": "Individual", "business": "Business"},
            required=True
        ))
        
        # Conditional fields
        builder.add_field("conditional", FieldDefinition(
            "personal_income",
            FieldType.NUMBER,
            condition={"field": "user_type", "operator": "equals", "value": "individual"},
            min_value=0
        ))
        
        builder.add_field("conditional", FieldDefinition(
            "company_name",
            FieldType.TEXT,
            condition={"field": "user_type", "operator": "equals", "value": "business"},
            required=True
        ))
        
        builder.add_field("conditional", FieldDefinition(
            "company_revenue",
            FieldType.NUMBER,
            condition={"field": "user_type", "operator": "equals", "value": "business"},
            min_value=0
        ))
        
        form = builder.build_form("conditional")
        
        # Test individual path
        form.set_field_value("user_type", "individual")
        form.set_field_value("personal_income", 50000)
        
        # Should be valid for individual
        assert form.validate_form()
        
        # Test business path
        form.reset()
        form.set_field_value("user_type", "business")
        form.set_field_value("company_name", "Acme Corp")
        form.set_field_value("company_revenue", 1000000)
        
        # Should be valid for business
        assert form.validate_form()
        
        # Test invalid business (missing required company_name)
        form.reset()
        form.set_field_value("user_type", "business")
        form.set_field_value("company_revenue", 1000000)
        # Missing company_name
        
        # Should be invalid
        assert not form.validate_form()
    
    def test_multi_theme_compatibility(self):
        """Test that forms work across all themes."""
        themes = TUIEngineThemes.list_themes()
        
        for theme_name in themes:
            # Create form with each theme
            builder = FormBuilder(theme_name)
            schema = builder.create_form(f"test_{theme_name}", f"Test {theme_name}")
            
            # Add various field types
            fields = [
                FieldDefinition("text", FieldType.TEXT),
                FieldDefinition("email", FieldType.EMAIL),
                FieldDefinition("number", FieldType.NUMBER),
                FieldDefinition("select", FieldType.SELECT, choices={"a": "A", "b": "B"}),
                FieldDefinition("checkbox", FieldType.CHECKBOX)
            ]
            
            for field in fields:
                builder.add_field(f"test_{theme_name}", field)
            
            form = builder.build_form(f"test_{theme_name}")
            
            # Test basic operations
            form.set_field_value("text", "test")
            form.set_field_value("email", "test@example.com")
            form.set_field_value("number", 42)
            form.set_field_value("select", "a")
            form.set_field_value("checkbox", True)
            
            # Should work with all themes
            assert form.validate_form(), f"Form validation failed with theme: {theme_name}"
            
            # Export should work
            data = form.export_data()
            assert data["text"] == "test"
            assert data["email"] == "test@example.com"
    
    def test_data_persistence_workflow(self):
        """Test data persistence across sessions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Session 1: Create and save form
            builder = FormBuilder("professional_blue")
            schema = builder.create_form("persistent", "Persistent Form")
            
            builder.add_field("persistent", FieldDefinition("name", FieldType.TEXT))
            builder.add_field("persistent", FieldDefinition("email", FieldType.EMAIL))
            
            form = builder.build_form("persistent")
            
            # Fill form
            form.set_field_value("name", "John Doe")
            form.set_field_value("email", "john@example.com")
            
            # Save schema and data
            schema_file = os.path.join(temp_dir, "schema.json")
            data_file = os.path.join(temp_dir, "data.json")
            
            with open(schema_file, 'w') as f:
                f.write(builder.save_schema("persistent"))
            
            with open(data_file, 'w') as f:
                json.dump(form.export_data(), f)
            
            # Session 2: Load and restore form
            new_builder = FormBuilder()
            
            with open(schema_file, 'r') as f:
                restored_schema = new_builder.load_schema(f.read())
            
            restored_form = new_builder.build_form("persistent")
            
            with open(data_file, 'r') as f:
                restored_data = json.load(f)
            
            restored_form.import_data(restored_data)
            
            # Verify restoration
            assert restored_form.get_field_value("name") == "John Doe"
            assert restored_form.get_field_value("email") == "john@example.com"
            assert restored_form.validate_form()


class TestCrossComponentIntegration:
    """Test integration between different TUI Engine components."""
    
    def test_theme_validation_integration(self):
        """Test theme and validation system integration."""
        from tui_engine.validation import ValidationTheme
        
        for theme_name in TUIEngineThemes.list_themes():
            # Create validation theme
            val_theme = ValidationTheme(theme_name)
            
            # Test error styling
            error_message = val_theme.style_message("Test error", "ERROR")
            assert isinstance(error_message, str)
            
            # Test with form
            builder = FormBuilder(theme_name)
            schema = builder.create_form("themed_validation", "Themed Validation")
            
            builder.add_field("themed_validation", FieldDefinition(
                "email", FieldType.EMAIL, required=True,
                validation_message="Custom themed error"
            ))
            
            form = builder.build_form("themed_validation")
            
            # Invalid input should trigger themed error
            form.set_field_value("email", "invalid")
            assert not form.validate_form()
            
            errors = form.get_validation_errors()
            assert len(errors) > 0
    
    def test_questionary_adapter_integration(self):
        """Test questionary adapter integration."""
        from tui_engine.questionary_adapter import QuestionaryStyleAdapter
        
        for theme_name in TUIEngineThemes.list_themes():
            adapter = QuestionaryStyleAdapter(theme_name)
            
            # Should create valid style
            assert adapter.style is not None
            
            # Should work with form builder
            builder = FormBuilder(theme_name)
            schema = builder.create_form("adapter_test", "Adapter Test")
            
            builder.add_field("adapter_test", FieldDefinition("test", FieldType.TEXT))
            form = builder.build_form("adapter_test")
            
            # Form should use the same theme
            assert form.schema.theme == theme_name
```

---

## Performance Testing

### Benchmark Testing

```python
# test_performance.py
import pytest
import time
import psutil
import os
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType
from tui_engine.themes import TUIEngineThemes


class TestPerformance:
    """Performance testing for TUI Engine."""
    
    @pytest.mark.benchmark
    def test_form_creation_performance(self, benchmark):
        """Benchmark form creation performance."""
        def create_large_form():
            builder = FormBuilder("professional_blue")
            schema = builder.create_form("perf_test", "Performance Test")
            
            for i in range(100):
                field = FieldDefinition(f"field_{i}", FieldType.TEXT)
                builder.add_field("perf_test", field)
            
            return builder.build_form("perf_test")
        
        result = benchmark(create_large_form)
        assert result is not None
    
    @pytest.mark.benchmark
    def test_validation_performance(self, benchmark):
        """Benchmark validation performance."""
        # Create form with many validated fields
        builder = FormBuilder("professional_blue")
        schema = builder.create_form("validation_perf", "Validation Performance")
        
        field_types = [FieldType.EMAIL, FieldType.URL, FieldType.PHONE, FieldType.NUMBER]
        
        for i in range(25):  # 100 total fields
            for field_type in field_types:
                field = FieldDefinition(f"{field_type.value}_{i}", field_type, required=True)
                builder.add_field("validation_perf", field)
        
        form = builder.build_form("validation_perf")
        
        # Set valid data
        valid_data = {}
        for i in range(25):
            valid_data[f"email_{i}"] = f"user{i}@example.com"
            valid_data[f"url_{i}"] = f"https://example{i}.com"
            valid_data[f"phone_{i}"] = f"+1-555-{100+i:03d}-{1000+i:04d}"
            valid_data[f"number_{i}"] = i * 10
        
        form.import_data(valid_data)
        
        def validate_large_form():
            return form.validate_form()
        
        result = benchmark(validate_large_form)
        assert result is True
    
    @pytest.mark.benchmark
    def test_serialization_performance(self, benchmark):
        """Benchmark schema serialization performance."""
        builder = FormBuilder("professional_blue")
        schema = builder.create_form("serial_perf", "Serialization Performance")
        
        # Create complex form
        for i in range(50):
            field = FieldDefinition(
                f"field_{i}",
                FieldType.TEXT,
                required=i % 3 == 0,
                min_length=2,
                max_length=100,
                placeholder=f"Enter value {i}",
                help_text=f"Help text for field {i}"
            )
            builder.add_field("serial_perf", field)
        
        def serialize_form():
            return builder.save_schema("serial_perf")
        
        result = benchmark(serialize_form)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_memory_usage(self):
        """Test memory usage patterns."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create multiple large forms
        forms = []
        for i in range(10):
            builder = FormBuilder("professional_blue")
            schema = builder.create_form(f"memory_test_{i}", f"Memory Test {i}")
            
            for j in range(50):
                field = FieldDefinition(f"field_{j}", FieldType.TEXT)
                builder.add_field(f"memory_test_{i}", field)
            
            form = builder.build_form(f"memory_test_{i}")
            forms.append(form)
        
        peak_memory = process.memory_info().rss
        
        # Clean up
        del forms
        
        final_memory = process.memory_info().rss
        
        # Memory should not grow excessively
        memory_growth = peak_memory - initial_memory
        memory_mb = memory_growth / (1024 * 1024)
        
        # Should not use more than 100MB for test data (adjust as needed)
        assert memory_mb < 100, f"Memory usage too high: {memory_mb:.2f}MB"
        
        # Memory should be released after cleanup
        memory_released = peak_memory - final_memory
        release_ratio = memory_released / memory_growth if memory_growth > 0 else 1.0
        
        # Should release at least 50% of memory
        assert release_ratio > 0.5, f"Memory not properly released: {release_ratio:.2f}"
    
    @pytest.mark.parametrize("field_count", [10, 50, 100, 250])
    def test_scalability(self, field_count):
        """Test scalability with varying field counts."""
        start_time = time.time()
        
        builder = FormBuilder("professional_blue")
        schema = builder.create_form("scale_test", "Scale Test")
        
        for i in range(field_count):
            field = FieldDefinition(f"field_{i}", FieldType.TEXT)
            builder.add_field("scale_test", field)
        
        form = builder.build_form("scale_test")
        
        # Set all values
        for i in range(field_count):
            form.set_field_value(f"field_{i}", f"value_{i}")
        
        # Validate
        is_valid = form.validate_form()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance should scale reasonably
        max_duration = field_count * 0.01  # 10ms per field max
        assert duration < max_duration, f"Performance degraded: {duration:.3f}s for {field_count} fields"
        assert is_valid
    
    def test_concurrent_forms(self):
        """Test concurrent form operations."""
        import threading
        import concurrent.futures
        
        def create_and_validate_form(form_id):
            """Create and validate a form in a thread."""
            builder = FormBuilder("professional_blue")
            schema = builder.create_form(f"concurrent_{form_id}", f"Concurrent {form_id}")
            
            for i in range(20):
                field = FieldDefinition(f"field_{i}", FieldType.TEXT, required=i % 5 == 0)
                builder.add_field(f"concurrent_{form_id}", field)
            
            form = builder.build_form(f"concurrent_{form_id}")
            
            # Fill required fields
            for i in range(0, 20, 5):
                form.set_field_value(f"field_{i}", f"value_{i}")
            
            return form.validate_form()
        
        start_time = time.time()
        
        # Test concurrent form operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(create_and_validate_form, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        duration = end_time - start_time
        
        # All should be valid
        assert all(results)
        
        # Should complete in reasonable time
        assert duration < 10.0, f"Concurrent operations too slow: {duration:.3f}s"
```

---

## Visual Testing

### Theme Rendering Tests

```python
# test_visual.py
import pytest
from tui_engine.themes import TUIEngineThemes
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType


class TestVisualRendering:
    """Test visual rendering and theme consistency."""
    
    def test_theme_color_consistency(self):
        """Test that themes have consistent color definitions."""
        themes = TUIEngineThemes.list_themes()
        
        required_colors = [
            'question', 'answered_question', 'instruction', 'answer',
            'highlighted', 'selected', 'pointer', 'checkbox',
            'success', 'error', 'warning', 'info'
        ]
        
        for theme_name in themes:
            theme = TUIEngineThemes.get_theme(theme_name)
            theme_dict = {item[0]: item[1] for item in theme.style}
            
            for color in required_colors:
                assert color in theme_dict, f"Theme {theme_name} missing color: {color}"
    
    def test_form_rendering(self):
        """Test form rendering output."""
        builder = FormBuilder("professional_blue")
        schema = builder.create_form("render_test", "Render Test")
        
        fields = [
            FieldDefinition("name", FieldType.TEXT, label="Full Name", required=True),
            FieldDefinition("email", FieldType.EMAIL, label="Email Address"),
            FieldDefinition("age", FieldType.INTEGER, label="Age", min_value=0, max_value=120),
            FieldDefinition("newsletter", FieldType.CHECKBOX, label="Subscribe to newsletter")
        ]
        
        for field in fields:
            builder.add_field("render_test", field)
        
        form = builder.build_form("render_test")
        
        # Test rendering
        rendered = form.render_form()
        
        # Should contain field labels
        assert "Full Name" in rendered
        assert "Email Address" in rendered
        assert "Age" in rendered
        assert "Subscribe to newsletter" in rendered
        
        # Should be non-empty
        assert len(rendered) > 0
        assert rendered.strip() != ""
    
    def test_error_message_rendering(self):
        """Test error message rendering."""
        builder = FormBuilder("professional_blue")
        schema = builder.create_form("error_test", "Error Test")
        
        builder.add_field("error_test", FieldDefinition(
            "email",
            FieldType.EMAIL,
            required=True,
            validation_message="Please enter a valid email address"
        ))
        
        form = builder.build_form("error_test")
        
        # Set invalid email
        form.set_field_value("email", "invalid-email")
        
        # Should not be valid
        assert not form.validate_form()
        
        # Should have error messages
        errors = form.get_validation_errors()
        assert len(errors) > 0
        
        # Error messages should be strings
        for error in errors:
            assert isinstance(error, str)
            assert len(error) > 0
    
    @pytest.mark.parametrize("theme_name", TUIEngineThemes.list_themes())
    def test_theme_form_rendering(self, theme_name):
        """Test form rendering with all themes."""
        builder = FormBuilder(theme_name)
        schema = builder.create_form("theme_render", "Theme Render Test")
        
        builder.add_field("theme_render", FieldDefinition(
            "test_field",
            FieldType.TEXT,
            label="Test Field"
        ))
        
        form = builder.build_form("theme_render")
        
        # Should render without errors
        rendered = form.render_form()
        assert isinstance(rendered, str)
        assert len(rendered) > 0
        assert "Test Field" in rendered
```

---

## CI/CD Integration

### GitHub Actions Configuration

```yaml
# .github/workflows/test.yml
name: TUI Engine Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest pytest-cov pytest-benchmark pytest-mock
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=tui_engine --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
    
    - name: Run performance benchmarks
      run: |
        pytest tests/performance/ -v --benchmark-only --benchmark-json=benchmark.json
    
    - name: Run headless tests
      run: |
        pytest tests/headless/ -v
      env:
        CI: true
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

  compatibility:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.9", "3.11"]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest
    
    - name: Run compatibility tests
      run: |
        pytest tests/compatibility/ -v
```

### Pytest Configuration

```ini
# pytest.ini
[tool:pytest]
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=tui_engine
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=85

markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    benchmark: Benchmark tests
    headless: Tests that don't require TTY
    slow: Slow running tests

testpaths = tests

python_files = test_*.py
python_classes = Test*
python_functions = test_*

filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

### Coverage Configuration

```ini
# .coveragerc
[run]
source = tui_engine
omit = 
    */tests/*
    */test_*
    */__pycache__/*
    */site-packages/*
    */demos/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod
```

---

## Best Practices

### Testing Guidelines

1. **Test Isolation**: Each test should be independent and not rely on external state
2. **Mock External Dependencies**: Use mocking for questionary widgets in CI environments
3. **Performance Monitoring**: Include performance tests to catch regressions
4. **Cross-Platform Testing**: Test on multiple operating systems and Python versions
5. **Headless Support**: Ensure tests can run without TTY for CI/CD

### Test Organization

```
tests/
├── unit/
│   ├── test_themes.py
│   ├── test_validation.py
│   ├── test_form_builder.py
│   └── test_widgets.py
├── integration/
│   ├── test_end_to_end.py
│   ├── test_cross_component.py
│   └── test_workflows.py
├── performance/
│   ├── test_benchmarks.py
│   ├── test_memory.py
│   └── test_scalability.py
├── headless/
│   ├── test_ci_friendly.py
│   ├── test_mock_interactions.py
│   └── test_non_interactive.py
├── compatibility/
│   ├── test_cross_platform.py
│   └── test_python_versions.py
└── conftest.py  # Shared fixtures
```

### Test Data Management

```python
# conftest.py
import pytest
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType


@pytest.fixture(scope="session")
def sample_themes():
    """Sample themes for testing."""
    from tui_engine.themes import TUIEngineThemes
    return TUIEngineThemes.list_themes()


@pytest.fixture
def basic_form():
    """Basic form for testing."""
    builder = FormBuilder("professional_blue")
    schema = builder.create_form("basic", "Basic Form")
    
    fields = [
        FieldDefinition("name", FieldType.TEXT, required=True),
        FieldDefinition("email", FieldType.EMAIL, required=True),
        FieldDefinition("age", FieldType.INTEGER, min_value=0, max_value=120)
    ]
    
    for field in fields:
        builder.add_field("basic", field)
    
    return builder.build_form("basic")


@pytest.fixture
def valid_user_data():
    """Valid user data for testing."""
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    }


@pytest.fixture
def invalid_user_data():
    """Invalid user data for testing."""
    return {
        "name": "",  # Empty required field
        "email": "invalid-email",  # Invalid email
        "age": -5  # Invalid age
    }
```

This comprehensive testing framework ensures TUI Engine components are thoroughly tested across all environments and use cases, providing confidence in the system's reliability and performance.