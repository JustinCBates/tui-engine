"""Simple test script to verify the package works."""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import questionary_extended as qe
    
    print("✅ Package imported successfully!")
    print(f"Version: {qe.__version__}")
    
    # Test basic functionality
    print("\nTesting basic prompts...")
    
    # Test enhanced text (should fall back to regular questionary)
    name = qe.enhanced_text("What's your name?", default="Test User").ask()
    print(f"Name: {name}")
    
    # Test number input
    age = qe.number("What's your age?", min_value=0, max_value=150, allow_float=False).ask()
    print(f"Age: {age}")
    
    # Test rating
    rating = qe.rating("Rate this demo (1-5):", max_rating=5).ask()
    print(f"Rating: {rating}")
    
    print("\n🎉 All tests passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")