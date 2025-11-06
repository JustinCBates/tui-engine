#!/usr/bin/env python3
"""
Questionary-TUI Engine Compatibility Test

This script verifies that Questionary and prompt-toolkit versions are compatible
and can work together in the TUI Engine environment.
"""

import sys
from typing import Dict, Any

def check_questionary_compatibility() -> Dict[str, Any]:
    """Check Questionary installation and compatibility."""
    result = {
        'questionary_available': False,
        'questionary_version': None,
        'prompt_toolkit_version': None,
        'compatibility_status': 'unknown',
        'errors': []
    }
    
    try:
        import questionary
        result['questionary_available'] = True
        result['questionary_version'] = questionary.__version__
        
        # Test basic questionary functionality
        # Create a simple prompt to verify it works
        style_test = questionary.Style([
            ('question', 'fg:#ff0066 bold'),
            ('answer', 'fg:#44ff00 bold'),
        ])
        
        # Verify we can create prompts without errors
        test_prompt = questionary.text(
            "Test prompt (not executed)", 
            style=style_test
        )
        
        result['compatibility_status'] = 'questionary_works'
        
    except ImportError as e:
        result['errors'].append(f"Questionary import error: {e}")
        return result
    except Exception as e:
        result['errors'].append(f"Questionary functionality error: {e}")
        
    try:
        import prompt_toolkit
        result['prompt_toolkit_version'] = prompt_toolkit.__version__
        
        # Test prompt-toolkit integration
        from prompt_toolkit.layout.containers import Window
        from prompt_toolkit.layout.controls import FormattedTextControl
        
        # Create a simple prompt-toolkit widget
        test_widget = Window(
            content=FormattedTextControl(text="Test widget"),
            height=1
        )
        
        result['compatibility_status'] = 'full_compatibility'
        
    except ImportError as e:
        result['errors'].append(f"Prompt-toolkit import error: {e}")
    except Exception as e:
        result['errors'].append(f"Prompt-toolkit functionality error: {e}")
        
    return result

def check_version_compatibility(questionary_version: str, prompt_toolkit_version: str) -> bool:
    """Check if the versions are compatible based on known compatibility matrix."""
    
    # Parse versions
    try:
        q_major, q_minor, q_patch = map(int, questionary_version.split('.'))
        p_major, p_minor, p_patch = map(int, prompt_toolkit_version.split('.'))
    except ValueError:
        return False
    
    # Compatibility rules:
    # - Questionary 2.0.1+ requires prompt-toolkit 3.0.43+
    # - Questionary 2.1.x is compatible with prompt-toolkit 3.0.43+
    
    if q_major == 2 and q_minor >= 0:
        if p_major == 3 and p_minor == 0 and p_patch >= 43:
            return True
        elif p_major == 3 and p_minor > 0:
            return True
    
    return False

def main():
    """Main compatibility check function."""
    print("🔍 Checking Questionary-TUI Engine Compatibility...")
    print("=" * 50)
    
    # Check compatibility
    result = check_questionary_compatibility()
    
    # Display results
    if result['questionary_available']:
        print(f"✅ Questionary: {result['questionary_version']}")
        print(f"✅ Prompt-toolkit: {result['prompt_toolkit_version']}")
        
        # Check version compatibility
        if result['questionary_version'] and result['prompt_toolkit_version']:
            compatible = check_version_compatibility(
                result['questionary_version'], 
                result['prompt_toolkit_version']
            )
            
            if compatible:
                print("✅ Version compatibility: PASSED")
                print(f"✅ Integration status: {result['compatibility_status']}")
                print("\n🎉 All compatibility checks passed!")
                print("TUI Engine is ready for Questionary integration.")
                return 0
            else:
                print("❌ Version compatibility: FAILED")
                print("⚠️  Version mismatch detected.")
                
    else:
        print("❌ Questionary not available")
    
    # Display errors if any
    if result['errors']:
        print("\n🚨 Errors encountered:")
        for error in result['errors']:
            print(f"   - {error}")
    
    print("\n❌ Compatibility check failed!")
    return 1

if __name__ == "__main__":
    sys.exit(main())