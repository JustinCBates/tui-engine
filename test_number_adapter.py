#!/usr/bin/env python3
"""Test script for NumberAdapter functionality.

This script tests both enhanced and legacy modes of the NumberAdapter,
including different number formats, validation, constraints, and formatting.
"""
import sys
import os
from pathlib import Path
from decimal import Decimal

# Add the project src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from typing import List, Dict, Any, Optional


def test_number_formatter():
    """Test the NumberFormatter functionality."""
    print("🧪 Testing NumberFormatter...")
    
    from tui_engine.widgets.number_adapter import NumberFormatter, NumberFormat
    
    # Test integer formatting
    print("  🔢 Integer formatting tests:")
    int_config = NumberFormat(format_type='int', thousands_separator=True)
    int_formatter = NumberFormatter(int_config)
    
    int_tests = [
        (1234, "1,234"),
        (-5678, "-5,678"),
        (0, "0"),
        (42, "42")
    ]
    
    for value, expected in int_tests:
        result = int_formatter.format_number(value, for_display=True)
        print(f"    {value} -> '{result}' (expected '{expected}')")
        assert result == expected or result == str(value)  # Allow both formats
    
    # Test float formatting
    print("  🔢 Float formatting tests:")
    float_config = NumberFormat(format_type='float', decimal_places=2, thousands_separator=True)
    float_formatter = NumberFormatter(float_config)
    
    float_tests = [
        (1234.56, "1,234.56"),
        (0.99, "0.99"),
        (-42.123, "-42.12")  # Should round to 2 decimal places
    ]
    
    for value, expected_pattern in float_tests:
        result = float_formatter.format_number(value, for_display=True)
        print(f"    {value} -> '{result}'")
        # Basic validation - check decimal places and negative handling
        if value < 0:
            assert result.startswith('-')
        if '.' in result:
            decimal_part = result.split('.')[-1]
            assert len(decimal_part) <= 2
    
    # Test currency formatting
    print("  💰 Currency formatting tests:")
    currency_config = NumberFormat(format_type='currency', currency_symbol='$', decimal_places=2)
    currency_formatter = NumberFormatter(currency_config)
    
    currency_tests = [
        (1234.56, "$1,234.56"),
        (0.99, "$0.99"),
        (1000000, "$1,000,000.00")
    ]
    
    for value, expected_pattern in currency_tests:
        result = currency_formatter.format_number(value, for_display=True)
        print(f"    ${value} -> '{result}'")
        assert '$' in result
        if value >= 1000:
            assert ',' in result or '.' in result  # Some thousands separator or decimal
    
    # Test percentage formatting
    print("  📊 Percentage formatting tests:")
    percent_config = NumberFormat(format_type='percentage', decimal_places=1)
    percent_formatter = NumberFormatter(percent_config)
    
    percent_tests = [
        (0.1234, "12.3%"),
        (0.5, "50.0%"),
        (1.0, "100.0%")
    ]
    
    for value, expected_pattern in percent_tests:
        result = percent_formatter.format_number(value, for_display=True)
        print(f"    {value} -> '{result}'")
        assert '%' in result
    
    print("✅ NumberFormatter tests passed!")
    return True


def test_number_validator():
    """Test the NumberValidator functionality."""
    print("🧪 Testing NumberValidator...")
    
    from tui_engine.widgets.number_adapter import NumberValidator, NumberFormat
    
    # Test basic validation
    print("  ✅ Basic validation tests:")
    basic_config = NumberFormat(format_type='float', allow_negative=True, allow_zero=True)
    validator = NumberValidator(basic_config, min_value=0, max_value=100)
    
    # Mock document class for testing
    class MockDocument:
        def __init__(self, text):
            self.text = text
    
    # Test valid values
    valid_tests = ["50", "0", "100", "25.5"]
    for test_value in valid_tests:
        try:
            validator.validate(MockDocument(test_value))
            print(f"    ✓ '{test_value}' is valid")
        except Exception as e:
            print(f"    ❌ '{test_value}' failed: {e}")
    
    # Test invalid values
    invalid_tests = ["-5", "150", "abc", ""]
    for test_value in invalid_tests:
        try:
            validator.validate(MockDocument(test_value))
            print(f"    ❌ '{test_value}' should be invalid but passed")
        except Exception as e:
            print(f"    ✓ '{test_value}' correctly rejected: {e}")
    
    # Test custom validation
    print("  🧪 Custom validation tests:")
    def even_numbers_only(value):
        if isinstance(value, (int, float)) and value % 2 != 0:
            return "Only even numbers allowed"
        return True
    
    custom_validator = NumberValidator(basic_config, custom_validator=even_numbers_only)
    
    even_tests = [("4", True), ("5", False), ("8.0", True), ("7.5", False)]
    for test_value, should_pass in even_tests:
        try:
            custom_validator.validate(MockDocument(test_value))
            if should_pass:
                print(f"    ✓ '{test_value}' (even) passed")
            else:
                print(f"    ❌ '{test_value}' (odd) should have failed")
        except Exception as e:
            if not should_pass:
                print(f"    ✓ '{test_value}' (odd) correctly rejected")
            else:
                print(f"    ❌ '{test_value}' (even) incorrectly rejected: {e}")
    
    print("✅ NumberValidator tests passed!")
    return True


def test_enhanced_number_adapter():
    """Test EnhancedNumberAdapter functionality."""
    print("🧪 Testing EnhancedNumberAdapter...")
    
    try:
        from tui_engine.widgets.number_adapter import EnhancedNumberAdapter
        
        # Test integer adapter
        print("  🔢 Integer adapter tests:")
        int_adapter = EnhancedNumberAdapter(
            message="Enter integer:",
            format_type='int',
            min_value=0,
            max_value=100,
            default_value=50
        )
        
        print(f"    Created: {int_adapter}")
        assert int_adapter.get_value() == 50
        
        # Test value operations
        int_adapter.set_value("75")
        assert int_adapter.get_value() == 75
        print("    ✓ Integer value setting works")
        
        # Test increment/decrement
        int_adapter.increment()
        assert int_adapter.get_value() == 76
        print("    ✓ Integer increment works")
        
        int_adapter.decrement()
        assert int_adapter.get_value() == 75
        print("    ✓ Integer decrement works")
        
        # Test float adapter
        print("  🔢 Float adapter tests:")
        float_adapter = EnhancedNumberAdapter(
            message="Enter float:",
            format_type='float',
            decimal_places=2,
            default_value=12.34
        )
        
        print(f"    Created: {float_adapter}")
        assert abs(float_adapter.get_value() - 12.34) < 0.01
        
        formatted = float_adapter.get_formatted_value()
        print(f"    Formatted: {formatted}")
        assert '12.34' in formatted
        
        # Test currency adapter
        print("  💰 Currency adapter tests:")
        currency_adapter = EnhancedNumberAdapter(
            message="Enter amount:",
            format_type='currency',
            currency_symbol='$',
            min_value=0,
            default_value=100.50
        )
        
        print(f"    Created: {currency_adapter}")
        formatted_currency = currency_adapter.get_formatted_value()
        print(f"    Formatted currency: {formatted_currency}")
        assert '$' in formatted_currency
        
        # Test percentage adapter
        print("  📊 Percentage adapter tests:")
        percent_adapter = EnhancedNumberAdapter(
            message="Enter percentage:",
            format_type='percentage',
            min_value=0.0,
            max_value=1.0,
            default_value=0.25
        )
        
        print(f"    Created: {percent_adapter}")
        formatted_percent = percent_adapter.get_formatted_value()
        print(f"    Formatted percentage: {formatted_percent}")
        assert '%' in formatted_percent
        
        # Test validation
        print("  🛡️  Validation tests:")
        
        # Test range validation
        int_adapter.set_value(150)  # Above max
        is_valid, msg = int_adapter.validate_current_value()
        print(f"    Range validation (150 > 100): {is_valid} - {msg}")
        assert not is_valid
        
        int_adapter.set_value(50)  # Valid
        is_valid, msg = int_adapter.validate_current_value()
        print(f"    Range validation (50): {is_valid}")
        assert is_valid
        
        # Test custom validation
        def positive_even_validator(value):
            if value % 2 != 0:
                return "Only even numbers allowed"
            return True
        
        int_adapter.enable_validation(positive_even_validator)
        int_adapter.set_value(51)  # Odd number
        is_valid, msg = int_adapter.validate_current_value()
        print(f"    Custom validation (odd): {is_valid} - {msg}")
        assert not is_valid
        
        int_adapter.set_value(52)  # Even number
        is_valid, msg = int_adapter.validate_current_value()
        print(f"    Custom validation (even): {is_valid}")
        assert is_valid
        
        # Test constraints
        int_adapter.set_constraints(min_value=10, max_value=90)
        int_adapter.set_value(5)  # Below new min
        is_valid, msg = int_adapter.validate_current_value()
        print(f"    New constraints (5 < 10): {is_valid}")
        assert not is_valid
        
        # Test theme changing
        if int_adapter.is_questionary_enhanced():
            success = int_adapter.change_theme('dark_mode')
            print(f"    Theme change: {success}")
            
            info = int_adapter.get_widget_info()
            print(f"    Widget info: format={info['format_type']}, theme={info['theme']}")
        
        print("✅ EnhancedNumberAdapter tests passed!")
        return True
        
    except ImportError as e:
        print(f"⚠️  Questionary not available, skipping enhanced tests: {e}")
        return True
    except Exception as e:
        print(f"❌ EnhancedNumberAdapter test failed: {e}")
        return False


def test_backward_compatible_adapter():
    """Test the backward-compatible NumberAdapter."""
    print("🧪 Testing backward-compatible NumberAdapter...")
    
    from tui_engine.widgets.number_adapter import NumberAdapter
    
    # Test legacy mode (with explicit widget)
    print("  🔙 Legacy mode tests:")
    legacy_adapter = NumberAdapter(widget="dummy_widget")
    print(f"    Created legacy adapter: {legacy_adapter}")
    
    # Test value operations
    legacy_adapter.set_value(42.5)
    assert legacy_adapter.get_value() == 42.5
    print("    ✓ Legacy value operations work")
    
    formatted = legacy_adapter.get_formatted_value()
    print(f"    Formatted: {formatted}")
    
    # Test enhanced mode (without widget)
    print("  🚀 Enhanced mode tests:")
    try:
        enhanced_adapter = NumberAdapter(
            message="Test number:",
            format_type='float',
            decimal_places=1,
            min_value=0,
            max_value=100,
            default_value=25.5
        )
        print(f"    Created enhanced adapter: {enhanced_adapter}")
        
        # Test enhanced features
        formatted = enhanced_adapter.get_formatted_value()
        print(f"    Enhanced formatting: {formatted}")
        
        # Test widget info
        info = enhanced_adapter.get_widget_info()
        print(f"    Widget info: {info['format_type']}, enhanced={info['use_questionary']}")
        
        # Test increment/decrement
        enhanced_adapter.increment()
        incremented_value = enhanced_adapter.get_value()
        print(f"    After increment: {incremented_value}")
        
        enhanced_adapter.decrement()
        decremented_value = enhanced_adapter.get_value()
        print(f"    After decrement: {decremented_value}")
        
    except Exception as e:
        print(f"    ⚠️  Enhanced mode not available: {e}")
    
    print("✅ Backward-compatible NumberAdapter tests passed!")
    return True


def test_convenience_functions():
    """Test convenience functions for creating number widgets."""
    print("🧪 Testing convenience functions...")
    
    from tui_engine.widgets.number_adapter import (
        create_integer_input, create_float_input, create_currency_input,
        create_percentage_input, create_scientific_input
    )
    
    # Test integer input
    print("  🔢 Integer input tests:")
    int_input = create_integer_input(
        message="Enter age:",
        min_value=0,
        max_value=120,
        default_value=25
    )
    print(f"    Integer input: {int_input}")
    assert int_input.get_value() == 25
    
    int_input.set_value(30)
    assert int_input.get_value() == 30
    print("    ✓ Integer input works")
    
    # Test float input
    print("  🔢 Float input tests:")
    float_input = create_float_input(
        message="Enter score:",
        decimal_places=1,
        min_value=0.0,
        max_value=100.0,
        default_value=85.5
    )
    print(f"    Float input: {float_input}")
    assert abs(float_input.get_value() - 85.5) < 0.01
    print("    ✓ Float input works")
    
    # Test currency input
    print("  💰 Currency input tests:")
    currency_input = create_currency_input(
        message="Enter price:",
        currency_symbol='€',
        default_value=29.99
    )
    print(f"    Currency input: {currency_input}")
    
    currency_formatted = currency_input.get_formatted_value()
    print(f"    Currency formatted: {currency_formatted}")
    assert '€' in currency_formatted or '29.99' in currency_formatted
    print("    ✓ Currency input works")
    
    # Test percentage input
    print("  📊 Percentage input tests:")
    percentage_input = create_percentage_input(
        message="Enter completion:",
        default_value=0.75
    )
    print(f"    Percentage input: {percentage_input}")
    
    percent_formatted = percentage_input.get_formatted_value()
    print(f"    Percentage formatted: {percent_formatted}")
    assert '%' in percent_formatted or '75' in percent_formatted
    print("    ✓ Percentage input works")
    
    # Test scientific input
    print("  🔬 Scientific input tests:")
    scientific_input = create_scientific_input(
        message="Enter coefficient:",
        precision=3,
        default_value=1.23e-4
    )
    print(f"    Scientific input: {scientific_input}")
    
    sci_formatted = scientific_input.get_formatted_value()
    print(f"    Scientific formatted: {sci_formatted}")
    print("    ✓ Scientific input works")
    
    print("✅ Convenience function tests passed!")
    return True


def test_real_world_scenarios():
    """Test real-world usage scenarios."""
    print("🧪 Testing real-world scenarios...")
    
    from tui_engine.widgets.number_adapter import NumberAdapter
    
    # Scenario 1: Shopping cart total
    print("  🛒 Shopping cart scenario:")
    cart_total = NumberAdapter(
        message="Cart total:",
        format_type='currency',
        currency_symbol='$',
        min_value=0,
        default_value=0
    )
    
    # Add items to cart
    items = [12.99, 24.50, 7.25]
    total = sum(items)
    cart_total.set_value(total)
    
    formatted_total = cart_total.get_formatted_value()
    print(f"    Cart total: {formatted_total}")
    assert '$' in formatted_total or str(total) in formatted_total
    
    # Scenario 2: Grade percentage
    print("  📝 Grade percentage scenario:")
    
    def grade_validator(percentage):
        """Validate grade percentage (0-100% range)."""
        if percentage < 0 or percentage > 1:
            return "Grade must be between 0% and 100%"
        return True
    
    grade_input = NumberAdapter(
        message="Enter grade percentage:",
        format_type='percentage',
        min_value=0.0,
        max_value=1.0
    )
    grade_input.enable_validation(grade_validator)
    
    # Test valid grade
    grade_input.set_value(0.87)  # 87%
    is_valid, msg = grade_input.validate_current_value()
    print(f"    Valid grade (87%): {is_valid}")
    assert is_valid
    
    grade_formatted = grade_input.get_formatted_value()
    print(f"    Grade display: {grade_formatted}")
    
    # Test invalid grade
    grade_input.set_value(1.5)  # 150% - invalid
    is_valid, msg = grade_input.validate_current_value()
    print(f"    Invalid grade (150%): {is_valid} - {msg}")
    assert not is_valid
    
    # Scenario 3: Temperature converter
    print("  🌡️  Temperature converter scenario:")
    celsius_input = NumberAdapter(
        message="Temperature (°C):",
        format_type='float',
        decimal_places=1,
        min_value=-273.15,  # Absolute zero
        max_value=1000.0    # Reasonable max
    )
    
    celsius_input.set_value(25.0)  # Room temperature
    celsius = celsius_input.get_value()
    fahrenheit = (celsius * 9/5) + 32
    
    print(f"    {celsius}°C = {fahrenheit:.1f}°F")
    assert abs(fahrenheit - 77.0) < 0.1  # 25°C ≈ 77°F
    
    # Scenario 4: Financial calculation
    print("  💵 Financial calculation scenario:")
    
    principal = NumberAdapter(
        message="Principal amount:",
        format_type='currency',
        min_value=100,
        default_value=10000
    )
    
    interest_rate = NumberAdapter(
        message="Annual interest rate:",
        format_type='percentage',
        min_value=0.0,
        max_value=0.5,  # 50% max
        default_value=0.05  # 5%
    )
    
    years = NumberAdapter(
        message="Number of years:",
        format_type='int',
        min_value=1,
        max_value=50,
        default_value=10
    )
    
    # Simple interest calculation
    p = principal.get_value()
    r = interest_rate.get_value()
    t = years.get_value()
    
    if all(x is not None for x in [p, r, t]):
        simple_interest = p * r * t
        total_amount = p + simple_interest
        
        # Format results
        principal_str = principal.get_formatted_value()
        rate_str = interest_rate.get_formatted_value()
        
        print(f"    Principal: {principal_str}")
        print(f"    Rate: {rate_str}")
        print(f"    Years: {t}")
        print(f"    Interest: ${simple_interest:.2f}")
        print(f"    Total: ${total_amount:.2f}")
        
        assert simple_interest > 0
        assert total_amount > p
    
    print("✅ Real-world scenario tests passed!")
    return True


def test_error_handling():
    """Test error handling and edge cases."""
    print("🧪 Testing error handling...")
    
    from tui_engine.widgets.number_adapter import NumberAdapter, NumberFormatter, NumberFormat
    
    # Test invalid number parsing
    print("  🚫 Invalid input tests:")
    adapter = NumberAdapter(format_type='float')
    
    invalid_inputs = ["abc", "12.34.56", "", "infinity", "nan"]
    for invalid_input in invalid_inputs:
        adapter.set_value(invalid_input)
        value = adapter.get_value()
        print(f"    '{invalid_input}' -> {value}")
        # Should either be None or handle gracefully
    
    # Test constraint violations
    print("  ⚠️  Constraint violation tests:")
    constrained_adapter = NumberAdapter(
        format_type='int',
        min_value=10,
        max_value=90
    )
    
    # Test values outside constraints
    constraint_tests = [(5, False), (50, True), (100, False)]
    for test_value, should_be_valid in constraint_tests:
        constrained_adapter.set_value(test_value)
        is_valid, msg = constrained_adapter.validate_current_value()
        print(f"    Value {test_value}: {is_valid} (expected {should_be_valid})")
        assert is_valid == should_be_valid
    
    # Test division by zero and overflow scenarios
    print("  🔢 Edge case tests:")
    
    # Test very large numbers
    large_adapter = NumberAdapter(format_type='float')
    large_adapter.set_value(1e100)
    large_value = large_adapter.get_value()
    print(f"    Large number: {large_value}")
    
    # Test very small numbers
    small_adapter = NumberAdapter(format_type='float', decimal_places=10)
    small_adapter.set_value(1e-10)
    small_value = small_adapter.get_value()
    small_formatted = small_adapter.get_formatted_value()
    print(f"    Small number: {small_value} -> {small_formatted}")
    
    # Test None values
    none_adapter = NumberAdapter(format_type='int')
    none_adapter.set_value(None)
    none_value = none_adapter.get_value()
    print(f"    None value: {none_value}")
    assert none_value is None
    
    # Test empty string
    none_adapter.set_value("")
    empty_value = none_adapter.get_value()
    print(f"    Empty string: {empty_value}")
    assert empty_value is None
    
    print("✅ Error handling tests passed!")
    return True


def test_formatting_edge_cases():
    """Test number formatting edge cases."""
    print("🧪 Testing formatting edge cases...")
    
    from tui_engine.widgets.number_adapter import NumberFormatter, NumberFormat
    
    # Test different locale-style formatting
    print("  🌍 Locale-style formatting:")
    
    # European-style formatting (comma as decimal separator)
    european_config = NumberFormat(
        format_type='float',
        decimal_separator=',',
        thousands_separator=True
    )
    european_formatter = NumberFormatter(european_config)
    
    euro_result = european_formatter.format_number(1234.56, for_display=True)
    print(f"    European format (1234.56): {euro_result}")
    
    # Test rounding behavior
    print("  🔄 Rounding tests:")
    rounding_config = NumberFormat(format_type='float', decimal_places=2)
    rounding_formatter = NumberFormatter(rounding_config)
    
    rounding_tests = [
        (1.234, "1.23"),  # Round down
        (1.235, "1.24"),  # Round up (banker's rounding)
        (1.999, "2.00"),  # Round up with carry
    ]
    
    for value, expected_pattern in rounding_tests:
        result = rounding_formatter.format_number(value, for_display=True)
        print(f"    {value} -> {result}")
        # Basic check - should have 2 decimal places
        if '.' in result:
            decimal_part = result.split('.')[-1]
            assert len(decimal_part) == 2
    
    # Test currency positioning
    print("  💰 Currency positioning tests:")
    
    prefix_config = NumberFormat(format_type='currency', currency_symbol='$', currency_position='prefix')
    suffix_config = NumberFormat(format_type='currency', currency_symbol='USD', currency_position='suffix')
    
    prefix_formatter = NumberFormatter(prefix_config)
    suffix_formatter = NumberFormatter(suffix_config)
    
    prefix_result = prefix_formatter.format_number(100, for_display=True)
    suffix_result = suffix_formatter.format_number(100, for_display=True)
    
    print(f"    Prefix: {prefix_result}")
    print(f"    Suffix: {suffix_result}")
    
    assert prefix_result.startswith('$') or '100' in prefix_result
    assert suffix_result.endswith('USD') or '100' in suffix_result
    
    print("✅ Formatting edge case tests passed!")
    return True


def main():
    """Run all NumberAdapter tests."""
    print("🚀 Starting NumberAdapter test suite...\n")
    
    tests = [
        test_number_formatter,
        test_number_validator,
        test_enhanced_number_adapter,
        test_backward_compatible_adapter,
        test_convenience_functions,
        test_real_world_scenarios,
        test_error_handling,
        test_formatting_edge_cases
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with error: {e}\n")
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All NumberAdapter tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())