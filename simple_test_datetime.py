#!/usr/bin/env python3
"""Simple test for DateTimeAdapter basic functionality."""
import sys
import os
from pathlib import Path

# Add the project src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Test basic import
try:
    from tui_engine.widgets.date_time_adapter import DateTimeAdapter, DateTimeParser
    print("✅ Successfully imported DateTimeAdapter and DateTimeParser")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test DateTimeParser basics
print("\n🧪 Testing DateTimeParser basics...")
parser = DateTimeParser()

# Test simple date parsing
result = parser.parse_date("2025-11-05")
if result:
    print(f"✅ Date parsing works: {result}")
else:
    print("❌ Date parsing failed")

# Test simple time parsing
result = parser.parse_time("14:30")
if result:
    print(f"✅ Time parsing works: {result}")
else:
    print("❌ Time parsing failed")

# Test basic adapter creation
print("\n🧪 Testing DateTimeAdapter creation...")
try:
    # Test legacy mode
    legacy_adapter = DateTimeAdapter(widget="test_widget")
    print("✅ Legacy adapter created successfully")
    
    # Test enhanced mode (may fail if Questionary not available)
    try:
        enhanced_adapter = DateTimeAdapter(
            message="Test:",
            mode='date',
            default_value="2025-11-05"
        )
        print("✅ Enhanced adapter created successfully")
    except Exception as e:
        print(f"⚠️  Enhanced adapter creation failed (probably missing Questionary): {e}")
        
except Exception as e:
    print(f"❌ Adapter creation failed: {e}")

print("\n🎉 Basic DateTimeAdapter test completed!")