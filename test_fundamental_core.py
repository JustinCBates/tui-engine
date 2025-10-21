"""Test the fundamental core functionality."""

import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_basic_imports():
    """Test that basic imports work."""
    try:
        import questionary_extended as qe
        print("✅ Basic import successful")
        print(f"   Version: {qe.__version__}")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_core_prompts():
    """Test core prompt functionality."""
    try:
        import questionary_extended as qe
        
        # Test that we can create prompt objects (don't ask for input)
        text_prompt = qe.enhanced_text("Test text")
        print("✅ Enhanced text prompt created")
        
        number_prompt = qe.number("Test number", min_value=0, max_value=100)
        print("✅ Number prompt created")
        
        rating_prompt = qe.rating("Test rating", max_rating=5)
        print("✅ Rating prompt created")
        
        return True
    except Exception as e:
        print(f"❌ Core prompt test failed: {e}")
        return False

def test_validators():
    """Test validator functionality."""
    try:
        import questionary_extended as qe
        
        # Test number validator
        validator = qe.NumberValidator(min_value=0, max_value=100)
        print("✅ NumberValidator created")
        
        # Test email validator
        email_validator = qe.EmailValidator()
        print("✅ EmailValidator created")
        
        return True
    except Exception as e:
        print(f"❌ Validator test failed: {e}")
        return False

def test_progress_tracker():
    """Test progress tracker."""
    try:
        import questionary_extended as qe
        
        with qe.progress_tracker("Test Operation", total_steps=3) as progress:
            progress.step("Step 1")
            progress.step("Step 2") 
            progress.step("Step 3")
            progress.complete("Test completed!")
        
        print("✅ Progress tracker works")
        return True
    except Exception as e:
        print(f"❌ Progress tracker test failed: {e}")
        return False

def main():
    """Run all fundamental tests."""
    print("🧪 Testing Fundamental Core Implementation")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Core Prompts", test_core_prompts),
        ("Validators", test_validators),
        ("Progress Tracker", test_progress_tracker),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 30)
        result = test_func()
        results.append(result)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All fundamental tests passed! Core implementation is working.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)