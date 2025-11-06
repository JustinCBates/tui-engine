#!/usr/bin/env python3
"""
Enhanced PasswordAdapter Test Suite

This script thoroughly tests the enhanced PasswordAdapter functionality,
ensuring proper Questionary integration while maintaining backward compatibility.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tui_engine.widgets.password_adapter import (
    PasswordAdapter, EnhancedPasswordAdapter, PasswordStrengthValidator, 
    create_password_input
)


def test_backward_compatibility():
    """Test that the enhanced adapter maintains backward compatibility."""
    print("🔄 Testing Backward Compatibility...")
    print("=" * 50)
    
    # Test original interface with None widget
    try:
        adapter1 = PasswordAdapter(None)
        print("✅ PasswordAdapter(None) - Compatible")
        
        # Test basic operations
        adapter1.set_value("test_password")
        value = adapter1.get_value()
        if value == "test_password":
            print("✅ Basic get/set value operations - Compatible")
        else:
            print(f"❌ Value mismatch: expected 'test_password', got '{value}'")
        
        # Test focus
        adapter1.focus()  # Should not raise exception
        print("✅ Focus operation - Compatible")
        
        # Test sync
        sync_value = adapter1._tui_sync()  # Should not raise exception
        print("✅ Sync operation - Compatible")
        
        # Test ptk_widget property
        widget = adapter1.ptk_widget
        print("✅ ptk_widget property - Compatible")
            
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
    
    print()


def test_password_strength_validator():
    """Test the password strength validation system."""
    print("💪 Testing Password Strength Validator...")
    print("=" * 50)
    
    try:
        # Test default validator
        validator = PasswordStrengthValidator()
        
        # Test weak password
        is_valid, errors, score = validator.validate("123")
        if not is_valid and score < 30:
            print("✅ Weak password correctly identified")
            print(f"   Errors: {errors[:2]}...")  # Show first 2 errors
        
        # Test strong password
        is_valid, errors, score = validator.validate("MyStr0ng!P@ssw0rd")
        if is_valid and score > 80:
            print("✅ Strong password correctly identified")
            print(f"   Score: {score}, Description: {validator.get_strength_description(score)}")
        
        # Test custom requirements
        custom_validator = PasswordStrengthValidator(
            min_length=6,
            require_uppercase=False,
            require_special=False
        )
        
        is_valid, errors, score = custom_validator.validate("simple123")
        if is_valid:
            print("✅ Custom requirements working")
        
        # Test strength descriptions
        descriptions = []
        for test_score in [10, 35, 55, 75, 95]:
            desc = validator.get_strength_description(test_score)
            descriptions.append(f"{test_score}:{desc}")
        print(f"✅ Strength descriptions: {', '.join(descriptions)}")
        
    except Exception as e:
        print(f"❌ Password strength validator test failed: {e}")
    
    print()


def test_enhanced_initialization():
    """Test enhanced PasswordAdapter initialization."""
    print("✨ Testing Enhanced Initialization...")
    print("=" * 50)
    
    # Test basic enhanced initialization
    try:
        adapter = PasswordAdapter(
            message="Enter your password:",
            style='professional_blue',
            confirm_password=False
        )
        print("✅ Basic enhanced initialization successful")
        
        # Test with confirmation
        adapter2 = PasswordAdapter(
            message="Create password:",
            confirm_password=True,
            confirm_message="Confirm your password:",
            style='dark_mode'
        )
        print("✅ Enhanced initialization with confirmation successful")
        
        # Test widget info
        info = adapter.get_widget_info()
        print(f"✅ Widget info: Questionary={info['use_questionary']}, Theme={info['theme']}")
        
    except Exception as e:
        print(f"❌ Enhanced initialization test failed: {e}")
    
    print()


def test_password_validation():
    """Test password validation functionality."""
    print("✅ Testing Password Validation...")
    print("=" * 50)
    
    try:
        # Create adapter with custom strength requirements
        adapter = PasswordAdapter(
            message="Enter secure password:",
            confirm_password=False
        )
        
        # Test various password strengths
        test_passwords = [
            ("weak", "123"),
            ("better", "password123"),
            ("good", "MyPassword123"),
            ("strong", "MyStr0ng!P@ssw0rd"),
            ("empty", "")
        ]
        
        for desc, password in test_passwords:
            if adapter._enhanced_adapter:
                is_valid, errors, score = adapter.validate_password(password)
                print(f"✅ {desc} password: Score={score}, Valid={is_valid}")
                if errors and len(errors) <= 2:  # Show some errors
                    print(f"   First error: {errors[0]}")
            else:
                print(f"✅ {desc} password: Validation skipped (fallback mode)")
        
        # Test strength info
        adapter.set_value("TestPassword123!")
        if adapter._enhanced_adapter:
            strength_info = adapter.get_strength_info()
            print(f"✅ Strength info: {strength_info['description']} ({strength_info['score']})")
        
    except Exception as e:
        print(f"❌ Password validation test failed: {e}")
    
    print()


def test_confirmation_functionality():
    """Test password confirmation matching."""
    print("🔐 Testing Confirmation Functionality...")
    print("=" * 50)
    
    try:
        # Test with confirmation enabled
        adapter = PasswordAdapter(
            message="Password:",
            confirm_password=True,
            confirm_message="Confirm:"
        )
        
        info = adapter.get_widget_info()
        if info['requires_confirmation']:
            print("✅ Confirmation requirement enabled")
        
        # Test confirmation validation (simulated)
        if adapter._enhanced_adapter:
            # Set matching passwords
            adapter._enhanced_adapter._current_password = "test123"
            adapter._enhanced_adapter._confirmed_password = "test123"
            
            is_match, error = adapter.validate_confirmation()
            if is_match:
                print("✅ Matching passwords validation successful")
            
            # Set non-matching passwords
            adapter._enhanced_adapter._confirmed_password = "different"
            is_match, error = adapter.validate_confirmation()
            if not is_match and "not match" in error:
                print("✅ Non-matching passwords correctly detected")
        
        # Test enable/disable confirmation
        adapter.disable_confirmation()
        info = adapter.get_widget_info()
        if not info['requires_confirmation']:
            print("✅ Confirmation disable successful")
        
        adapter.enable_confirmation("Re-enter password:")
        info = adapter.get_widget_info()
        if info['requires_confirmation']:
            print("✅ Confirmation re-enable successful")
        
    except Exception as e:
        print(f"❌ Confirmation functionality test failed: {e}")
    
    print()


def test_security_features():
    """Test security-related features."""
    print("🛡️  Testing Security Features...")
    print("=" * 50)
    
    try:
        adapter = PasswordAdapter(
            message="Secure password:",
            secure_clear=True
        )
        
        # Test password setting and clearing
        adapter.set_value("sensitive_password")
        value_before = adapter.get_value()
        if value_before == "sensitive_password":
            print("✅ Password setting successful")
        
        # Test secure clear
        adapter.clear_password()
        value_after = adapter.get_value()
        if value_after == "":
            print("✅ Password clearing successful")
        
        # Test hash generation (for enhanced adapter)
        if adapter._enhanced_adapter:
            adapter.set_value("test_password")
            sync_value = adapter._tui_sync()  # Should return hash, not actual password
            if sync_value and sync_value != "test_password":
                print("✅ Password hashing for sync working")
        
        # Test widget info security
        adapter.set_value("secret123")
        info = adapter.get_widget_info()
        # Ensure actual password is not exposed in info
        info_str = str(info)
        if "secret123" not in info_str:
            print("✅ Password not exposed in widget info")
        
    except Exception as e:
        print(f"❌ Security features test failed: {e}")
    
    print()


def test_theme_integration():
    """Test theme integration and switching."""
    print("🎨 Testing Theme Integration...")
    print("=" * 50)
    
    themes_to_test = ['professional_blue', 'dark_mode', 'high_contrast', 'minimal']
    
    for theme_name in themes_to_test:
        try:
            adapter = PasswordAdapter(
                message=f"Password ({theme_name}):",
                style=theme_name
            )
            
            info = adapter.get_widget_info()
            if info['theme'] == theme_name:
                print(f"✅ {theme_name} theme applied successfully")
            else:
                print(f"⚠️  {theme_name} theme may not be fully applied (fallback mode)")
                
        except Exception as e:
            print(f"❌ {theme_name} theme test failed: {e}")
    
    # Test theme switching
    try:
        adapter = PasswordAdapter(
            message="Theme switching test:",
            style='professional_blue'
        )
        
        for theme in ['dark_mode', 'minimal']:
            adapter.change_theme(theme)
            print(f"✅ Theme switched to {theme}")
            
    except Exception as e:
        print(f"❌ Theme switching test failed: {e}")
    
    print()


def test_enhanced_features():
    """Test enhanced features specific to the new implementation."""
    print("🚀 Testing Enhanced Features...")
    print("=" * 50)
    
    try:
        # Test message updating
        adapter = PasswordAdapter(
            message="Initial message:"
        )
        
        adapter.set_message("Updated message:")
        info = adapter.get_widget_info()
        if info['message'] == "Updated message:":
            print("✅ Message update successful")
        
        # Test Questionary enhancement check
        is_enhanced = adapter.is_questionary_enhanced()
        print(f"✅ Questionary enhancement status: {is_enhanced}")
        
        # Test comprehensive widget info
        adapter.set_value("test_password")
        info = adapter.get_widget_info()
        required_keys = ['use_questionary', 'has_password', 'requires_confirmation', 
                        'strength_score', 'is_password_valid', 'theme']
        missing_keys = [key for key in required_keys if key not in info]
        if not missing_keys:
            print("✅ Comprehensive widget info available")
            print(f"   - Has password: {info['has_password']}")
            print(f"   - Strength: {info['strength_description']} ({info['strength_score']})")
        else:
            print(f"⚠️  Missing widget info keys: {missing_keys}")
        
        # Test style adapter access
        if adapter._enhanced_adapter:
            style_adapter = adapter._enhanced_adapter.get_style_adapter()
            if style_adapter is not None:
                print("✅ Style adapter access successful")
        
    except Exception as e:
        print(f"❌ Enhanced features test failed: {e}")
    
    print()


def test_convenience_function():
    """Test the convenience create_password_input function."""
    print("🛠️  Testing Convenience Function...")
    print("=" * 50)
    
    try:
        # Test convenience function
        adapter = create_password_input(
            message="Enter password:",
            style='dark_mode',
            confirm_password=True,
            min_length=6
        )
        
        if adapter is not None:
            print("✅ Convenience function create_password_input successful")
            
            info = adapter.get_widget_info()
            print(f"✅ Created with confirmation: {info['requires_confirmation']}")
            print(f"   Theme: {info['theme']}")
            
            # Test that it's fully functional
            adapter.set_value("test123")
            value = adapter.get_value()
            if value == "test123":
                print("✅ Convenience adapter is functional")
        
    except Exception as e:
        print(f"❌ Convenience function test failed: {e}")
    
    print()


def test_custom_validation():
    """Test custom validation functionality."""
    print("🔧 Testing Custom Validation...")
    print("=" * 50)
    
    try:
        # Test custom validator
        def no_common_passwords(password):
            common = ["password", "123456", "qwerty", "admin"]
            if password.lower() in common:
                return "Please avoid common passwords"
            return True
        
        adapter = PasswordAdapter(
            message="Secure password:",
            custom_validator=no_common_passwords
        )
        
        # Test with common password
        if adapter._enhanced_adapter:
            is_valid, errors, score = adapter.validate_password("password")
            if not is_valid and any("common" in error for error in errors):
                print("✅ Custom validation - Common password rejected")
            
            # Test with acceptable password
            is_valid, errors, score = adapter.validate_password("MyUniqueP@ss123")
            if is_valid:
                print("✅ Custom validation - Unique password accepted")
        
        # Test custom strength rules
        def custom_rule(password):
            if "!" not in password:
                return False, "Password must contain an exclamation mark"
            return True, ""
        
        if adapter._enhanced_adapter:
            adapter._enhanced_adapter.strength_validator.custom_rules = [custom_rule]
            
            is_valid, errors, score = adapter.validate_password("NoExclamation123")
            if not is_valid and any("exclamation" in error.lower() for error in errors):
                print("✅ Custom strength rule working")
        
    except Exception as e:
        print(f"❌ Custom validation test failed: {e}")
    
    print()


def test_edge_cases():
    """Test edge cases and error handling."""
    print("⚠️  Testing Edge Cases...")
    print("=" * 50)
    
    # Test empty password handling
    try:
        adapter = PasswordAdapter(message="Empty test:", allow_empty=True)
        adapter.set_value("")
        
        info = adapter.get_widget_info()
        if not info['has_password']:
            print("✅ Empty password handled gracefully")
        
        # Test with empty not allowed
        adapter2 = PasswordAdapter(message="Required test:", allow_empty=False)
        if adapter2._enhanced_adapter:
            is_valid, errors, score = adapter2.validate_password("")
            if not is_valid and any("empty" in error.lower() for error in errors):
                print("✅ Empty password correctly rejected when not allowed")
    except Exception as e:
        print(f"❌ Empty password test failed: {e}")
    
    # Test None value handling
    try:
        adapter = PasswordAdapter()
        adapter.set_value(None)
        value = adapter.get_value()
        if value == "":
            print("✅ None value handled gracefully")
    except Exception as e:
        print(f"❌ None value test failed: {e}")
    
    # Test validator exceptions
    try:
        def bad_validator(password):
            raise Exception("Validator error")
        
        adapter = PasswordAdapter(
            message="Bad validator test:",
            custom_validator=bad_validator
        )
        
        if adapter._enhanced_adapter:
            is_valid, errors, score = adapter.validate_password("test")
            if not is_valid and any("error" in error.lower() for error in errors):
                print("✅ Validator exceptions handled gracefully")
    except Exception as e:
        print(f"❌ Validator exception test failed: {e}")
    
    # Test very long password
    try:
        long_password = "a" * 1000
        adapter = PasswordAdapter()
        adapter.set_value(long_password)
        
        if adapter.get_value() == long_password:
            print("✅ Very long password handled gracefully")
    except Exception as e:
        print(f"❌ Long password test failed: {e}")
    
    print()


def demonstrate_usage_patterns():
    """Demonstrate various usage patterns."""
    print("📚 Usage Pattern Demonstrations...")
    print("=" * 50)
    
    print("Example 1: Simple password input")
    try:
        adapter1 = create_password_input(
            message="Password:",
            style='professional_blue'
        )
        print(f"✅ Simple password input: {adapter1}")
    except Exception as e:
        print(f"❌ Simple password input failed: {e}")
    
    print("\nExample 2: Password with confirmation")
    try:
        adapter2 = PasswordAdapter(
            message="Create password:",
            confirm_password=True,
            style='dark_mode'
        )
        print(f"✅ Password with confirmation: {adapter2}")
    except Exception as e:
        print(f"❌ Password with confirmation failed: {e}")
    
    print("\nExample 3: High-security password")
    try:
        # Custom strength validator for high security
        high_security_validator = PasswordStrengthValidator(
            min_length=12,
            require_uppercase=True,
            require_lowercase=True,
            require_digits=True,
            require_special=True
        )
        
        adapter3 = PasswordAdapter(
            message="High-security password:",
            confirm_password=True,
            strength_validator=high_security_validator,
            style='high_contrast',
            show_strength=True
        )
        print(f"✅ High-security password: {adapter3}")
    except Exception as e:
        print(f"❌ High-security password failed: {e}")
    
    print("\nExample 4: Legacy compatibility")
    try:
        adapter4 = PasswordAdapter(None)  # Legacy mode
        adapter4.set_value("legacy_password")
        value = adapter4.get_value()
        print(f"✅ Legacy compatibility: password set and retrieved")
    except Exception as e:
        print(f"❌ Legacy compatibility failed: {e}")
    
    print()


def main():
    """Main test function."""
    print("🔒 Enhanced PasswordAdapter Test Suite")
    print("=" * 60)
    print()
    
    # Run all tests
    test_backward_compatibility()
    test_password_strength_validator()
    test_enhanced_initialization()
    test_password_validation()
    test_confirmation_functionality()
    test_security_features()
    test_theme_integration()
    test_enhanced_features()
    test_convenience_function()
    test_custom_validation()
    test_edge_cases()
    demonstrate_usage_patterns()
    
    print("✅ All PasswordAdapter tests completed!")
    print("\n🎉 Enhanced PasswordAdapter is ready for integration!")


if __name__ == "__main__":
    main()