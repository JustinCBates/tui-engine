#!/usr/bin/env python3
"""Quick verification of enhanced demo features."""

import os
import sys

# Add paths
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "questionary-extended")
)
sys.path.insert(0, os.path.dirname(__file__))


def test_enhanced_features():
    """Test the enhanced features without user interaction."""

    print("🔍 Verifying Enhanced Demo Features")
    print("=" * 50)

    # Test 1: Import the enhanced demo
    try:
        from interactive_demo import (
            COMPONENT_CATALOG,
            get_code_sample,
        )

        print("✅ Enhanced demo imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

    # Test 2: Check code samples
    try:
        sample = get_code_sample("text")
        if "import questionary" in sample and "questionary.text" in sample:
            print("✅ Code samples working")
        else:
            print("❌ Code samples malformed")
            return False
    except Exception as e:
        print(f"❌ Code sample error: {e}")
        return False

    # Test 3: Check component coverage
    try:
        total_components = sum(len(COMPONENT_CATALOG[cat]) for cat in COMPONENT_CATALOG)
        if total_components >= 20:  # Should have at least 20 components
            print(f"✅ Component coverage: {total_components} components")
        else:
            print(f"❌ Low component coverage: {total_components}")
            return False
    except Exception as e:
        print(f"❌ Component coverage error: {e}")
        return False

    # Test 4: Check feature demo functions exist
    try:
        demo_functions = [
            "demo_text_features",
            "demo_number_features",
            "demo_select_features",
            "demo_email_validator_features",
            "demo_theming_features",
        ]

        import interactive_demo

        missing_functions = []

        for func_name in demo_functions:
            if not hasattr(interactive_demo, func_name):
                missing_functions.append(func_name)

        if not missing_functions:
            print("✅ Feature demo functions available")
        else:
            print(f"❌ Missing demo functions: {missing_functions}")
            return False

    except Exception as e:
        print(f"❌ Feature demo error: {e}")
        return False

    # Test 5: Test a sample code compilation
    try:
        code_samples = [
            get_code_sample("text"),
            get_code_sample("select"),
            get_code_sample("email_validator"),
        ]

        for i, code in enumerate(code_samples):
            compile(code, f"<sample_{i}>", "exec")

        print("✅ Code samples compile successfully")
    except Exception as e:
        print(f"❌ Code compilation error: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 All enhanced features verified successfully!")
    return True


if __name__ == "__main__":
    success = test_enhanced_features()
    if not success:
        sys.exit(1)
