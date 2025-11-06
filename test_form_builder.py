#!/usr/bin/env python3
"""
Test suite for FormBuilder System

This test suite validates all FormBuilder functionality including:
- Schema creation and management
- Field definitions and types
- Conditional logic
- Dynamic form generation
- Validation integration
- Real-world form scenarios
- Performance optimization
"""

import sys
import time
import traceback
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, '/home/vpsuser/vpsuser/projects/tui-engine/src')

from tui_engine.form_builder import (
    FormBuilder, FieldDefinition, FieldType, FormSchema, FormSection,
    DynamicForm, ConditionalLogic, FormRenderer,
    create_simple_form, create_registration_form, create_contact_form, create_settings_form
)
from tui_engine.validation import ValidationLevel, ValidationResult


def test_field_definition():
    """Test field definition creation and configuration."""
    print("🧪 Testing FieldDefinition...")
    
    # Test basic field creation
    print("  📝 Basic field creation tests:")
    field = FieldDefinition(
        name="username",
        type=FieldType.TEXT,
        required=True,
        min_length=3,
        max_length=20
    )
    assert field.name == "username"
    assert field.type == FieldType.TEXT
    assert field.required == True
    assert field.label == "Username"  # Auto-generated
    print("    ✅ Basic field created correctly")
    
    # Test field with custom label
    print("  🏷️ Custom label tests:")
    field_custom = FieldDefinition(
        name="user_email",
        type=FieldType.EMAIL,
        label="Email Address",
        description="Your primary email address"
    )
    assert field_custom.label == "Email Address"
    assert field_custom.description == "Your primary email address"
    print("    ✅ Custom label and description work")
    
    # Test select field with choices
    print("  📋 Select field tests:")
    select_field = FieldDefinition(
        name="country",
        type=FieldType.SELECT,
        choices={"us": "United States", "ca": "Canada", "uk": "United Kingdom"},
        required=True
    )
    assert select_field.choices["us"] == "United States"
    assert len(select_field.choices) == 3
    print("    ✅ Select field with choices works")
    
    # Test number field with range
    print("  🔢 Number field tests:")
    number_field = FieldDefinition(
        name="age",
        type=FieldType.NUMBER,
        min_value=18,
        max_value=120,
        required=True
    )
    assert number_field.min_value == 18
    assert number_field.max_value == 120
    print("    ✅ Number field with range works")
    
    # Test conditional field
    print("  🔗 Conditional field tests:")
    conditional_field = FieldDefinition(
        name="other_details",
        type=FieldType.TEXT,
        condition={"field": "category", "operator": "equals", "value": "other"}
    )
    assert conditional_field.condition["field"] == "category"
    print("    ✅ Conditional field works")
    
    print("✅ FieldDefinition tests passed!")


def test_form_schema():
    """Test form schema creation and management."""
    print("🧪 Testing FormSchema...")
    
    # Test basic schema creation
    print("  📋 Basic schema creation tests:")
    schema = FormSchema(
        name="test_form",
        title="Test Form",
        description="A test form",
        theme="professional_blue"
    )
    assert schema.name == "test_form"
    assert schema.title == "Test Form"
    assert schema.theme == "professional_blue"
    assert schema.created_at is not None
    print("    ✅ Basic schema created correctly")
    
    # Test adding fields
    print("  📝 Field addition tests:")
    field1 = FieldDefinition("username", FieldType.TEXT, required=True)
    field2 = FieldDefinition("email", FieldType.EMAIL, required=True)
    
    schema.fields = [field1, field2]
    assert len(schema.fields) == 2
    assert schema.fields[0].name == "username"
    assert schema.fields[1].type == FieldType.EMAIL
    print("    ✅ Fields added correctly")
    
    # Test adding sections
    print("  📂 Section addition tests:")
    section = FormSection(
        name="personal_info",
        title="Personal Information",
        fields=["username", "email"]
    )
    schema.sections = [section]
    assert len(schema.sections) == 1
    assert schema.sections[0].title == "Personal Information"
    print("    ✅ Sections added correctly")
    
    print("✅ FormSchema tests passed!")


def test_conditional_logic():
    """Test conditional field logic."""
    print("🧪 Testing ConditionalLogic...")
    
    logic = ConditionalLogic()
    
    # Test basic conditions
    print("  🔍 Basic condition tests:")
    form_data = {"category": "personal", "age": "25", "country": "us"}
    
    # Equals condition
    condition1 = {"field": "category", "operator": "equals", "value": "personal"}
    assert logic.evaluate_condition(condition1, form_data) == True
    print("    ✅ Equals condition works")
    
    # Not equals condition
    condition2 = {"field": "category", "operator": "not_equals", "value": "business"}
    assert logic.evaluate_condition(condition2, form_data) == True
    print("    ✅ Not equals condition works")
    
    # Greater than condition
    condition3 = {"field": "age", "operator": "greater_than", "value": "18"}
    assert logic.evaluate_condition(condition3, form_data) == True
    print("    ✅ Greater than condition works")
    
    # Less than condition
    condition4 = {"field": "age", "operator": "less_than", "value": "30"}
    assert logic.evaluate_condition(condition4, form_data) == True
    print("    ✅ Less than condition works")
    
    # In condition
    condition5 = {"field": "country", "operator": "in", "value": ["us", "ca", "uk"]}
    assert logic.evaluate_condition(condition5, form_data) == True
    print("    ✅ In condition works")
    
    # Empty condition
    empty_data = {"category": "", "description": "   "}
    condition6 = {"field": "category", "operator": "empty"}
    assert logic.evaluate_condition(condition6, empty_data) == True
    print("    ✅ Empty condition works")
    
    # Not empty condition
    condition7 = {"field": "country", "operator": "not_empty"}
    assert logic.evaluate_condition(condition7, form_data) == True
    print("    ✅ Not empty condition works")
    
    # Contains condition
    condition8 = {"field": "category", "operator": "contains", "value": "person"}
    assert logic.evaluate_condition(condition8, form_data) == True
    print("    ✅ Contains condition works")
    
    print("✅ ConditionalLogic tests passed!")


def test_form_renderer():
    """Test form renderer functionality."""
    print("🧪 Testing FormRenderer...")
    
    renderer = FormRenderer("professional_blue")
    
    # Test widget creation for different field types
    print("  🎨 Widget creation tests:")
    form_data = {}
    
    # Text field
    text_field = FieldDefinition("name", FieldType.TEXT, required=True)
    text_widget = renderer.create_widget(text_field, form_data)
    assert text_widget is not None
    print("    ✅ Text widget created")
    
    # Email field
    email_field = FieldDefinition("email", FieldType.EMAIL, required=True)
    email_widget = renderer.create_widget(email_field, form_data)
    assert email_widget is not None
    print("    ✅ Email widget created")
    
    # Select field
    select_field = FieldDefinition(
        "country", 
        FieldType.SELECT, 
        choices={"us": "United States", "ca": "Canada"}
    )
    select_widget = renderer.create_widget(select_field, form_data)
    assert select_widget is not None
    print("    ✅ Select widget created")
    
    # Number field
    number_field = FieldDefinition(
        "age", 
        FieldType.NUMBER, 
        min_value=18, 
        max_value=120
    )
    number_widget = renderer.create_widget(number_field, form_data)
    assert number_widget is not None
    print("    ✅ Number widget created")
    
    # Checkbox field
    checkbox_field = FieldDefinition("agree", FieldType.CHECKBOX)
    checkbox_widget = renderer.create_widget(checkbox_field, form_data)
    assert checkbox_widget is not None
    print("    ✅ Checkbox widget created")
    
    # Password field
    password_field = FieldDefinition("password", FieldType.PASSWORD, min_length=8)
    password_widget = renderer.create_widget(password_field, form_data)
    assert password_widget is not None
    print("    ✅ Password widget created")
    
    print("✅ FormRenderer tests passed!")


def test_form_builder():
    """Test form builder functionality."""
    print("🧪 Testing FormBuilder...")
    
    builder = FormBuilder("professional_blue")
    
    # Test form creation
    print("  🏗️ Form creation tests:")
    schema = builder.create_form("test_form", "Test Form")
    assert schema.name == "test_form"
    assert schema.title == "Test Form"
    assert "test_form" in builder.forms
    print("    ✅ Form created and stored")
    
    # Test field addition
    print("  📝 Field addition tests:")
    field1 = FieldDefinition("username", FieldType.TEXT, required=True)
    field2 = FieldDefinition("email", FieldType.EMAIL, required=True)
    
    builder.add_field("test_form", field1)
    builder.add_field("test_form", field2)
    
    assert len(builder.forms["test_form"].fields) == 2
    print("    ✅ Fields added successfully")
    
    # Test section addition
    print("  📂 Section addition tests:")
    section = FormSection("personal", "Personal Information", fields=["username", "email"])
    builder.add_section("test_form", section)
    
    assert len(builder.forms["test_form"].sections) == 1
    print("    ✅ Section added successfully")
    
    # Test form building
    print("  🔨 Form building tests:")
    dynamic_form = builder.build_form("test_form")
    assert isinstance(dynamic_form, DynamicForm)
    assert dynamic_form.schema.name == "test_form"
    print("    ✅ Dynamic form built successfully")
    
    # Test form listing
    print("  📋 Form listing tests:")
    forms = builder.list_forms()
    assert "test_form" in forms
    print("    ✅ Form listing works")
    
    # Test form info
    print("  ℹ️ Form info tests:")
    info = builder.get_form_info("test_form")
    assert info["name"] == "test_form"
    assert info["field_count"] == 2
    assert info["section_count"] == 1
    print("    ✅ Form info retrieval works")
    
    print("✅ FormBuilder tests passed!")


def test_dynamic_form():
    """Test dynamic form functionality."""
    print("🧪 Testing DynamicForm...")
    
    builder = FormBuilder()
    
    # Create a test form
    schema = builder.create_form("user_form", "User Registration")
    
    # Add fields
    fields = [
        FieldDefinition("username", FieldType.TEXT, required=True, min_length=3),
        FieldDefinition("email", FieldType.EMAIL, required=True),
        FieldDefinition("age", FieldType.NUMBER, min_value=18, max_value=120),
        FieldDefinition("country", FieldType.SELECT, choices={"us": "USA", "ca": "Canada"}),
        FieldDefinition("newsletter", FieldType.CHECKBOX, label="Subscribe to newsletter"),
        FieldDefinition("bio", FieldType.TEXT, condition={"field": "age", "operator": "greater_than", "value": "21"})
    ]
    
    for field in fields:
        builder.add_field("user_form", field)
    
    form = builder.build_form("user_form")
    
    # Test initial state
    print("  🚀 Initial state tests:")
    assert len(form.visible_fields) > 0
    assert not form.submitted
    print("    ✅ Initial state correct")
    
    # Test field value setting
    print("  📝 Field value tests:")
    result = form.set_field_value("username", "testuser")
    assert form.get_field_value("username") == "testuser"
    print("    ✅ Field value setting works")
    
    # Test conditional field visibility
    print("  👁️ Conditional visibility tests:")
    initial_visible = len(form.visible_fields)
    form.set_field_value("age", "25")  # Should show bio field
    new_visible = len(form.visible_fields)
    assert new_visible >= initial_visible  # Bio field should be visible now
    print("    ✅ Conditional visibility works")
    
    # Test form validation
    print("  ✅ Form validation tests:")
    # Set valid values
    form.set_field_value("username", "testuser")
    form.set_field_value("email", "test@example.com")
    form.set_field_value("age", "25")
    form.set_field_value("country", "us")
    
    is_valid = form.validate_form()
    assert is_valid == True
    print("    ✅ Valid form passes validation")
    
    # Test invalid form
    form.set_field_value("email", "invalid-email")
    is_valid = form.validate_form()
    assert is_valid == False
    print("    ✅ Invalid form fails validation")
    
    # Test error retrieval
    print("  ❌ Error retrieval tests:")
    errors = form.get_validation_errors()
    assert len(errors) > 0  # Should have email error
    print("    ✅ Error retrieval works")
    
    # Test form rendering
    print("  🎨 Form rendering tests:")
    rendered = form.render_form()
    assert "User Registration" in rendered
    assert "username" in rendered or "Username" in rendered
    print("    ✅ Form rendering works")
    
    # Test form submission (valid form)
    print("  📤 Form submission tests:")
    form.set_field_value("email", "test@example.com")  # Fix email
    result = form.submit()
    assert result["success"] == True
    assert "data" in result
    print("    ✅ Valid form submission works")
    
    # Test form reset
    print("  🔄 Form reset tests:")
    form.reset()
    assert len(form.data) == 0
    assert not form.submitted
    print("    ✅ Form reset works")
    
    # Test data export/import
    print("  💾 Data export/import tests:")
    form.set_field_value("username", "testuser2")
    form.set_field_value("email", "test2@example.com")
    
    # Export BEFORE reset
    exported = form.export_data()
    assert "data" in exported
    assert exported["data"]["username"] == "testuser2"
    
    # THEN reset
    form.reset()
    
    # THEN import
    success = form.import_data(exported)
    assert success == True
    assert form.get_field_value("username") == "testuser2"
    print("    ✅ Data export/import works")
    
    print("✅ DynamicForm tests passed!")


def test_schema_serialization():
    """Test schema save/load functionality."""
    print("🧪 Testing schema serialization...")
    
    builder = FormBuilder()
    
    # Create a complex form
    schema = builder.create_form("complex_form", "Complex Form", description="A complex test form")
    
    # Add various field types
    fields = [
        FieldDefinition("text_field", FieldType.TEXT, required=True, min_length=2, max_length=50),
        FieldDefinition("email_field", FieldType.EMAIL, required=True),
        FieldDefinition("number_field", FieldType.NUMBER, min_value=0, max_value=100),
        FieldDefinition("select_field", FieldType.SELECT, choices={"a": "Option A", "b": "Option B"}),
        FieldDefinition("checkbox_field", FieldType.CHECKBOX),
        FieldDefinition("conditional_field", FieldType.TEXT, 
                       condition={"field": "checkbox_field", "operator": "equals", "value": True})
    ]
    
    for field in fields:
        builder.add_field("complex_form", field)
    
    # Add sections
    section1 = FormSection("basic", "Basic Information", fields=["text_field", "email_field"])
    section2 = FormSection("advanced", "Advanced Options", fields=["number_field", "select_field"])
    builder.add_section("complex_form", section1)
    builder.add_section("complex_form", section2)
    
    # Test schema export
    print("  💾 Schema export tests:")
    json_data = builder.save_schema("complex_form")
    assert "complex_form" in json_data
    assert "text_field" in json_data
    assert "Basic Information" in json_data
    print("    ✅ Schema exported to JSON")
    
    # Test schema import
    print("  📥 Schema import tests:")
    new_builder = FormBuilder()
    loaded_schema = new_builder.load_schema(json_data)
    
    assert loaded_schema.name == "complex_form"
    assert len(loaded_schema.fields) == 6
    assert len(loaded_schema.sections) == 2
    print("    ✅ Schema imported from JSON")
    
    # Verify loaded form works
    print("  ✅ Loaded form functionality tests:")
    dynamic_form = new_builder.build_form("complex_form")
    dynamic_form.set_field_value("text_field", "test")
    dynamic_form.set_field_value("email_field", "test@example.com")
    dynamic_form.set_field_value("number_field", 50)  # Valid number within range 0-100
    
    is_valid = dynamic_form.validate_form()
    assert is_valid == True
    print("    ✅ Loaded form works correctly")
    
    print("✅ Schema serialization tests passed!")


def test_convenience_functions():
    """Test convenience form creation functions."""
    print("🧪 Testing convenience functions...")
    
    # Test simple form creation
    print("  🏗️ Simple form creation tests:")
    simple_form = create_simple_form(
        "Test Form",
        [
            {"name": "name", "type": "text", "required": True},
            {"name": "email", "type": "email", "required": True},
            {"name": "age", "type": "number", "min_value": 18}
        ]
    )
    assert simple_form.schema.title == "Test Form"
    assert len(simple_form.schema.fields) == 3
    print("    ✅ Simple form created")
    
    # Test registration form
    print("  👤 Registration form tests:")
    reg_form = create_registration_form()
    assert "Registration" in reg_form.schema.title
    assert len(reg_form.schema.fields) >= 5  # Should have multiple fields
    print("    ✅ Registration form created")
    
    # Test contact form
    print("  📞 Contact form tests:")
    contact_form = create_contact_form()
    assert "Contact" in contact_form.schema.title
    assert len(contact_form.schema.fields) >= 4
    print("    ✅ Contact form created")
    
    # Test settings form
    print("  ⚙️ Settings form tests:")
    settings_form = create_settings_form()
    assert "Settings" in settings_form.schema.title
    assert len(settings_form.schema.fields) >= 5
    print("    ✅ Settings form created")
    
    print("✅ Convenience function tests passed!")


def test_real_world_scenarios():
    """Test real-world form scenarios."""
    print("🧪 Testing real-world scenarios...")
    
    # Scenario 1: Multi-step user onboarding
    print("  👤 User onboarding scenario:")
    builder = FormBuilder()
    schema = builder.create_form("onboarding", "User Onboarding", multi_step=True)
    
    # Step 1: Basic info
    basic_fields = [
        FieldDefinition("first_name", FieldType.TEXT, required=True),
        FieldDefinition("last_name", FieldType.TEXT, required=True),
        FieldDefinition("email", FieldType.EMAIL, required=True),
    ]
    
    # Step 2: Details
    detail_fields = [
        FieldDefinition("company", FieldType.TEXT),
        FieldDefinition("role", FieldType.SELECT, choices={"dev": "Developer", "mgr": "Manager", "other": "Other"}),
        FieldDefinition("experience", FieldType.NUMBER, min_value=0, max_value=50),
    ]
    
    # Step 3: Preferences
    pref_fields = [
        FieldDefinition("newsletter", FieldType.CHECKBOX, label="Subscribe to newsletter"),
        FieldDefinition("theme", FieldType.SELECT, choices={"light": "Light", "dark": "Dark"}),
    ]
    
    all_fields = basic_fields + detail_fields + pref_fields
    for field in all_fields:
        builder.add_field("onboarding", field)
    
    form = builder.build_form("onboarding")
    
    # Test step-by-step completion
    form.set_field_value("first_name", "John")
    form.set_field_value("last_name", "Doe")
    form.set_field_value("email", "john.doe@example.com")
    form.set_field_value("company", "Tech Corp")
    
    assert form.get_field_value("first_name") == "John"
    print("    ✅ Multi-step onboarding form works")
    
    # Scenario 2: Dynamic survey form
    print("  📊 Dynamic survey scenario:")
    survey_builder = FormBuilder()
    survey_schema = survey_builder.create_form("survey", "Customer Survey")
    
    # Add conditional questions
    survey_fields = [
        FieldDefinition("satisfaction", FieldType.SELECT, required=True,
                       choices={"1": "Very Unsatisfied", "2": "Unsatisfied", "3": "Neutral", "4": "Satisfied", "5": "Very Satisfied"}),
        FieldDefinition("improvement_needed", FieldType.CHECKBOX, 
                       condition={"field": "satisfaction", "operator": "in", "value": ["1", "2", "3"]},
                       label="Would you like to suggest improvements?"),
        FieldDefinition("improvements", FieldType.EDITOR, 
                       condition={"field": "improvement_needed", "operator": "equals", "value": True},
                       required=True, language="text"),
        FieldDefinition("recommend", FieldType.SELECT,
                       condition={"field": "satisfaction", "operator": "in", "value": ["4", "5"]},
                       choices={"yes": "Yes", "no": "No", "maybe": "Maybe"}),
    ]
    
    for field in survey_fields:
        survey_builder.add_field("survey", field)
    
    survey_form = survey_builder.build_form("survey")
    
    # Test conditional logic
    initial_visible = len(survey_form.visible_fields)
    survey_form.set_field_value("satisfaction", "2")  # Unsatisfied
    survey_form.set_field_value("improvement_needed", True)
    
    # Should show improvements field
    final_visible = len(survey_form.visible_fields)
    assert final_visible > initial_visible
    print("    ✅ Dynamic survey form works")
    
    # Scenario 3: Configuration form with validation
    print("  ⚙️ Configuration scenario:")
    config_form = create_settings_form()
    
    # Set valid configuration
    config_form.set_field_value("app_name", "My Application")
    config_form.set_field_value("theme", "professional_blue")
    config_form.set_field_value("auto_save", True)
    config_form.set_field_value("backup_interval", 10)
    config_form.set_field_value("log_level", "info")
    config_form.set_field_value("data_directory", "/home/user/data")
    config_form.set_field_value("language", "en")
    
    is_valid = config_form.validate_form()
    assert is_valid == True
    
    # Test invalid configuration
    config_form.set_field_value("backup_interval", 100)  # Out of range
    is_valid = config_form.validate_form()
    assert is_valid == False
    print("    ✅ Configuration form validation works")
    
    print("✅ Real-world scenario tests passed!")


def test_performance_and_optimization():
    """Test performance characteristics."""
    print("🧪 Testing performance and optimization...")
    
    # Test large form creation
    print("  🏗️ Large form creation tests:")
    start_time = time.time()
    
    builder = FormBuilder()
    schema = builder.create_form("large_form", "Large Form")
    
    # Create 100 fields
    for i in range(100):
        field = FieldDefinition(
            f"field_{i}",
            FieldType.TEXT,
            required=i % 5 == 0,  # Every 5th field required
            min_length=2,
            max_length=50
        )
        builder.add_field("large_form", field)
    
    form = builder.build_form("large_form")
    creation_time = time.time() - start_time
    
    assert len(form.schema.fields) == 100
    print(f"    ✅ Large form (100 fields) created in {creation_time:.3f}s")
    
    # Test bulk data setting
    print("  📝 Bulk data setting tests:")
    start_time = time.time()
    
    for i in range(100):
        form.set_field_value(f"field_{i}", f"value_{i}")
    
    setting_time = time.time() - start_time
    print(f"    ✅ 100 field values set in {setting_time:.3f}s")
    
    # Test validation performance
    print("  ✅ Validation performance tests:")
    start_time = time.time()
    
    is_valid = form.validate_form()
    validation_time = time.time() - start_time
    
    assert is_valid == True
    print(f"    ✅ Large form validated in {validation_time:.3f}s")
    
    # Test conditional logic performance
    print("  🔍 Conditional logic performance tests:")
    conditional_builder = FormBuilder()
    conditional_schema = conditional_builder.create_form("conditional_form", "Conditional Form")
    
    # Create fields with complex conditions
    base_field = FieldDefinition("trigger", FieldType.SELECT, choices={"a": "A", "b": "B", "c": "C"})
    conditional_builder.add_field("conditional_form", base_field)
    
    for i in range(50):
        conditional_field = FieldDefinition(
            f"conditional_{i}",
            FieldType.TEXT,
            condition={"field": "trigger", "operator": "equals", "value": "a" if i % 2 == 0 else "b"}
        )
        conditional_builder.add_field("conditional_form", conditional_field)
    
    conditional_form = conditional_builder.build_form("conditional_form")
    
    start_time = time.time()
    conditional_form.set_field_value("trigger", "a")  # Should trigger visibility updates
    conditional_time = time.time() - start_time
    
    print(f"    ✅ Conditional logic for 50 fields processed in {conditional_time:.3f}s")
    
    # Test schema serialization performance
    print("  💾 Serialization performance tests:")
    start_time = time.time()
    json_data = builder.save_schema("large_form")
    serialization_time = time.time() - start_time
    
    assert len(json_data) > 1000  # Should be substantial JSON
    print(f"    ✅ Large schema serialized in {serialization_time:.3f}s")
    
    start_time = time.time()
    new_builder = FormBuilder()
    loaded_schema = new_builder.load_schema(json_data)
    deserialization_time = time.time() - start_time
    
    assert len(loaded_schema.fields) == 100
    print(f"    ✅ Large schema deserialized in {deserialization_time:.3f}s")
    
    print("✅ Performance and optimization tests passed!")


def test_error_handling_and_edge_cases():
    """Test error handling and edge cases."""
    print("🧪 Testing error handling and edge cases...")
    
    builder = FormBuilder()
    
    # Test non-existent form access
    print("  🚫 Non-existent form tests:")
    try:
        builder.build_form("non_existent")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found" in str(e)
    print("    ✅ Non-existent form properly handled")
    
    # Test invalid field addition
    print("  ❌ Invalid field addition tests:")
    try:
        invalid_field = FieldDefinition("test", FieldType.TEXT)
        builder.add_field("non_existent", invalid_field)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found" in str(e)
    print("    ✅ Invalid field addition properly handled")
    
    # Test malformed schema loading
    print("  📄 Malformed schema tests:")
    try:
        builder.load_schema("invalid json")
        assert False, "Should have raised exception"
    except Exception:
        pass  # Expected
    print("    ✅ Malformed schema properly handled")
    
    # Test circular dependencies
    print("  🔄 Circular dependency tests:")
    schema = builder.create_form("circular_test", "Circular Test")
    
    field1 = FieldDefinition(
        "field1", 
        FieldType.TEXT,
        condition={"field": "field2", "operator": "not_empty"}
    )
    field2 = FieldDefinition(
        "field2", 
        FieldType.TEXT,
        condition={"field": "field1", "operator": "not_empty"}
    )
    
    builder.add_field("circular_test", field1)
    builder.add_field("circular_test", field2)
    
    form = builder.build_form("circular_test")
    # Should not crash, even with circular dependencies
    form.set_field_value("field1", "test")
    print("    ✅ Circular dependencies handled gracefully")
    
    # Test extreme values
    print("  🌊 Extreme value tests:")
    extreme_form = create_simple_form(
        "Extreme Test",
        [
            {"name": "long_text", "type": "text", "max_length": 10},
            {"name": "range_number", "type": "number", "min_value": 0, "max_value": 10}
        ]
    )
    
    # Test very long text
    extreme_form.set_field_value("long_text", "a" * 100)  # Way over limit
    is_valid = extreme_form.validate_form()
    assert is_valid == False  # Should fail validation
    
    # Test out of range number
    extreme_form.set_field_value("long_text", "ok")  # Fix text
    extreme_form.set_field_value("range_number", 1000)  # Out of range
    is_valid = extreme_form.validate_form()
    assert is_valid == False  # Should fail validation
    print("    ✅ Extreme values properly validated")
    
    # Test empty form operations
    print("  🗳️ Empty form tests:")
    empty_schema = builder.create_form("empty_form", "Empty Form")
    empty_form = builder.build_form("empty_form")
    
    # Should work with no fields
    is_valid = empty_form.validate_form()
    assert is_valid == True  # Empty form is valid
    
    result = empty_form.submit()
    assert result["success"] == True
    print("    ✅ Empty form operations work")
    
    # Test Unicode and special characters
    print("  🌍 Unicode tests:")
    unicode_form = create_simple_form(
        "Unicode Test",
        [
            {"name": "unicode_name", "type": "text", "required": True},
            {"name": "emoji_text", "type": "text"}
        ]
    )
    
    unicode_form.set_field_value("unicode_name", "José García-Müller")
    unicode_form.set_field_value("emoji_text", "Hello 👋 World 🌍!")
    
    is_valid = unicode_form.validate_form()
    assert is_valid == True
    
    # Test rendering with Unicode
    rendered = unicode_form.render_form()
    assert "José" in rendered
    assert "👋" in rendered
    print("    ✅ Unicode handling works correctly")
    
    print("✅ Error handling and edge case tests passed!")


def main():
    """Run all FormBuilder tests."""
    print("🚀 Starting FormBuilder test suite...")
    print()
    
    try:
        test_field_definition()
        print()
        
        test_form_schema()
        print()
        
        test_conditional_logic()
        print()
        
        test_form_renderer()
        print()
        
        test_form_builder()
        print()
        
        test_dynamic_form()
        print()
        
        test_schema_serialization()
        print()
        
        test_convenience_functions()
        print()
        
        test_real_world_scenarios()
        print()
        
        test_performance_and_optimization()
        print()
        
        test_error_handling_and_edge_cases()
        print()
        
        print("📊 Test Results: 11/11 tests passed")
        print("🎉 All FormBuilder tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print(f"Traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()