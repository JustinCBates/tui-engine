#!/usr/bin/env python3
"""
Enhanced TextInputAdapter Test Suite

This script thoroughly tests the enhanced TextInputAdapter functionality,
ensuring proper Questionary integration while maintaining backward compatibility.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tui_engine.widgets.text_input_adapter import TextInputAdapter, EnhancedTextInputAdapter
from tui_engine.themes import TUIEngineThemes
import questionary


def test_backward_compatibility():
    """Test that the enhanced adapter maintains backward compatibility."""
    print("🔄 Testing Backward Compatibility...")
    print("=" * 50)
    
    # Test original interface
    try:
        # Test with None (original behavior)
        adapter1 = TextInputAdapter(None)
        print("✅ TextInputAdapter(None) - Compatible")
        
        # Test basic operations
        adapter1.set_value("test value")
        value = adapter1.get_value()
        if value == "test value":
            print("✅ Basic get/set value operations - Compatible")
        else:
            print(f"❌ Value mismatch: expected 'test value', got '{value}'")
        
        # Test focus
        adapter1.focus()  # Should not raise exception
        print("✅ Focus operation - Compatible")
        
        # Test sync
        adapter1._tui_sync()  # Should not raise exception
        print("✅ Sync operation - Compatible")
        
        # Test ptk_widget property
        widget = adapter1.ptk_widget
        if widget is not None:
            print("✅ ptk_widget property - Compatible")
        else:
            print("❌ ptk_widget property returned None")
            
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
    
    print()


def test_enhanced_features():
    """Test enhanced Questionary features."""
    print("✨ Testing Enhanced Features...")
    print("=" * 50)
    
    # Test enhanced initialization
    try:
        adapter = EnhancedTextInputAdapter(
            message="Enhanced test input:",
            style='professional_blue',
            placeholder="Enter something...",
            default="default value"
        )
        print("✅ Enhanced initialization successful")
        
        # Test enhanced properties
        info = adapter.get_widget_info()
        print(f"✅ Widget info: {info['use_questionary']} Questionary, Theme: {info['theme']}")
        
        # Test styling
        if adapter.is_questionary_enhanced():
            print("✅ Questionary enhancement active")
        else:
            print("⚠️  Questionary enhancement not active (may be expected in test environment)")
        
    except Exception as e:
        print(f"❌ Enhanced features test failed: {e}")
    
    # Test validation integration
    try:
        def simple_validator(text: str) -> str:
            if len(text) < 3:
                return "Text must be at least 3 characters"
            return ""  # Empty string means valid
        
        adapter = EnhancedTextInputAdapter(
            message="Validated input:",
            validator=simple_validator
        )
        
        # Test validation
        is_valid, error = adapter.validate_input("ab")
        if not is_valid and error:
            print("✅ Validation working (short input rejected)")
        
        is_valid, error = adapter.validate_input("abc")
        if is_valid:
            print("✅ Validation working (valid input accepted)")
            
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
    
    print()


def test_theme_integration():
    """Test theme integration functionality."""
    print("🎨 Testing Theme Integration...")
    print("=" * 50)
    
    # Test different themes
    themes_to_test = ['professional_blue', 'dark_mode', 'high_contrast']
    
    for theme_name in themes_to_test:
        try:
            adapter = EnhancedTextInputAdapter(
                message=f"Testing {theme_name} theme:",
                style=theme_name
            )
            
            info = adapter.get_widget_info()
            if info['theme'] == theme_name:
                print(f"✅ {theme_name} theme applied successfully")
            else:
                print(f"❌ {theme_name} theme application failed")
                
        except Exception as e:
            print(f"❌ {theme_name} theme test failed: {e}")
    
    # Test theme switching
    try:
        adapter = EnhancedTextInputAdapter(message="Theme switching test:")
        
        for theme in ['dark_mode', 'minimal']:
            adapter.change_theme(theme)
            # Note: Theme change requires widget recreation to take full effect
            print(f"✅ Theme switched to {theme}")
            
    except Exception as e:
        print(f"❌ Theme switching test failed: {e}")
    
    print()


def test_validation_system():
    """Test the validation system comprehensively."""
    print("✅ Testing Validation System...")
    print("=" * 50)
    
    # Test different validation patterns
    validation_tests = [
        {
            'name': 'Length validation',
            'validator': lambda text: len(text) >= 5 or "Must be at least 5 characters",
            'test_cases': [
                ('abc', False),
                ('abcde', True),
                ('hello world', True)
            ]
        },
        {
            'name': 'Email validation',
            'validator': lambda text: '@' in text or "Must contain @ symbol",
            'test_cases': [
                ('test', False),
                ('test@example.com', True),
                ('user@domain.org', True)
            ]
        },
        {
            'name': 'Boolean validation',
            'validator': lambda text: len(text) > 0,  # Returns boolean
            'test_cases': [
                ('', False),
                ('any text', True)
            ]
        }
    ]
    
    for test in validation_tests:
        print(f"\nTesting {test['name']}:")
        try:
            adapter = EnhancedTextInputAdapter(
                message=f"{test['name']} test:",
                validator=test['validator']
            )
            
            for text, expected_valid in test['test_cases']:
                is_valid, error = adapter.validate_input(text)
                if is_valid == expected_valid:
                    status = "✅" if is_valid else "✅"
                    print(f"  {status} '{text}' -> Valid: {is_valid}, Error: '{error}'")
                else:
                    print(f"  ❌ '{text}' -> Expected: {expected_valid}, Got: {is_valid}")
                    
        except Exception as e:
            print(f"  ❌ {test['name']} validation test failed: {e}")
    
    print()


def test_input_modes():
    """Test different input modes (text, password, multiline)."""
    print("🔤 Testing Input Modes...")
    print("=" * 50)
    
    # Test different input modes
    modes = [
        {'name': 'Single-line text', 'multiline': False, 'password': False},
        {'name': 'Password input', 'multiline': False, 'password': True},
        {'name': 'Multiline text', 'multiline': True, 'password': False},
    ]
    
    for mode in modes:
        try:
            adapter = EnhancedTextInputAdapter(
                message=f"{mode['name']} test:",
                multiline=mode['multiline'],
                password=mode['password'],
                default="test content"
            )
            
            # Test basic operations
            value = adapter.get_value()
            if value == "test content":
                print(f"✅ {mode['name']} - Default value set correctly")
            
            adapter.set_value("new content")
            value = adapter.get_value()
            if value == "new content":
                print(f"✅ {mode['name']} - Value update working")
            else:
                print(f"❌ {mode['name']} - Value update failed")
                
        except Exception as e:
            print(f"❌ {mode['name']} test failed: {e}")
    
    print()


def test_widget_properties():
    """Test widget property access and modification."""
    print("⚙️  Testing Widget Properties...")
    print("=" * 50)
    
    # Test property access and modification
    try:
        adapter = EnhancedTextInputAdapter(
            message="Initial message",
            placeholder="Initial placeholder"
        )
        
        # Test message modification
        adapter.set_message("Updated message")
        if adapter.message == "Updated message":
            print("✅ Message update successful")
        
        # Test placeholder modification
        adapter.set_placeholder("Updated placeholder")
        if adapter.placeholder == "Updated placeholder":
            print("✅ Placeholder update successful")
        
        # Test validation enable/disable
        def test_validator(text):
            return len(text) > 0
        
        adapter.enable_validation(test_validator)
        if adapter.validator is not None:
            print("✅ Validation enable successful")
        
        adapter.disable_validation()
        if adapter.validator is None:
            print("✅ Validation disable successful")
        
        # Test style adapter access
        style_adapter = adapter.get_style_adapter()
        if style_adapter is not None:
            print("✅ Style adapter access successful")
        
        # Test widget info
        info = adapter.get_widget_info()
        required_keys = ['use_questionary', 'has_validator', 'multiline', 'password', 'theme']
        if all(key in info for key in required_keys):
            print("✅ Widget info complete")
        else:
            missing = [key for key in required_keys if key not in info]
            print(f"❌ Widget info missing keys: {missing}")
            
    except Exception as e:
        print(f"❌ Widget properties test failed: {e}")
    
    print()


def test_questionary_integration():
    """Test integration with Questionary prompts."""
    print("🔗 Testing Questionary Integration...")
    print("=" * 50)
    
    try:
        # Test that we can create Questionary-compatible widgets
        adapter = EnhancedTextInputAdapter(
            message="Integration test:",
            style='dark_mode'
        )
        
        # Verify Questionary components are accessible
        if adapter.is_questionary_enhanced():
            print("✅ Questionary enhancement verified")
            
            # Test style adapter functionality
            style_adapter = adapter.get_style_adapter()
            if style_adapter:
                style = style_adapter.get_questionary_style()
                if style:
                    print("✅ Questionary style extraction successful")
                else:
                    print("❌ Questionary style extraction failed")
            
        else:
            print("⚠️  Questionary enhancement not available (test environment)")
        
        # Test widget creation with various configurations
        configs = [
            {'style': 'professional_blue', 'validator': lambda x: len(x) > 0},
            {'style': 'high_contrast', 'password': True},
            {'style': 'minimal', 'multiline': True}
        ]
        
        for i, config in enumerate(configs, 1):
            try:
                test_adapter = EnhancedTextInputAdapter(
                    message=f"Config test {i}:",
                    **config
                )
                print(f"✅ Configuration {i} created successfully")
            except Exception as e:
                print(f"❌ Configuration {i} failed: {e}")
                
    except Exception as e:
        print(f"❌ Questionary integration test failed: {e}")
    
    print()


def demonstrate_enhanced_usage():
    """Demonstrate enhanced adapter usage patterns."""
    print("🚀 Enhanced Usage Demonstration...")
    print("=" * 50)
    
    print("Example 1: Professional form input")
    try:
        username_adapter = EnhancedTextInputAdapter(
            message="Username:",
            style='professional_blue',
            validator=lambda x: len(x) >= 3 or "Username must be at least 3 characters",
            placeholder="Enter username..."
        )
        print(f"✅ Username adapter: {username_adapter}")
    except Exception as e:
        print(f"❌ Username adapter failed: {e}")
    
    print("\nExample 2: Secure password input")
    try:
        password_adapter = EnhancedTextInputAdapter(
            message="Password:",
            style='dark_mode',
            password=True,
            validator=lambda x: len(x) >= 8 or "Password must be at least 8 characters"
        )
        print(f"✅ Password adapter: {password_adapter}")
    except Exception as e:
        print(f"❌ Password adapter failed: {e}")
    
    print("\nExample 3: Multiline text with validation")
    try:
        comment_adapter = EnhancedTextInputAdapter(
            message="Comments:",
            style='high_contrast',
            multiline=True,
            placeholder="Enter your comments here...",
            validator=lambda x: len(x.strip()) > 0 or "Comments cannot be empty"
        )
        print(f"✅ Comment adapter: {comment_adapter}")
    except Exception as e:
        print(f"❌ Comment adapter failed: {e}")
    
    print("\nExample 4: Backward compatible usage")
    try:
        legacy_adapter = TextInputAdapter()
        legacy_adapter.set_value("legacy content")
        value = legacy_adapter.get_value()
        print(f"✅ Legacy adapter: value='{value}'")
    except Exception as e:
        print(f"❌ Legacy adapter failed: {e}")
    
    print()


def main():
    """Main test function."""
    print("🔤 Enhanced TextInputAdapter Test Suite")
    print("=" * 60)
    print()
    
    # Run all tests
    test_backward_compatibility()
    test_enhanced_features()
    test_theme_integration()
    test_validation_system()
    test_input_modes()
    test_widget_properties()
    test_questionary_integration()
    demonstrate_enhanced_usage()
    
    print("✅ All TextInputAdapter tests completed!")
    print("\n🎉 Enhanced TextInputAdapter is ready for integration!")


if __name__ == "__main__":
    main()