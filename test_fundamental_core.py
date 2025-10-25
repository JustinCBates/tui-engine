"""Test the fundamental core functionality."""

import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_basic_imports():
    """Test that basic imports work."""
    import questionary_extended as qe
    # Basic import should succeed and expose a __version__ attribute
    assert hasattr(qe, "__version__")

def test_core_prompts():
    """Test core prompt functionality."""
    import questionary_extended as qe

    # Creating prompt objects should not raise
    _ = qe.enhanced_text("Test text")
    _ = qe.number("Test number", min_value=0, max_value=100)
    _ = qe.rating("Test rating", max_rating=5)

def test_validators():
    """Test validator functionality."""
    import questionary_extended as qe

    # Validators should be instantiable
    _ = qe.NumberValidator(min_value=0, max_value=100)
    _ = qe.EmailValidator()

def test_progress_tracker():
    """Test progress tracker."""
    import questionary_extended as qe

    # ProgressTracker should be usable as a context manager
    with qe.ProgressTracker("Test Operation", total_steps=3) as progress:
        progress.step("Step 1")
        progress.step("Step 2")
        progress.step("Step 3")
        progress.complete("Test completed!")

    # If we reach here, the operations didn't raise
    assert True

def main():
    """Run all fundamental tests."""
    print("🧪 Testing Fundamental Core Implementation")
    print("=" * 50)
    
    # main() remains for CLI usage; pytest will run individual test_* functions
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
        try:
            test_func()
            results.append(True)
        except Exception:
            results.append(False)

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