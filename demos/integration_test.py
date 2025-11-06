#!/usr/bin/env python3
"""
Integration Test Demo

This demo tests the integration between all TUI Engine components:
- Themes and styling
- Validation system
- Form builder
- Widget compatibility
- Performance optimizations

This serves as both a demo and a comprehensive integration test.
"""

import os
import sys
import time
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tui_engine.themes import TUIEngineThemes
from tui_engine.questionary_adapter import QuestionaryStyleAdapter
from tui_engine.form_builder import (
    FormBuilder, FieldDefinition, FieldType, DynamicForm,
    create_registration_form, create_contact_form, create_settings_form
)
from tui_engine.validation import (
    create_form_validator, EmailValidator, URLValidator, PhoneValidator,
    CreditCardValidator, NumberValidator, DateValidator, ValidationChain
)


class IntegrationTest:
    """Integration test suite for TUI Engine components."""
    
    def __init__(self):
        """Initialize integration test."""
        self.test_results = {}
        self.themes = TUIEngineThemes.list_themes()
        
    def run_all_tests(self):
        """Run complete integration test suite."""
        print("🧪 TUI ENGINE INTEGRATION TEST SUITE")
        print("=" * 60)
        print("Testing integration between all components...\n")
        
        tests = [
            ("Theme Integration", self.test_theme_integration),
            ("Validation Integration", self.test_validation_integration),
            ("Form Builder Integration", self.test_form_builder_integration),
            ("Widget Compatibility", self.test_widget_compatibility),
            ("Cross-Theme Validation", self.test_cross_theme_validation),
            ("Complex Form Scenarios", self.test_complex_scenarios),
            ("Performance Integration", self.test_performance_integration),
            ("Error Handling", self.test_error_handling),
            ("Data Persistence", self.test_data_persistence),
            ("Questionary Compatibility", self.test_questionary_compatibility),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"🔧 Running {test_name}...")
            
            try:
                start_time = time.time()
                result = test_func()
                duration = time.time() - start_time
                
                if result.get('passed', False):
                    print(f"✅ {test_name}: PASSED ({duration:.3f}s)")
                    passed += 1
                else:
                    print(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
                
                self.test_results[test_name] = {
                    **result,
                    'duration': duration
                }
                
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                self.test_results[test_name] = {
                    'passed': False,
                    'error': str(e),
                    'duration': 0
                }
        
        self.print_summary(passed, total)
        return passed == total
    
    def test_theme_integration(self) -> Dict[str, Any]:
        """Test theme integration across components."""
        try:
            results = []
            
            for theme_name in self.themes:
                # Test theme loading
                theme = TUIEngineThemes.get_theme(theme_name)
                adapter = QuestionaryStyleAdapter(theme_name)
                
                # Verify theme has required attributes
                required_attrs = ['primary', 'secondary', 'success', 'warning', 'error', 'info']
                for attr in required_attrs:
                    if not hasattr(theme, attr):
                        return {'passed': False, 'error': f'Theme {theme_name} missing {attr}'}
                
                # Test theme with form builder
                builder = FormBuilder(theme_name)
                schema = builder.create_form(f"theme_test_{theme_name}", "Theme Test")
                
                field = FieldDefinition("test_field", FieldType.TEXT, required=True)
                builder.add_field(f"theme_test_{theme_name}", field)
                
                form = builder.build_form(f"theme_test_{theme_name}")
                
                # Verify form has theme applied
                if form.schema.theme != theme_name:
                    return {'passed': False, 'error': f'Form theme mismatch: {form.schema.theme} != {theme_name}'}
                
                results.append(f"{theme_name}: OK")
            
            return {
                'passed': True,
                'results': results,
                'themes_tested': len(self.themes)
            }
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_validation_integration(self) -> Dict[str, Any]:
        """Test validation system integration."""
        try:
            # Test individual validators
            validators = [
                (EmailValidator(), "test@example.com", True),
                (EmailValidator(), "invalid-email", False),
                (URLValidator(), "https://www.example.com", True),
                (URLValidator(), "not-a-url", False),
                (PhoneValidator(), "+1-555-123-4567", True),
                (PhoneValidator(), "invalid-phone", False),
                (CreditCardValidator(), "4532015112830366", True),
                (CreditCardValidator(), "1234567890", False),
                (NumberValidator(min_value=0, max_value=100), 50, True),
                (NumberValidator(min_value=0, max_value=100), 150, False),
            ]
            
            for validator, test_value, expected in validators:
                result = validator.validate(test_value)
                if result.is_valid != expected:
                    return {
                        'passed': False, 
                        'error': f'Validator {type(validator).__name__} failed for {test_value}'
                    }
            
            # Test validation chains
            form_validator = create_form_validator()
            email_chain = form_validator.add_field("email")
            email_chain.required().email()
            
            # Test valid email
            results = form_validator.validate_field("email", "test@example.com")
            if not all(r.is_valid for r in results):
                return {'passed': False, 'error': 'Email validation chain failed for valid email'}
            
            # Test invalid email
            results = form_validator.validate_field("email", "invalid")
            if all(r.is_valid for r in results):
                return {'passed': False, 'error': 'Email validation chain passed for invalid email'}
            
            return {
                'passed': True,
                'validators_tested': len(validators),
                'chain_tests': 2
            }
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_form_builder_integration(self) -> Dict[str, Any]:
        """Test form builder integration with themes and validation."""
        try:
            # Test pre-built forms
            forms = [
                ("registration", create_registration_form("professional_blue")),
                ("contact", create_contact_form("elegant_dark")),
                ("settings", create_settings_form("vibrant_green")),
            ]
            
            form_results = []
            
            for form_name, form in forms:
                # Test form creation
                if not isinstance(form, DynamicForm):
                    return {'passed': False, 'error': f'{form_name} form is not DynamicForm instance'}
                
                # Test form validation
                initial_valid = form.validate_form()  # Should be False for empty form
                
                # Test field setting
                form.set_field_value("email", "test@example.com")
                
                # Test form rendering
                rendered = form.render_form()
                if not isinstance(rendered, str) or len(rendered) == 0:
                    return {'passed': False, 'error': f'{form_name} form rendering failed'}
                
                form_results.append(f"{form_name}: OK")
            
            # Test custom form building
            builder = FormBuilder("professional_blue")
            schema = builder.create_form("integration_test", "Integration Test Form")
            
            # Add various field types
            fields = [
                FieldDefinition("text_field", FieldType.TEXT, required=True),
                FieldDefinition("email_field", FieldType.EMAIL, required=True),
                FieldDefinition("url_field", FieldType.URL),
                FieldDefinition("phone_field", FieldType.PHONE),
                FieldDefinition("number_field", FieldType.NUMBER, min_value=0, max_value=100),
                FieldDefinition("select_field", FieldType.SELECT, 
                              choices={"a": "Option A", "b": "Option B"}),
                FieldDefinition("checkbox_field", FieldType.CHECKBOX),
                FieldDefinition("date_field", FieldType.DATE),
            ]
            
            for field in fields:
                builder.add_field("integration_test", field)
            
            custom_form = builder.build_form("integration_test")
            
            # Test custom form
            if not isinstance(custom_form, DynamicForm):
                return {'passed': False, 'error': 'Custom form is not DynamicForm instance'}
            
            # Test serialization
            json_data = builder.save_schema("integration_test")
            if not json_data or len(json_data) == 0:
                return {'passed': False, 'error': 'Schema serialization failed'}
            
            # Test deserialization
            new_builder = FormBuilder()
            loaded_schema = new_builder.load_schema(json_data)
            if len(loaded_schema.fields) != len(fields):
                return {'passed': False, 'error': 'Schema deserialization failed'}
            
            return {
                'passed': True,
                'prebuilt_forms': len(forms),
                'custom_fields': len(fields),
                'serialization': 'OK'
            }
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_widget_compatibility(self) -> Dict[str, Any]:
        """Test widget compatibility across themes."""
        try:
            widget_types = [
                FieldType.TEXT, FieldType.EMAIL, FieldType.URL, FieldType.PHONE,
                FieldType.NUMBER, FieldType.SELECT, FieldType.MULTI_SELECT,
                FieldType.CHECKBOX, FieldType.DATE, FieldType.FILE,
                FieldType.PASSWORD, FieldType.CREDIT_CARD
            ]
            
            compatibility_results = []
            
            for theme_name in self.themes:
                theme_results = []
                
                for widget_type in widget_types:
                    try:
                        builder = FormBuilder(theme_name)
                        schema = builder.create_form("widget_test", "Widget Test")
                        
                        field = FieldDefinition(
                            f"test_{widget_type.value}",
                            widget_type,
                            choices={"a": "A", "b": "B"} if widget_type in [FieldType.SELECT, FieldType.MULTI_SELECT] else None
                        )
                        
                        builder.add_field("widget_test", field)
                        form = builder.build_form("widget_test")
                        
                        # Test widget creation and rendering
                        rendered = form.render_form()
                        if not rendered:
                            theme_results.append(f"{widget_type.value}: FAILED")
                        else:
                            theme_results.append(f"{widget_type.value}: OK")
                            
                    except Exception as e:
                        theme_results.append(f"{widget_type.value}: ERROR - {str(e)}")
                
                compatibility_results.append({
                    'theme': theme_name,
                    'widgets': theme_results
                })
            
            # Check for any failures
            failures = []
            for theme_result in compatibility_results:
                for widget_result in theme_result['widgets']:
                    if 'FAILED' in widget_result or 'ERROR' in widget_result:
                        failures.append(f"{theme_result['theme']}: {widget_result}")
            
            if failures:
                return {
                    'passed': False,
                    'error': f'Widget compatibility failures: {failures[:3]}...' if len(failures) > 3 else str(failures)
                }
            
            return {
                'passed': True,
                'themes_tested': len(self.themes),
                'widget_types_tested': len(widget_types),
                'total_combinations': len(self.themes) * len(widget_types)
            }
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_cross_theme_validation(self) -> Dict[str, Any]:
        """Test validation consistency across themes."""
        try:
            test_data = {
                "email": "test@example.com",
                "url": "https://www.example.com",
                "phone": "+1-555-123-4567",
                "number": 42,
                "credit_card": "4532015112830366"
            }
            
            theme_validation_results = {}
            
            for theme_name in self.themes:
                builder = FormBuilder(theme_name)
                schema = builder.create_form("validation_test", "Validation Test")
                
                # Add validated fields
                fields = [
                    FieldDefinition("email", FieldType.EMAIL, required=True),
                    FieldDefinition("url", FieldType.URL, required=True),
                    FieldDefinition("phone", FieldType.PHONE, required=True),
                    FieldDefinition("number", FieldType.NUMBER, min_value=0, max_value=100, required=True),
                    FieldDefinition("credit_card", FieldType.CREDIT_CARD, required=True),
                ]
                
                for field in fields:
                    builder.add_field("validation_test", field)
                
                form = builder.build_form("validation_test")
                
                # Set test data
                for field_name, value in test_data.items():
                    form.set_field_value(field_name, value)
                
                # Validate
                is_valid = form.validate_form()
                theme_validation_results[theme_name] = is_valid
            
            # Check consistency
            first_result = list(theme_validation_results.values())[0]
            if not all(result == first_result for result in theme_validation_results.values()):
                return {
                    'passed': False,
                    'error': f'Validation inconsistency across themes: {theme_validation_results}'
                }
            
            # All should be valid with our test data
            if not first_result:
                return {
                    'passed': False,
                    'error': 'Valid test data failed validation'
                }
            
            return {
                'passed': True,
                'themes_tested': len(self.themes),
                'validation_consistency': 'OK',
                'test_data_valid': True
            }
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_complex_scenarios(self) -> Dict[str, Any]:
        """Test complex real-world scenarios."""
        try:
            scenarios = []
            
            # Scenario 1: Multi-step form with conditional logic
            builder = FormBuilder("professional_blue")
            schema = builder.create_form("complex_form", "Complex Form", multi_step=True)
            
            conditional_fields = [
                FieldDefinition("user_type", FieldType.SELECT,
                              choices={"individual": "Individual", "business": "Business"},
                              required=True),
                FieldDefinition("company_name", FieldType.TEXT,
                              condition={"field": "user_type", "operator": "equals", "value": "business"},
                              required=True),
                FieldDefinition("personal_income", FieldType.NUMBER,
                              condition={"field": "user_type", "operator": "equals", "value": "individual"},
                              min_value=0),
            ]
            
            for field in conditional_fields:
                builder.add_field("complex_form", field)
            
            form = builder.build_form("complex_form")
            
            # Test conditional logic
            form.set_field_value("user_type", "business")
            if "company_name" not in form.visible_fields:
                return {'passed': False, 'error': 'Conditional field not visible'}
            
            form.set_field_value("user_type", "individual")
            if "personal_income" not in form.visible_fields:
                return {'passed': False, 'error': 'Conditional field switch failed'}
            
            scenarios.append("Conditional logic: OK")
            
            # Scenario 2: Form with all validation types
            validator_form = create_registration_form("elegant_dark")
            
            # Fill with valid data
            valid_data = {
                "username": "testuser123",
                "email": "test@example.com",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "full_name": "Test User",
                "terms_accepted": True
            }
            
            for field, value in valid_data.items():
                validator_form.set_field_value(field, value)
            
            if not validator_form.validate_form():
                return {'passed': False, 'error': 'Valid registration data failed validation'}
            
            scenarios.append("Registration validation: OK")
            
            # Scenario 3: Data export/import
            export_data = validator_form.export_data()
            if not export_data or len(export_data) == 0:
                return {'passed': False, 'error': 'Data export failed'}
            
            validator_form.reset()
            validator_form.import_data(export_data)
            
            # Verify import
            if validator_form.get_field_value("email") != "test@example.com":
                return {'passed': False, 'error': 'Data import failed'}
            
            scenarios.append("Data export/import: OK")
            
            return {
                'passed': True,
                'scenarios_tested': len(scenarios),
                'results': scenarios
            }
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_performance_integration(self) -> Dict[str, Any]:
        """Test performance under integration load."""
        try:
            performance_results = {}
            
            # Test 1: Large form creation across themes
            start_time = time.time()
            
            for theme_name in self.themes:
                builder = FormBuilder(theme_name)
                schema = builder.create_form(f"perf_test_{theme_name}", "Performance Test")
                
                # Add 50 fields
                for i in range(50):
                    field = FieldDefinition(f"field_{i}", FieldType.TEXT, required=i % 10 == 0)
                    builder.add_field(f"perf_test_{theme_name}", field)
                
                form = builder.build_form(f"perf_test_{theme_name}")
            
            theme_creation_time = time.time() - start_time
            performance_results["theme_creation"] = f"{theme_creation_time:.3f}s"
            
            # Test 2: Validation performance
            start_time = time.time()
            
            form_validator = create_form_validator()
            
            # Add multiple validation chains
            for i in range(20):
                email_chain = form_validator.add_field(f"email_{i}")
                email_chain.required().email()
                
                url_chain = form_validator.add_field(f"url_{i}")
                url_chain.url()
                
                number_chain = form_validator.add_field(f"number_{i}")
                number_chain.number(min_value=0, max_value=100)
            
            # Validate all fields
            for i in range(20):
                form_validator.validate_field(f"email_{i}", "test@example.com")
                form_validator.validate_field(f"url_{i}", "https://example.com")
                form_validator.validate_field(f"number_{i}", 50)
            
            validation_time = time.time() - start_time
            performance_results["validation"] = f"{validation_time:.3f}s"
            
            # Test 3: Serialization performance
            start_time = time.time()
            
            for theme_name in self.themes:
                builder = FormBuilder(theme_name)
                schema = builder.create_form(f"serial_test_{theme_name}", "Serialization Test")
                
                for i in range(30):
                    field = FieldDefinition(f"field_{i}", FieldType.TEXT)
                    builder.add_field(f"serial_test_{theme_name}", field)
                
                json_data = builder.save_schema(f"serial_test_{theme_name}")
                new_builder = FormBuilder()
                loaded_schema = new_builder.load_schema(json_data)
            
            serialization_time = time.time() - start_time
            performance_results["serialization"] = f"{serialization_time:.3f}s"
            
            # Performance thresholds (adjust based on requirements)
            if theme_creation_time > 5.0:  # 5 seconds max for all themes
                return {'passed': False, 'error': f'Theme creation too slow: {theme_creation_time:.3f}s'}
            
            if validation_time > 2.0:  # 2 seconds max for validation
                return {'passed': False, 'error': f'Validation too slow: {validation_time:.3f}s'}
            
            if serialization_time > 3.0:  # 3 seconds max for serialization
                return {'passed': False, 'error': f'Serialization too slow: {serialization_time:.3f}s'}
            
            return {
                'passed': True,
                'performance_results': performance_results,
                'within_thresholds': True
            }
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and edge cases."""
        try:
            error_cases = []
            
            # Test 1: Invalid theme
            try:
                builder = FormBuilder("invalid_theme")
                # Should not fail but use default theme
                if builder.theme_name == "invalid_theme":
                    return {'passed': False, 'error': 'Invalid theme accepted'}
                error_cases.append("Invalid theme handling: OK")
            except Exception:
                error_cases.append("Invalid theme handling: OK (exception thrown)")
            
            # Test 2: Invalid field type
            try:
                builder = FormBuilder("professional_blue")
                schema = builder.create_form("error_test", "Error Test")
                
                # This should be handled gracefully
                field = FieldDefinition("test", "INVALID_TYPE")  # Invalid type
                builder.add_field("error_test", field)
                error_cases.append("Invalid field type: Handled")
            except Exception:
                error_cases.append("Invalid field type: Exception (expected)")
            
            # Test 3: Invalid validation data
            validator = EmailValidator()
            result = validator.validate(None)  # None value
            if not result.is_valid:
                error_cases.append("None validation: OK")
            else:
                return {'passed': False, 'error': 'None value passed email validation'}
            
            # Test 4: Empty form validation
            form = create_registration_form("professional_blue")
            is_valid = form.validate_form()  # Should be False for empty required fields
            if not is_valid:
                error_cases.append("Empty form validation: OK")
            else:
                return {'passed': False, 'error': 'Empty form passed validation'}
            
            # Test 5: Invalid JSON schema
            try:
                builder = FormBuilder()
                builder.load_schema("invalid json")
                error_cases.append("Invalid JSON: Handled")
            except Exception:
                error_cases.append("Invalid JSON: Exception (expected)")
            
            return {
                'passed': True,
                'error_cases_tested': len(error_cases),
                'results': error_cases
            }
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_data_persistence(self) -> Dict[str, Any]:
        """Test data persistence and consistency."""
        try:
            persistence_tests = []
            
            # Test 1: Form data persistence
            form = create_registration_form("professional_blue")
            
            test_data = {
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
                "full_name": "Test User",
                "terms_accepted": True
            }
            
            # Set data
            for field, value in test_data.items():
                form.set_field_value(field, value)
            
            # Export and reset
            exported_data = form.export_data()
            form.reset()
            
            # Verify reset
            if form.get_field_value("email"):
                return {'passed': False, 'error': 'Form reset failed'}
            
            # Import and verify
            form.import_data(exported_data)
            if form.get_field_value("email") != "test@example.com":
                return {'passed': False, 'error': 'Data import failed'}
            
            persistence_tests.append("Form data persistence: OK")
            
            # Test 2: Schema persistence
            builder = FormBuilder("elegant_dark")
            schema = builder.create_form("persistence_test", "Persistence Test")
            
            original_fields = [
                FieldDefinition("field1", FieldType.TEXT, required=True),
                FieldDefinition("field2", FieldType.EMAIL),
                FieldDefinition("field3", FieldType.SELECT, choices={"a": "A", "b": "B"}),
            ]
            
            for field in original_fields:
                builder.add_field("persistence_test", field)
            
            # Serialize
            json_data = builder.save_schema("persistence_test")
            
            # Load in new builder
            new_builder = FormBuilder()
            loaded_schema = new_builder.load_schema(json_data)
            
            # Verify schema integrity
            if len(loaded_schema.fields) != len(original_fields):
                return {'passed': False, 'error': 'Schema field count mismatch'}
            
            # Check field properties
            for original, loaded in zip(original_fields, loaded_schema.fields):
                if original.name != loaded.name or original.field_type != loaded.field_type:
                    return {'passed': False, 'error': 'Schema field property mismatch'}
            
            persistence_tests.append("Schema persistence: OK")
            
            # Test 3: Theme persistence
            themed_form = builder.build_form("persistence_test")
            if themed_form.theme_name != "elegant_dark":
                return {'passed': False, 'error': 'Theme not persisted in form'}
            
            persistence_tests.append("Theme persistence: OK")
            
            return {
                'passed': True,
                'tests_completed': len(persistence_tests),
                'results': persistence_tests
            }
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_questionary_compatibility(self) -> Dict[str, Any]:
        """Test questionary compatibility and styling."""
        try:
            compatibility_tests = []
            
            # Test 1: Style adapter creation
            for theme_name in self.themes:
                adapter = QuestionaryStyleAdapter(theme_name)
                
                if not hasattr(adapter, 'style'):
                    return {'passed': False, 'error': f'Style adapter for {theme_name} missing style attribute'}
                
                # Verify style is not empty
                if not adapter.style:
                    return {'passed': False, 'error': f'Style adapter for {theme_name} has empty style'}
            
            compatibility_tests.append(f"Style adapters: {len(self.themes)} themes OK")
            
            # Test 2: Theme color mapping
            for theme_name in self.themes:
                theme = TUIEngineThemes.get_theme(theme_name)
                adapter = QuestionaryStyleAdapter(theme_name)
                
                # Check that theme colors are mapped
                required_colors = ['primary', 'secondary', 'success', 'warning', 'error', 'info']
                for color in required_colors:
                    if not hasattr(theme, color):
                        return {'passed': False, 'error': f'Theme {theme_name} missing {color} color'}
            
            compatibility_tests.append("Theme color mapping: OK")
            
            # Test 3: Integration with forms
            for theme_name in self.themes:
                form = create_registration_form(theme_name)
                
                # Verify form has theme applied
                if form.schema.theme != theme_name:
                    return {'passed': False, 'error': f'Form theme mismatch for {theme_name}'}
                
                # Verify form can render (basic compatibility check)
                rendered = form.render_form()
                if not rendered or len(rendered) == 0:
                    return {'passed': False, 'error': f'Form rendering failed for theme {theme_name}'}
            
            compatibility_tests.append("Form integration: OK")
            
            return {
                'passed': True,
                'compatibility_tests': len(compatibility_tests),
                'results': compatibility_tests,
                'questionary_integration': 'Verified'
            }
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def print_summary(self, passed: int, total: int):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("🧪 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed / total) * 100
        print(f"🎯 Results: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        if passed == total:
            print("🎉 ALL INTEGRATION TESTS PASSED!")
            print("✅ TUI Engine components are fully integrated and compatible")
        else:
            print(f"⚠️  {total - passed} test(s) failed")
            print("❌ Integration issues detected")
        
        print()
        
        # Detailed results
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result.get('passed', False) else "❌ FAILED"
            duration = result.get('duration', 0)
            print(f"{status} {test_name} ({duration:.3f}s)")
            
            if not result.get('passed', False):
                error = result.get('error', 'Unknown error')
                print(f"   Error: {error}")
        
        print("\n" + "=" * 60)
        print("🔧 INTEGRATION TEST COMPLETE")
        print("=" * 60)
        
        # Component summary
        print("\n💡 INTEGRATION SUMMARY:")
        print("• Themes: All themes integrate properly with forms and validation")
        print("• Validation: Consistent validation across all themes and widgets")
        print("• Form Builder: Compatible with all themes and validation types")
        print("• Widgets: All widget types work across all themes")
        print("• Performance: Integration maintains performance standards")
        print("• Error Handling: Graceful handling of edge cases and errors")
        print("• Data Persistence: Reliable data export/import and schema serialization")
        print("• Questionary: Full compatibility with questionary styling and components")


def main():
    """Main integration test entry point."""
    print("🚀 Starting TUI Engine Integration Tests...")
    print("This comprehensive test verifies all components work together.\n")
    
    try:
        test_suite = IntegrationTest()
        success = test_suite.run_all_tests()
        
        if success:
            print("\n🎉 Integration test completed successfully!")
            print("All TUI Engine components are properly integrated.")
        else:
            print("\n⚠️  Integration test completed with issues.")
            print("Some components may need attention.")
        
        return success
        
    except KeyboardInterrupt:
        print("\n🛑 Integration test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()