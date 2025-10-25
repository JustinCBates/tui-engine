#!/usr/bin/env python3
"""Test script to verify enhanced interactive demo functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'questionary-extended'))

import questionary_extended as qe
import questionary
from questionary_extended import EmailValidator, URLValidator, DateValidator
from questionary_extended import NumberValidator, RangeValidator, RegexValidator
from questionary_extended import ColorPalette
from datetime import date
import time


def test_code_samples():
    """Test that all code samples are syntactically correct."""
    
    print("🧪 Testing Code Samples...")
    
    # Import the get_code_sample function
    sys.path.insert(0, os.path.dirname(__file__))
    from interactive_demo import get_code_sample
    
    # Test components that should have code samples
    components = [
        "text", "password", "enhanced_text", "number", "integer", "rating",
        "select", "checkbox", "autocomplete", "rawselect", "confirm",
        "email_validator", "url_validator", "date_validator", 
        "number_validator", "range_validator", "regex_validator",
        "format_date", "format_number", "theming", "progress_tracker",
        "form", "path", "press_key", "print"
    ]
    
    for component in components:
        try:
            code = get_code_sample(component)
            if "# Code sample not available" not in code:
                # Try to compile the code (syntax check)
                compile(code, f"<{component}_sample>", "exec")
                print(f"  ✅ {component}: Code sample valid")
            else:
                print(f"  ⚠️  {component}: No code sample")
        except SyntaxError as e:
            print(f"  ❌ {component}: Syntax error - {e}")
        except Exception as e:
            print(f"  ⚠️  {component}: Other error - {e}")


def test_feature_demos():
    """Test that feature demo functions exist and are callable."""
    
    print("\n🧪 Testing Feature Demo Functions...")
    
    # Import demo functions
    sys.path.insert(0, os.path.dirname(__file__))
    import interactive_demo
    
    demo_functions = [
        "demo_text_features", "demo_password_features", "demo_enhanced_text_features",
        "demo_number_features", "demo_integer_features", "demo_rating_features",
        "demo_select_features", "demo_checkbox_features", "demo_autocomplete_features",
        "demo_rawselect_features", "demo_confirm_features", "demo_email_validator_features",
        "demo_url_validator_features", "demo_date_validator_features", 
        "demo_number_validator_features", "demo_range_validator_features", 
        "demo_regex_validator_features", "demo_format_date_features", 
        "demo_format_number_features", "demo_theming_features", 
        "demo_progress_tracker_features", "demo_form_features", 
        "demo_path_features", "demo_press_key_features", "demo_print_features"
    ]
    
    for func_name in demo_functions:
        if hasattr(interactive_demo, func_name):
            func = getattr(interactive_demo, func_name)
            if callable(func):
                print(f"  ✅ {func_name}: Available")
            else:
                print(f"  ❌ {func_name}: Not callable")
        else:
            print(f"  ❌ {func_name}: Missing")


def test_component_coverage():
    """Test component coverage in the interactive demo."""
    
    print("\n🧪 Testing Component Coverage...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from interactive_demo import COMPONENTS
    
    categories = list(COMPONENTS.keys())
    total_components = sum(len(COMPONENTS[cat]) for cat in categories)
    
    print(f"  📊 Total Categories: {len(categories)}")
    print(f"  📊 Total Components: {total_components}")
    
    for category in categories:
        component_count = len(COMPONENTS[category])
        print(f"    📁 {category}: {component_count} components")
        
        for component_key in COMPONENTS[category]:
            component_info = COMPONENTS[category][component_key]
            has_demo = 'demo' in component_info and callable(component_info['demo'])
            print(f"      {'✅' if has_demo else '❌'} {component_info['name']}")


def test_validators():
    """Test that validators work correctly."""
    
    print("\n🧪 Testing Validators...")
    
    # Test EmailValidator
    email_validator = EmailValidator()
    
    valid_emails = ["test@example.com", "user.name@domain.co.uk"]
    invalid_emails = ["invalid-email", "missing@", "@missing.com"]
    
    for email in valid_emails:
        try:
            result = email_validator.validate(email)
            if result is True or result is None:
                print(f"  ✅ EmailValidator: '{email}' - valid")
            else:
                print(f"  ❌ EmailValidator: '{email}' - should be valid")
        except Exception as e:
            print(f"  ⚠️  EmailValidator: '{email}' - error: {e}")
    
    for email in invalid_emails:
        try:
            result = email_validator.validate(email)
            if result is False or isinstance(result, str):
                print(f"  ✅ EmailValidator: '{email}' - correctly invalid")
            else:
                print(f"  ❌ EmailValidator: '{email}' - should be invalid")
        except Exception as e:
            print(f"  ⚠️  EmailValidator: '{email}' - error: {e}")


def test_utilities():
    """Test utility functions."""
    
    print("\n🧪 Testing Utilities...")
    
    # Test date formatting
    try:
        today = date.today()
        formatted = qe.format_date(today, "%Y-%m-%d")
        print(f"  ✅ format_date: {formatted}")
    except Exception as e:
        print(f"  ❌ format_date: {e}")
    
    # Test number formatting
    try:
        number = 1234567.89
        formatted = qe.format_number(number, thousands_sep=True)
        print(f"  ✅ format_number: {formatted}")
    except Exception as e:
        print(f"  ❌ format_number: {e}")


def test_theming():
    """Test theming system."""
    
    print("\n🧪 Testing Theming...")
    
    try:
        # Test built-in themes
        theme_count = len(qe.THEMES)
        print(f"  ✅ Built-in themes: {theme_count}")
        
        # Test custom theme creation
        custom_palette = ColorPalette(
            primary="#ff0000",
            secondary="#00ff00",
            success="#0000ff",
            error="#ffff00"
        )
        
        custom_theme = qe.create_theme("Test Theme", palette=custom_palette)
        print(f"  ✅ Custom theme: {custom_theme.name}")
        
    except Exception as e:
        print(f"  ❌ Theming error: {e}")


if __name__ == "__main__":
    print("🚀 Enhanced Interactive Demo Test Suite")
    print("=" * 50)
    
    try:
        test_code_samples()
        test_feature_demos()
        test_component_coverage()
        test_validators()
        test_utilities()
        test_theming()
        
        print("\n" + "=" * 50)
        print("✨ Test Suite Complete!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)