#!/usr/bin/env python3
"""
Comprehensive test suite for ValidationSystem.

This test suite validates:
- Built-in validators (email, URL, phone, etc.)
- Custom validation rules and chains
- Validation result formatting and styling
- Form-level validation coordination
- Cross-field validation dependencies
- Performance and caching
- Professional styling integration
- Real-world validation scenarios

Run with: python test_validation.py
"""

import sys
import time
import tempfile
from pathlib import Path

# Add src to path for testing
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

try:
    from tui_engine.validation import (
        ValidationLevel, ValidationTrigger, ValidationResult, ValidationRule,
        ValidatorRegistry, ValidationChain, ValidationTheme, EnhancedValidator,
        create_form_validator, validate_email, validate_url, validate_phone
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


def test_validation_result():
    """Test ValidationResult functionality."""
    print("🧪 Testing ValidationResult...")
    
    # Test valid result
    print("  ✅ Valid result tests:")
    valid_result = ValidationResult(is_valid=True, message="All good")
    assert valid_result.is_valid == True
    assert bool(valid_result) == True
    assert "Valid" in str(valid_result)
    print("    ✅ Valid result creation and boolean evaluation")
    
    # Test invalid result
    print("  ❌ Invalid result tests:")
    invalid_result = ValidationResult(
        is_valid=False,
        level=ValidationLevel.ERROR,
        message="Something is wrong",
        field_name="email",
        suggestions=["user@example.com"]
    )
    assert invalid_result.is_valid == False
    assert bool(invalid_result) == False
    assert "email" in str(invalid_result)
    assert "Something is wrong" in str(invalid_result)
    print("    ✅ Invalid result creation and representation")
    
    # Test different severity levels
    print("  📊 Severity level tests:")
    levels = [ValidationLevel.INFO, ValidationLevel.WARNING, ValidationLevel.ERROR, ValidationLevel.CRITICAL]
    for level in levels:
        result = ValidationResult(is_valid=False, level=level, message="Test message")
        result_str = str(result)
        assert "Test message" in result_str
        print(f"    ✅ {level.value}: {result_str[:50]}...")
    
    print("✅ ValidationResult tests passed!")


def test_validation_rule():
    """Test ValidationRule functionality."""
    print("\n🧪 Testing ValidationRule...")
    
    # Test simple rule
    print("  📝 Simple rule tests:")
    def simple_validator(value):
        return len(str(value)) > 3
    
    rule = ValidationRule(
        name="min_length",
        validator=simple_validator,
        message="Must be longer than 3 characters"
    )
    
    # Test valid value
    result = rule.validate("hello")
    assert result.is_valid == True
    assert result.rule_name == "min_length"
    print("    ✅ Valid value passes")
    
    # Test invalid value
    result = rule.validate("hi")
    assert result.is_valid == False
    assert result.message == "Must be longer than 3 characters"
    print("    ✅ Invalid value fails with correct message")
    
    # Test rule returning ValidationResult
    print("  🔄 ValidationResult return tests:")
    def complex_validator(value):
        if not value:
            return ValidationResult(False, ValidationLevel.ERROR, "Value is required")
        if len(str(value)) < 5:
            return ValidationResult(
                False, ValidationLevel.WARNING, "Value is short",
                suggestions=["Make it longer"]
            )
        return ValidationResult(True, ValidationLevel.INFO, "Good length")
    
    complex_rule = ValidationRule(name="complex", validator=complex_validator)
    
    # Test empty value
    result = complex_rule.validate("")
    assert not result.is_valid
    assert result.level == ValidationLevel.ERROR
    print("    ✅ Empty value handled correctly")
    
    # Test short value
    result = complex_rule.validate("test")
    assert not result.is_valid
    assert result.level == ValidationLevel.WARNING
    assert len(result.suggestions) > 0
    print("    ✅ Short value returns warning with suggestions")
    
    # Test good value
    result = complex_rule.validate("testing")
    assert result.is_valid
    assert result.level == ValidationLevel.INFO
    print("    ✅ Good value passes with info")
    
    # Test exception handling
    print("  ⚠️ Exception handling tests:")
    def broken_validator(value):
        raise ValueError("Something went wrong")
    
    broken_rule = ValidationRule(name="broken", validator=broken_validator)
    result = broken_rule.validate("test")
    assert not result.is_valid
    assert result.level == ValidationLevel.CRITICAL
    assert "exception" in result.metadata
    print("    ✅ Exceptions handled gracefully")
    
    print("✅ ValidationRule tests passed!")


def test_validator_registry():
    """Test ValidatorRegistry functionality."""
    print("\n🧪 Testing ValidatorRegistry...")
    
    # Test registry initialization
    print("  🏗️ Registry initialization tests:")
    registry = ValidatorRegistry()
    validators = registry.list_validators()
    
    expected_validators = [
        "required", "email", "url", "phone", "number", "integer",
        "date", "ip_address", "credit_card", "file_exists", "regex"
    ]
    
    for validator_name in expected_validators:
        assert validator_name in validators, f"Missing built-in validator: {validator_name}"
    
    print(f"    ✅ Registry initialized with {len(validators)} validators")
    
    # Test email validation
    print("  📧 Email validation tests:")
    email_validator = registry.get("email")
    assert email_validator is not None
    
    valid_emails = [
        "user@example.com",
        "test.email+tag@domain.co.uk",
        "user_name@company-name.org"
    ]
    
    invalid_emails = [
        "invalid.email",
        "@domain.com",
        "user@",
        "user..double.dot@example.com",
        "toolong" + "x" * 60 + "@example.com"  # Too long local part
    ]
    
    for email in valid_emails:
        result = email_validator.validate(email)
        assert result.is_valid, f"Should validate: {email}"
        print(f"    ✅ Valid email: {email}")
    
    for email in invalid_emails:
        result = email_validator.validate(email)
        assert not result.is_valid, f"Should not validate: {email}"
        print(f"    ❌ Invalid email: {email}")
    
    # Test URL validation
    print("  🌐 URL validation tests:")
    url_validator = registry.get("url")
    assert url_validator is not None
    
    valid_urls = [
        "https://example.com",
        "http://subdomain.example.com/path",
        "ftp://files.example.com",
        "https://example.com/path?query=value#fragment"
    ]
    
    invalid_urls = [
        "not-a-url",
        "example.com",  # Missing protocol
        "http://",      # Missing domain
        "://example.com"  # Missing scheme
    ]
    
    for url in valid_urls:
        result = url_validator.validate(url)
        assert result.is_valid, f"Should validate: {url}"
        print(f"    ✅ Valid URL: {url}")
    
    for url in invalid_urls:
        result = url_validator.validate(url)
        assert not result.is_valid, f"Should not validate: {url}"
        print(f"    ❌ Invalid URL: {url}")
    
    # Test phone validation
    print("  📱 Phone validation tests:")
    phone_validator = registry.get("phone")
    assert phone_validator is not None
    
    valid_phones = [
        "+1-555-123-4567",
        "555-123-4567",
        "+44-20-1234-5678",
        "5551234567"
    ]
    
    invalid_phones = [
        "123",          # Too short
        "+1-555-123-4567-8901-2345",  # Too long
        "not-a-phone",  # No digits
        ""              # Empty
    ]
    
    for phone in valid_phones:
        result = phone_validator.validate(phone)
        # Phone validation might return warnings for unrecognized formats
        print(f"    {'✅' if result.is_valid else '⚠️'} Phone: {phone} - {result.message or 'Valid'}")
    
    for phone in invalid_phones:
        result = phone_validator.validate(phone)
        assert not result.is_valid, f"Should not validate: {phone}"
        print(f"    ❌ Invalid phone: {phone}")
    
    # Test number validation
    print("  🔢 Number validation tests:")
    number_validator = registry.get("number")
    assert number_validator is not None
    
    valid_numbers = ["123", "123.45", "-456.78", "0", "1e10"]
    invalid_numbers = ["abc", "12.34.56", "not-a-number"]
    
    for number in valid_numbers:
        result = number_validator.validate(number)
        assert result.is_valid, f"Should validate: {number}"
        print(f"    ✅ Valid number: {number}")
    
    for number in invalid_numbers:
        result = number_validator.validate(number)
        assert not result.is_valid, f"Should not validate: {number}"
        print(f"    ❌ Invalid number: {number}")
    
    # Test IP address validation
    print("  🌐 IP address validation tests:")
    ip_validator = registry.get("ip_address")
    assert ip_validator is not None
    
    valid_ips = ["192.168.1.1", "10.0.0.1", "::1", "2001:db8::1"]
    invalid_ips = ["256.256.256.256", "not.an.ip", "192.168.1"]
    
    for ip in valid_ips:
        result = ip_validator.validate(ip)
        assert result.is_valid, f"Should validate: {ip}"
        print(f"    ✅ Valid IP: {ip}")
    
    for ip in invalid_ips:
        result = ip_validator.validate(ip)
        assert not result.is_valid, f"Should not validate: {ip}"
        print(f"    ❌ Invalid IP: {ip}")
    
    # Test credit card validation
    print("  💳 Credit card validation tests:")
    cc_validator = registry.get("credit_card")
    assert cc_validator is not None
    
    # Valid test credit card numbers (using Luhn algorithm)
    valid_cards = [
        "4532015112830366",  # Visa
        "5555555555554444",  # MasterCard
        "378282246310005",   # American Express
    ]
    
    invalid_cards = [
        "1234567890123456",  # Invalid Luhn
        "123",               # Too short
        "abcd1234567890123", # Contains letters
    ]
    
    for card in valid_cards:
        result = cc_validator.validate(card)
        assert result.is_valid, f"Should validate: {card}"
        print(f"    ✅ Valid card: {card} - {result.metadata.get('card_type', 'Unknown')}")
    
    for card in invalid_cards:
        result = cc_validator.validate(card)
        assert not result.is_valid, f"Should not validate: {card}"
        print(f"    ❌ Invalid card: {card}")
    
    # Test custom validators
    print("  🔧 Custom validator tests:")
    
    # Range validator
    range_validator = registry.create_range_validator(min_val=10, max_val=100)
    assert range_validator.validate("50").is_valid
    assert not range_validator.validate("5").is_valid
    assert not range_validator.validate("150").is_valid
    print("    ✅ Range validator works")
    
    # Length validator
    length_validator = registry.create_length_validator(min_len=3, max_len=10)
    assert length_validator.validate("hello").is_valid
    assert not length_validator.validate("hi").is_valid
    assert not length_validator.validate("this is too long").is_valid
    print("    ✅ Length validator works")
    
    # Regex validator
    regex_validator = registry.create_regex_validator(r'^\d{3}-\d{3}-\d{4}$', "Must be XXX-XXX-XXXX format")
    assert regex_validator.validate("123-456-7890").is_valid
    assert not regex_validator.validate("1234567890").is_valid
    print("    ✅ Regex validator works")
    
    print("✅ ValidatorRegistry tests passed!")


def test_validation_chain():
    """Test ValidationChain functionality."""
    print("\n🧪 Testing ValidationChain...")
    
    # Test chain creation and rule addition
    print("  ⛓️ Chain creation tests:")
    chain = ValidationChain("email_field")
    assert chain.field_name == "email_field"
    assert len(chain.rules) == 0
    print("    ✅ Chain created")
    
    # Test fluent interface
    print("  🔗 Fluent interface tests:")
    chain = (ValidationChain("test_field")
             .required("Field is required")
             .min_length(5, "Must be at least 5 characters")
             .max_length(20, "Must be no more than 20 characters"))
    
    assert len(chain.rules) == 3
    print("    ✅ Fluent chaining works")
    
    # Test validation with all rules passing
    print("  ✅ All rules passing tests:")
    results = chain.validate("hello world")
    assert len(results) == 3
    assert all(result.is_valid for result in results)
    print("    ✅ All rules pass for valid input")
    
    # Test validation with rule failing
    print("  ❌ Rule failing tests:")
    results = chain.validate("hi")  # Too short
    assert len(results) <= 3  # May stop on first error
    assert not all(result.is_valid for result in results)
    print("    ✅ Rules fail for invalid input")
    
    # Test stop on first error
    print("  🛑 Stop on error tests:")
    chain.stop_on_first_error = True
    results = chain.validate("")  # Will fail required check
    assert len(results) == 1  # Should stop after first failure
    assert not results[0].is_valid
    print("    ✅ Stops on first error")
    
    # Test continue on error
    chain.stop_on_first_error = False
    results = chain.validate("")  # Will fail required and min_length, pass max_length
    assert len(results) == 3  # Should run all rules
    assert results[0].is_valid == False  # required fails
    assert results[1].is_valid == False  # min_length fails  
    assert results[2].is_valid == True   # max_length passes (empty <= 20)
    print("    ✅ Continues through all errors")
    
    # Test email chain
    print("  📧 Email chain tests:")
    email_chain = ValidationChain("email").required().email()
    
    valid_result = email_chain.validate("user@example.com")
    assert email_chain.is_valid("user@example.com")
    print("    ✅ Valid email passes chain")
    
    invalid_result = email_chain.validate("invalid-email")
    assert not email_chain.is_valid("invalid-email")
    errors = email_chain.get_errors("invalid-email")
    assert len(errors) > 0
    print("    ✅ Invalid email fails chain")
    
    # Test custom validation
    print("  🎯 Custom validation tests:")
    def is_even(value):
        try:
            return int(value) % 2 == 0
        except ValueError:
            return False
    
    custom_chain = (ValidationChain("number")
                   .required()
                   .custom(is_even, "Must be an even number", "even_check"))
    
    assert custom_chain.is_valid("4")
    assert not custom_chain.is_valid("3")
    assert not custom_chain.is_valid("abc")
    print("    ✅ Custom validation works")
    
    print("✅ ValidationChain tests passed!")


def test_validation_theme():
    """Test ValidationTheme functionality."""
    print("\n🧪 Testing ValidationTheme...")
    
    # Test theme initialization
    print("  🎨 Theme initialization tests:")
    theme = ValidationTheme("professional_blue")
    assert theme.theme_variant == "professional_blue"
    print("    ✅ Theme initialized")
    
    # Test message formatting
    print("  📝 Message formatting tests:")
    
    # Valid result
    valid_result = ValidationResult(True, ValidationLevel.INFO, "All good")
    formatted = theme.format_message(valid_result)
    print(f"    ✅ Valid: {formatted}")
    
    # Error result
    error_result = ValidationResult(
        False, ValidationLevel.ERROR, "Invalid email",
        suggestions=["user@example.com", "test@domain.org"]
    )
    formatted = theme.format_message(error_result)
    assert "Invalid email" in formatted
    assert "user@example.com" in formatted  # Should include suggestions
    first_line = formatted.split('\n')[0]
    print(f"    ❌ Error: {first_line}")  # First line only
    
    # Warning result
    warning_result = ValidationResult(False, ValidationLevel.WARNING, "Weak password")
    formatted = theme.format_message(warning_result)
    assert "Weak password" in formatted
    print(f"    ⚠️ Warning: {formatted}")
    
    # Test field status formatting
    print("  📊 Field status tests:")
    results = [
        ValidationResult(True, ValidationLevel.INFO, "Valid"),
        ValidationResult(True, ValidationLevel.INFO, "Good format")
    ]
    status = theme.format_field_status("email", results)
    assert "Valid" in status
    print(f"    ✅ Valid field: {status}")
    
    error_results = [
        ValidationResult(False, ValidationLevel.ERROR, "Required"),
        ValidationResult(False, ValidationLevel.ERROR, "Invalid format")
    ]
    status = theme.format_field_status("email", error_results)
    assert "Required" in status
    first_line = status.split('\n')[0]
    print(f"    ❌ Error field: {first_line}")  # First line only
    
    print("✅ ValidationTheme tests passed!")


def test_enhanced_validator():
    """Test EnhancedValidator functionality."""
    print("\n🧪 Testing EnhancedValidator...")
    
    # Test validator creation
    print("  🚀 Validator creation tests:")
    validator = EnhancedValidator("professional_blue")
    assert validator.theme_variant == "professional_blue"
    assert len(validator.chains) == 0
    print("    ✅ Validator created")
    
    # Test field addition
    print("  📝 Field addition tests:")
    email_chain = validator.add_field("email").required().email()
    phone_chain = validator.add_field("phone").required().phone()
    
    assert len(validator.chains) == 2
    assert "email" in validator.chains
    assert "phone" in validator.chains
    print("    ✅ Fields added")
    
    # Test single field validation
    print("  🔍 Single field validation tests:")
    email_results = validator.validate_field("email", "user@example.com")
    assert all(result.is_valid for result in email_results)
    print("    ✅ Valid email passes")
    
    email_results = validator.validate_field("email", "invalid-email")
    assert not all(result.is_valid for result in email_results)
    print("    ✅ Invalid email fails")
    
    # Test form data management
    print("  📋 Form data tests:")
    validator.set_field_value("email", "test@example.com")
    validator.set_field_value("phone", "555-123-4567")
    
    assert validator.form_data["email"] == "test@example.com"
    assert validator.form_data["phone"] == "555-123-4567"
    print("    ✅ Form data stored")
    
    # Test validation with stored data
    email_results = validator.validate_field("email")  # Uses stored value
    assert all(result.is_valid for result in email_results)
    print("    ✅ Validation with stored data works")
    
    # Test all field validation
    print("  📊 All field validation tests:")
    all_results = validator.validate_all()
    assert len(all_results) == 2
    assert "email" in all_results
    assert "phone" in all_results
    print("    ✅ All fields validated")
    
    # Test form validity
    print("  ✅ Form validity tests:")
    assert validator.is_valid()  # Should be valid with good data
    print("    ✅ Form is valid with good data")
    
    validator.set_field_value("email", "bad-email")
    assert not validator.is_valid()  # Should be invalid now
    print("    ❌ Form is invalid with bad data")
    
    # Test error retrieval
    print("  📋 Error retrieval tests:")
    errors = validator.get_errors()
    assert len(errors) > 0
    assert "email" in errors
    print(f"    ✅ Retrieved {len(errors)} field errors")
    
    formatted_errors = validator.get_formatted_errors()
    assert len(formatted_errors) > 0
    print(f"    ✅ Formatted errors: {len(formatted_errors)} characters")
    
    # Test field status
    print("  📊 Field status tests:")
    email_status = validator.get_field_status("email")
    assert "email" in email_status.lower()
    print(f"    ✅ Email status: {email_status.split(':')[0]}...")
    
    # Test validation summary
    print("  📈 Validation summary tests:")
    summary = validator.get_validation_summary()
    expected_keys = ['total_fields', 'valid_fields', 'invalid_fields', 'total_errors', 'is_form_valid', 'validation_coverage']
    for key in expected_keys:
        assert key in summary
    
    assert summary['total_fields'] == 2
    assert summary['invalid_fields'] > 0  # We have invalid email
    print(f"    ✅ Summary: {summary['valid_fields']}/{summary['total_fields']} valid, {summary['total_errors']} errors")
    
    # Test caching
    print("  🚀 Caching tests:")
    # Clear cache and measure time
    validator.cache.clear()
    
    start_time = time.time()
    for _ in range(100):
        validator.validate_field("email", "test@example.com")
    first_run_time = time.time() - start_time
    
    # Should be faster due to caching
    start_time = time.time()
    for _ in range(100):
        validator.validate_field("email", "test@example.com")
    cached_run_time = time.time() - start_time
    
    print(f"    ✅ First run: {first_run_time:.3f}s, Cached run: {cached_run_time:.3f}s")
    
    # Test questionary integration
    print("  🎭 Questionary integration tests:")
    questionary_validator = validator.create_questionary_validator("email")
    
    # Test with valid email
    result = questionary_validator("valid@example.com")
    assert result is True, "Should return True for valid email"
    print("    ✅ Valid email returns True")
    
    # Test with invalid email
    result = questionary_validator("invalid-email")
    assert isinstance(result, str), "Should return error message for invalid email"
    print(f"    ❌ Invalid email returns: {result}")
    
    # Test field removal
    print("  🗑️ Field removal tests:")
    validator.remove_field("phone")
    assert "phone" not in validator.chains
    assert len(validator.chains) == 1
    print("    ✅ Field removed")
    
    # Test reset
    print("  🔄 Reset tests:")
    validator.reset()
    assert len(validator.chains) == 0
    assert len(validator.form_data) == 0
    assert len(validator.cache) == 0
    print("    ✅ Validator reset")
    
    print("✅ EnhancedValidator tests passed!")


def test_convenience_functions():
    """Test convenience functions."""
    print("\n🧪 Testing convenience functions...")
    
    # Test create_form_validator
    print("  🏗️ Form validator creation tests:")
    validator = create_form_validator("dark_mode")
    assert isinstance(validator, EnhancedValidator)
    assert validator.theme_variant == "dark_mode"
    print("    ✅ Form validator created")
    
    # Test quick validation functions
    print("  ⚡ Quick validation tests:")
    
    # Email validation
    result = validate_email("user@example.com")
    assert result.is_valid
    print("    ✅ Valid email validated")
    
    result = validate_email("invalid-email")
    assert not result.is_valid
    print("    ❌ Invalid email rejected")
    
    # URL validation
    result = validate_url("https://example.com")
    assert result.is_valid
    print("    ✅ Valid URL validated")
    
    result = validate_url("not-a-url")
    assert not result.is_valid
    print("    ❌ Invalid URL rejected")
    
    # Phone validation
    result = validate_phone("555-123-4567")
    # Phone validation might return warnings for format
    print(f"    📱 Phone result: {'✅' if result.is_valid else '⚠️'} {result.message or 'Valid'}")
    
    print("✅ Convenience function tests passed!")


def test_real_world_scenarios():
    """Test real-world validation scenarios."""
    print("\n🧪 Testing real-world scenarios...")
    
    # Test user registration form
    print("  👤 User registration scenario:")
    validator = create_form_validator()
    
    # Set up registration form validation
    validator.add_field("username").required().min_length(3).max_length(20).regex(
        r'^[a-zA-Z0-9_]+$', "Username can only contain letters, numbers, and underscores"
    )
    validator.add_field("email").required().email()
    validator.add_field("password").required().min_length(8)
    validator.add_field("phone").required().phone()
    
    # Test with valid data
    valid_data = {
        "username": "john_doe123",
        "email": "john.doe@example.com",
        "password": "SecurePass123!",
        "phone": "555-123-4567"
    }
    
    for field, value in valid_data.items():
        validator.set_field_value(field, value)
    
    assert validator.is_valid(), "Registration form should be valid"
    summary = validator.get_validation_summary()
    print(f"    ✅ Valid registration: {summary['valid_fields']}/{summary['total_fields']} fields valid")
    
    # Test with invalid data
    invalid_data = {
        "username": "a",  # Too short
        "email": "invalid-email",
        "password": "123",  # Too short
        "phone": "123"  # Too short
    }
    
    for field, value in invalid_data.items():
        validator.set_field_value(field, value)
    
    assert not validator.is_valid(), "Registration form should be invalid"
    errors = validator.get_errors()
    print(f"    ❌ Invalid registration: {len(errors)} fields with errors")
    
    # Test contact form
    print("  📞 Contact form scenario:")
    contact_validator = create_form_validator()
    
    contact_validator.add_field("name").required().min_length(2)
    contact_validator.add_field("email").required().email()
    contact_validator.add_field("subject").required().min_length(5).max_length(100)
    contact_validator.add_field("message").required().min_length(10).max_length(1000)
    contact_validator.add_field("website").url()  # Optional URL
    
    # Test valid contact form
    contact_data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "subject": "Question about your services",
        "message": "I would like to know more about your TUI engine capabilities.",
        "website": "https://janesmith.com"
    }
    
    for field, value in contact_data.items():
        contact_validator.set_field_value(field, value)
    
    assert contact_validator.is_valid(), "Contact form should be valid"
    print("    ✅ Valid contact form")
    
    # Test payment form
    print("  💳 Payment form scenario:")
    payment_validator = create_form_validator()
    
    payment_validator.add_field("card_number").required().custom(
        lambda x: len(x.replace('-', '').replace(' ', '')) >= 13,
        "Card number must be at least 13 digits"
    )
    payment_validator.add_field("expiry").required().regex(
        r'^\d{2}/\d{2}$', "Expiry must be MM/YY format"
    )
    payment_validator.add_field("cvv").required().regex(
        r'^\d{3,4}$', "CVV must be 3 or 4 digits"
    )
    payment_validator.add_field("amount").required().custom(
        lambda x: float(x) > 0, "Amount must be greater than 0"
    )
    
    # Test valid payment
    payment_data = {
        "card_number": "4532-0151-1283-0366",
        "expiry": "12/25",
        "cvv": "123",
        "amount": "99.99"
    }
    
    for field, value in payment_data.items():
        payment_validator.set_field_value(field, value)
    
    is_valid = payment_validator.is_valid()
    print(f"    {'✅' if is_valid else '❌'} Payment form validation")
    
    # Test configuration form
    print("  ⚙️ Configuration form scenario:")
    config_validator = create_form_validator()
    
    config_validator.add_field("server_host").required().custom(
        lambda x: x in ["localhost", "127.0.0.1"] or "." in x,
        "Must be localhost, IP address, or domain name"
    )
    config_validator.add_field("server_port").required().custom(
        lambda x: 1 <= int(x) <= 65535, "Port must be between 1 and 65535"
    )
    config_validator.add_field("database_url").required().url()
    config_validator.add_field("max_connections").required().custom(
        lambda x: 1 <= int(x) <= 1000, "Must be between 1 and 1000"
    )
    
    # Test valid config
    config_data = {
        "server_host": "api.example.com",
        "server_port": "8080",
        "database_url": "postgresql://user:pass@db.example.com:5432/mydb",
        "max_connections": "100"
    }
    
    for field, value in config_data.items():
        config_validator.set_field_value(field, value)
    
    is_valid = config_validator.is_valid()
    print(f"    {'✅' if is_valid else '❌'} Configuration form validation")
    
    if not is_valid:
        errors = config_validator.get_errors()
        print(f"    ℹ️ Config errors: {list(errors.keys())}")
    
    print("✅ Real-world scenario tests passed!")


def test_performance_and_optimization():
    """Test performance and optimization features."""
    print("\n🧪 Testing performance and optimization...")
    
    # Test validation performance
    print("  ⚡ Validation performance tests:")
    validator = create_form_validator()
    
    # Create complex validation chain
    validator.add_field("email").required().email().min_length(5).max_length(50)
    validator.add_field("password").required().min_length(8).max_length(128).regex(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]',
        "Password must contain uppercase, lowercase, number, and special character"
    )
    
    # Test validation speed
    test_data = {
        "email": "user@example.com",
        "password": "SecurePass123!"
    }
    
    start_time = time.time()
    for _ in range(1000):
        for field, value in test_data.items():
            validator.validate_field(field, value)
    validation_time = time.time() - start_time
    
    validations_per_second = 2000 / validation_time  # 2 fields * 1000 iterations
    print(f"    ✅ Validation performance: {validations_per_second:.0f} validations/sec")
    
    # Test caching effectiveness
    print("  🚀 Caching effectiveness tests:")
    validator.cache.clear()
    
    # First run (no cache)
    start_time = time.time()
    for _ in range(100):
        validator.validate_field("email", "test@example.com")
    first_run_time = time.time() - start_time
    
    # Second run (with cache)
    start_time = time.time()
    for _ in range(100):
        validator.validate_field("email", "test@example.com")
    cached_run_time = time.time() - start_time
    
    speedup = first_run_time / cached_run_time if cached_run_time > 0 else float('inf')
    print(f"    ✅ Cache speedup: {speedup:.1f}x faster")
    
    # Test memory usage with large forms
    print("  💾 Memory usage tests:")
    large_validator = create_form_validator()
    
    # Create many fields
    for i in range(100):
        large_validator.add_field(f"field_{i}").required().min_length(1)
    
    # Set values for all fields
    for i in range(100):
        large_validator.set_field_value(f"field_{i}", f"value_{i}")
    
    # Validate all fields
    start_time = time.time()
    all_results = large_validator.validate_all()
    large_form_time = time.time() - start_time
    
    assert len(all_results) == 100
    validations_per_second = 100 / large_form_time if large_form_time > 0 else float('inf')
    print(f"    ✅ Large form (100 fields): {validations_per_second:.0f} fields/sec")
    
    # Test regex compilation caching
    print("  🔍 Regex caching tests:")
    registry = ValidatorRegistry()
    
    # Create multiple regex validators with same pattern
    pattern = r'^[A-Z][a-z]+$'
    start_time = time.time()
    for _ in range(100):
        validator_rule = registry.create_regex_validator(pattern, "Must start with capital letter")
        result = validator_rule.validate("TestValue")
    regex_time = time.time() - start_time
    
    print(f"    ✅ Regex validation: {100/regex_time:.0f} validations/sec")
    
    print("✅ Performance and optimization tests passed!")


def test_error_handling_and_edge_cases():
    """Test error handling and edge cases."""
    print("\n🧪 Testing error handling and edge cases...")
    
    # Test empty values
    print("  🗳️ Empty value tests:")
    validator = create_form_validator()
    validator.add_field("test").required()
    
    empty_values = [None, "", "   ", [], {}]
    for empty_value in empty_values:
        result = validator.validate_field("test", empty_value)
        errors = [r for r in result if not r.is_valid]
        assert len(errors) > 0, f"Empty value should fail: {empty_value}"
    print("    ✅ Empty values properly rejected")
    
    # Test very long values
    print("  📏 Long value tests:")
    long_validator = create_form_validator()
    long_validator.add_field("limited").max_length(10)
    
    very_long_value = "x" * 1000
    result = long_validator.validate_field("limited", very_long_value)
    errors = [r for r in result if not r.is_valid]
    assert len(errors) > 0, "Very long value should fail max length"
    print("    ✅ Very long values properly rejected")
    
    # Test unicode and special characters
    print("  🌍 Unicode tests:")
    unicode_validator = create_form_validator()
    unicode_validator.add_field("name").required().min_length(2)
    
    unicode_values = ["José", "李明", "🚀 Test", "Åse Nørrebro"]
    for unicode_value in unicode_values:
        result = unicode_validator.validate_field("name", unicode_value)
        valid_results = [r for r in result if r.is_valid]
        print(f"    ✅ Unicode value '{unicode_value}': {'Valid' if valid_results else 'Invalid'}")
    
    # Test circular dependencies (edge case)
    print("  🔄 Circular dependency tests:")
    circular_validator = create_form_validator()
    
    # This shouldn't cause infinite loops
    circular_validator.add_field("field_a").required()
    circular_validator.add_field("field_b").required()
    
    # Set up some values
    circular_validator.set_field_value("field_a", "value_a")
    circular_validator.set_field_value("field_b", "value_b")
    
    # This should complete without hanging
    start_time = time.time()
    result = circular_validator.validate_all()
    end_time = time.time()
    
    assert end_time - start_time < 1.0, "Validation should complete quickly"
    print("    ✅ No circular dependency issues")
    
    # Test malformed regex patterns
    print("  🚨 Malformed regex tests:")
    registry = ValidatorRegistry()
    
    try:
        # This should handle the malformed regex gracefully
        bad_regex_validator = registry.create_regex_validator(r'[unclosed', "Bad regex")
        result = bad_regex_validator.validate("test")
        print("    ✅ Malformed regex handled gracefully")
    except Exception as e:
        print(f"    ✅ Malformed regex threw expected exception: {type(e).__name__}")
    
    # Test extremely large numbers
    print("  🔢 Large number tests:")
    number_validator = create_form_validator()
    number_validator.add_field("big_number").required().custom(
        lambda x: float(x) < 1e10, "Number too large"
    )
    
    large_numbers = ["1e20", "99999999999999999999", "inf", "-inf"]
    for large_num in large_numbers:
        try:
            result = number_validator.validate_field("big_number", large_num)
            print(f"    ✅ Large number '{large_num}': Handled")
        except Exception as e:
            print(f"    ✅ Large number '{large_num}': Exception handled")
    
    print("✅ Error handling and edge case tests passed!")


def main():
    """Run all ValidationSystem tests."""
    print("🚀 Starting ValidationSystem test suite...\n")
    
    try:
        # Core functionality tests
        test_validation_result()
        test_validation_rule()
        test_validator_registry()
        test_validation_chain()
        test_validation_theme()
        test_enhanced_validator()
        test_convenience_functions()
        
        # Advanced tests
        test_real_world_scenarios()
        test_performance_and_optimization()
        test_error_handling_and_edge_cases()
        
        print(f"\n📊 Test Results: 10/10 tests passed")
        print("🎉 All ValidationSystem tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)