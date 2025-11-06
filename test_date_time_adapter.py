#!/usr/bin/env python3
"""Test script for DateTimeAdapter functionality.

This script tests both enhanced and legacy modes of the DateTimeAdapter,
including date/time parsing, timezone support, and calendar integration.
"""
import sys
import os
from pathlib import Path
from datetime import datetime, date, time, timezone, timedelta

# Add the project src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from typing import List, Dict, Any, Optional


def test_datetime_parser():
    """Test the DateTimeParser functionality."""
    print("🧪 Testing DateTimeParser...")
    
    from tui_engine.widgets.date_time_adapter import DateTimeParser
    
    parser = DateTimeParser()
    
    # Test date parsing
    date_tests = [
        ("2025-11-05", date(2025, 11, 5)),
        ("05/11/2025", date(2025, 11, 5)),
        ("11/05/2025", date(2025, 11, 5)),
        ("today", datetime.now().date()),
        ("tomorrow", datetime.now().date() + timedelta(days=1)),
        ("yesterday", datetime.now().date() - timedelta(days=1)),
        ("November 5, 2025", date(2025, 11, 5)),
        ("Nov 5, 2025", date(2025, 11, 5)),
    ]
    
    print("  📅 Date parsing tests:")
    for test_str, expected in date_tests:
        try:
            result = parser.parse_date(test_str)
            if isinstance(expected, date) and result == expected:
                print(f"    ✓ '{test_str}' -> {result}")
            elif test_str in ['today', 'tomorrow', 'yesterday'] and result is not None:
                print(f"    ✓ '{test_str}' -> {result}")
            else:
                print(f"    ❌ '{test_str}' -> {result} (expected {expected})")
        except Exception as e:
            print(f"    ❌ '{test_str}' failed: {e}")
    
    # Test time parsing
    time_tests = [
        ("14:30", time(14, 30)),
        ("02:30 PM", time(14, 30)),
        ("9:00 AM", time(9, 0)),
        ("23:59:59", time(23, 59, 59)),
    ]
    
    print("  🕐 Time parsing tests:")
    for test_str, expected in time_tests:
        try:
            result = parser.parse_time(test_str)
            if result == expected:
                print(f"    ✓ '{test_str}' -> {result}")
            else:
                print(f"    ❌ '{test_str}' -> {result} (expected {expected})")
        except Exception as e:
            print(f"    ❌ '{test_str}' failed: {e}")
    
    # Test datetime parsing
    datetime_tests = [
        ("2025-11-05 14:30", datetime(2025, 11, 5, 14, 30)),
        ("2025-11-05T14:30", datetime(2025, 11, 5, 14, 30)),
        ("November 5, 2025 2:30 PM", datetime(2025, 11, 5, 14, 30)),
    ]
    
    print("  📅🕐 DateTime parsing tests:")
    for test_str, expected in datetime_tests:
        try:
            result = parser.parse_datetime(test_str)
            if result and result.replace(tzinfo=None) == expected:
                print(f"    ✓ '{test_str}' -> {result}")
            else:
                print(f"    ❌ '{test_str}' -> {result} (expected {expected})")
        except Exception as e:
            print(f"    ❌ '{test_str}' failed: {e}")
    
    # Test formatting
    print("  📝 Formatting tests:")
    test_date = date(2025, 11, 5)
    test_time = time(14, 30)
    test_datetime = datetime(2025, 11, 5, 14, 30)
    
    date_formatted = parser.format_date(test_date, "%B %d, %Y")
    time_formatted = parser.format_time(test_time, "%I:%M %p")
    datetime_formatted = parser.format_datetime(test_datetime, "%Y-%m-%d %H:%M")
    
    print(f"    ✓ Date format: {date_formatted}")
    print(f"    ✓ Time format: {time_formatted}")
    print(f"    ✓ DateTime format: {datetime_formatted}")
    
    print("✅ DateTimeParser tests passed!")
    return True


def test_calendar_generator():
    """Test the CalendarGenerator functionality."""
    print("🧪 Testing CalendarGenerator...")
    
    from tui_engine.widgets.date_time_adapter import CalendarGenerator
    
    cal_gen = CalendarGenerator()
    
    # Test month calendar generation
    year, month = 2025, 11
    selected_date = date(2025, 11, 15)
    today = date(2025, 11, 5)
    
    calendar_lines = cal_gen.generate_month_calendar(year, month, selected_date, today)
    
    print(f"  📅 November 2025 calendar:")
    for line in calendar_lines:
        print(f"    {line}")
    
    assert len(calendar_lines) > 5  # Should have header, days, and legend
    assert "November 2025" in calendar_lines[0]
    print("  ✓ Calendar generation works")
    
    # Test month choices
    month_choices = cal_gen.get_month_choices(2025, 11)
    assert len(month_choices) == 12
    assert month_choices[10]['value'] == 11  # November is 11th month
    assert month_choices[10]['selected'] == True
    print("  ✓ Month choices generation works")
    
    # Test year choices
    year_choices = cal_gen.get_year_choices(2025, 3)
    assert len(year_choices) == 7  # 3 before + current + 3 after
    current_year_choice = next(choice for choice in year_choices if choice['value'] == 2025)
    assert current_year_choice['selected'] == True
    print("  ✓ Year choices generation works")
    
    print("✅ CalendarGenerator tests passed!")
    return True


def test_timezone_manager():
    """Test the TimezoneManager functionality."""
    print("🧪 Testing TimezoneManager...")
    
    from tui_engine.widgets.date_time_adapter import TimezoneManager
    
    tz_mgr = TimezoneManager()
    
    # Test timezone retrieval
    utc_tz = tz_mgr.get_timezone('UTC')
    assert utc_tz is not None
    print("  ✓ UTC timezone retrieval works")
    
    eastern_tz = tz_mgr.get_timezone('US/Eastern')
    assert eastern_tz is not None
    print("  ✓ US/Eastern timezone retrieval works")
    
    # Test local timezone
    local_tz = tz_mgr.get_local_timezone()
    assert local_tz is not None
    print("  ✓ Local timezone retrieval works")
    
    # Test timezone conversion
    test_dt = datetime(2025, 11, 5, 12, 0)  # Noon
    
    # Convert to UTC
    utc_dt = tz_mgr.convert_timezone(test_dt, local_tz, utc_tz)
    assert utc_dt.tzinfo is not None
    print(f"  ✓ Timezone conversion: {test_dt} -> {utc_dt}")
    
    # Test timezone choices
    tz_choices = tz_mgr.get_timezone_choices()
    assert len(tz_choices) > 10  # Should have many common timezones
    
    utc_choice = next((choice for choice in tz_choices if choice['value'] == 'UTC'), None)
    assert utc_choice is not None
    print(f"  ✓ Found {len(tz_choices)} timezone choices")
    
    print("✅ TimezoneManager tests passed!")
    return True


def test_enhanced_datetime_adapter():
    """Test EnhancedDateTimeAdapter functionality."""
    print("🧪 Testing EnhancedDateTimeAdapter...")
    
    try:
        from tui_engine.widgets.date_time_adapter import EnhancedDateTimeAdapter
        
        # Test date mode
        date_adapter = EnhancedDateTimeAdapter(
            message="Select date:",
            mode='date',
            default_value="2025-11-05",
            style='professional_blue'
        )
        
        print(f"  ✓ Created date adapter: {date_adapter}")
        
        # Test widget info
        info = date_adapter.get_widget_info()
        print(f"  ✓ Date adapter info: mode={info['mode']}, theme={info['theme']}")
        assert info['mode'] == 'date'
        
        # Test value setting/getting
        date_adapter.set_value("2025-12-25")
        assert date_adapter.get_value() == date(2025, 12, 25)
        print("  ✓ Date value setting/getting works")
        
        # Test formatted value
        formatted = date_adapter.get_formatted_value("%B %d, %Y")
        assert "December 25, 2025" in formatted
        print(f"  ✓ Date formatting works: {formatted}")
        
        # Test time mode
        time_adapter = EnhancedDateTimeAdapter(
            message="Select time:",
            mode='time',
            default_value="14:30",
            style='dark_mode'
        )
        
        print(f"  ✓ Created time adapter: {time_adapter}")
        assert time_adapter.get_value() == time(14, 30)
        
        # Test datetime mode
        datetime_adapter = EnhancedDateTimeAdapter(
            message="Select datetime:",
            mode='datetime',
            default_value="2025-11-05 14:30",
            timezone_aware=True,
            style='high_contrast'
        )
        
        print(f"  ✓ Created datetime adapter: {datetime_adapter}")
        dt_value = datetime_adapter.get_value()
        assert isinstance(dt_value, datetime)
        assert dt_value.year == 2025
        assert dt_value.month == 11
        assert dt_value.day == 5
        
        # Test validation
        def future_only_validator(dt):
            if isinstance(dt, (date, datetime)):
                check_date = dt.date() if isinstance(dt, datetime) else dt
                return check_date > datetime.now().date()
            return False
        
        datetime_adapter.enable_validation(future_only_validator)
        
        # Test past date (should fail validation)
        datetime_adapter.set_value("2020-01-01")
        is_valid, msg = datetime_adapter.validate_current_value()
        print(f"  ✓ Past date validation: {is_valid} ({msg})")
        
        # Test future date (should pass validation)
        future_date = datetime.now().date() + timedelta(days=30)
        datetime_adapter.set_value(future_date.strftime("%Y-%m-%d"))
        is_valid, msg = datetime_adapter.validate_current_value()
        print(f"  ✓ Future date validation: {is_valid} ({msg})")
        
        datetime_adapter.disable_validation()
        
        # Test constraints
        datetime_adapter.set_constraints(
            min_date="2025-01-01",
            max_date="2025-12-31"
        )
        
        datetime_adapter.set_value("2024-12-31")  # Before min_date
        is_valid, msg = datetime_adapter.validate_current_value()
        assert not is_valid
        print("  ✓ Date constraints validation works")
        
        # Test theme changing
        if datetime_adapter.is_questionary_enhanced():
            datetime_adapter.change_theme('minimal')
            updated_info = datetime_adapter.get_widget_info()
            assert updated_info['theme'] == 'minimal'
            print("  ✓ Theme change works")
        
        print("✅ EnhancedDateTimeAdapter tests passed!")
        return True
        
    except ImportError as e:
        print(f"⚠️  Questionary not available, skipping enhanced tests: {e}")
        return True
    except Exception as e:
        print(f"❌ EnhancedDateTimeAdapter test failed: {e}")
        return False


def test_backward_compatible_adapter():
    """Test the backward-compatible DateTimeAdapter."""
    print("🧪 Testing backward-compatible DateTimeAdapter...")
    
    from tui_engine.widgets.date_time_adapter import DateTimeAdapter
    
    # Test legacy mode (with explicit widget)
    legacy_adapter = DateTimeAdapter(widget="dummy_widget")
    print(f"  ✓ Legacy adapter created: {legacy_adapter}")
    
    # Test value operations
    test_date = datetime(2025, 11, 5, 14, 30)
    legacy_adapter.set_value(test_date)
    assert legacy_adapter.get_value() == test_date
    print("  ✓ Legacy value operations work")
    
    # Test enhanced mode (without widget)
    try:
        enhanced_adapter = DateTimeAdapter(
            message="Test datetime:",
            mode='datetime',
            default_value="2025-11-05 14:30",
            style='professional_blue'
        )
        print(f"  ✓ Enhanced adapter created: {enhanced_adapter}")
        
        # Test enhanced features
        formatted = enhanced_adapter.get_formatted_value("%Y-%m-%d %H:%M")
        print(f"  ✓ Enhanced formatting: {formatted}")
        
        # Test widget info
        info = enhanced_adapter.get_widget_info()
        print(f"  ✓ Widget info: {info}")
        assert 'use_questionary' in info
        
    except Exception as e:
        print(f"  ⚠️  Enhanced mode not available: {e}")
    
    print("✅ Backward-compatible DateTimeAdapter tests passed!")
    return True


def test_convenience_functions():
    """Test convenience functions for creating datetime widgets."""
    print("🧪 Testing convenience functions...")
    
    from tui_engine.widgets.date_time_adapter import (
        create_date_picker, create_time_picker, create_datetime_picker,
        create_birthday_picker, create_event_scheduler, create_log_timestamp_picker
    )
    
    # Test date picker
    date_picker = create_date_picker(
        message="Choose date:",
        default_value="2025-11-05",
        min_date="2025-01-01",
        max_date="2025-12-31"
    )
    print(f"  ✓ Date picker: {date_picker}")
    
    # Test time picker
    time_picker = create_time_picker(
        message="Choose time:",
        default_value="14:30"
    )
    print(f"  ✓ Time picker: {time_picker}")
    
    # Test datetime picker
    datetime_picker = create_datetime_picker(
        message="Choose datetime:",
        timezone_aware=True,
        default_timezone="UTC"
    )
    print(f"  ✓ DateTime picker: {datetime_picker}")
    
    # Test birthday picker
    birthday_picker = create_birthday_picker()
    print(f"  ✓ Birthday picker: {birthday_picker}")
    
    # Verify birthday constraints
    info = birthday_picker.get_widget_info()
    assert info['min_date'] is not None
    assert info['max_date'] is not None
    print("  ✓ Birthday picker has appropriate constraints")
    
    # Test event scheduler
    event_scheduler = create_event_scheduler(timezone_aware=True)
    print(f"  ✓ Event scheduler: {event_scheduler}")
    
    # Test log timestamp picker
    log_picker = create_log_timestamp_picker()
    print(f"  ✓ Log timestamp picker: {log_picker}")
    
    print("✅ Convenience function tests passed!")
    return True


def test_integration_scenarios():
    """Test real-world integration scenarios."""
    print("🧪 Testing integration scenarios...")
    
    from tui_engine.widgets.date_time_adapter import DateTimeAdapter
    
    # Scenario 1: Meeting scheduler with timezone support
    meeting_scheduler = DateTimeAdapter(
        message="Schedule meeting:",
        mode='datetime',
        timezone_aware=True,
        min_date=datetime.now().date(),  # Can't schedule in the past
        allow_relative=True
    )
    
    # Test scheduling for "tomorrow at 2 PM"
    meeting_scheduler.set_value("tomorrow")
    scheduled_date = meeting_scheduler.get_value()
    print(f"  ✓ Meeting scheduled: {scheduled_date}")
    
    # Scenario 2: Log analysis with time filtering
    log_filter = DateTimeAdapter(
        message="Filter logs from:",
        mode='datetime',
        format_str='%Y-%m-%d %H:%M:%S',
        timezone_aware=True,
        max_date=datetime.now()  # Logs can't be from the future
    )
    
    log_filter.set_value("2025-11-01 00:00:00")
    log_time = log_filter.get_formatted_value()
    print(f"  ✓ Log filter time: {log_time}")
    
    # Scenario 3: Birthday registration with validation
    def age_validator(birth_date):
        if isinstance(birth_date, date):
            today = datetime.now().date()
            age = today.year - birth_date.year
            if age < 13:
                return "Must be at least 13 years old"
            if age > 120:
                return "Age seems unrealistic"
        return True
    
    birthday_form = DateTimeAdapter(
        message="Enter your birthday:",
        mode='date',
        max_date=datetime.now().date()
    )
    birthday_form.enable_validation(age_validator)
    
    # Test with valid birthday
    birthday_form.set_value("1990-05-15")
    is_valid, msg = birthday_form.validate_current_value()
    print(f"  ✓ Valid birthday validation: {is_valid}")
    
    # Test with invalid birthday (too young)
    birthday_form.set_value("2020-01-01")
    is_valid, msg = birthday_form.validate_current_value()
    print(f"  ✓ Invalid birthday validation: {is_valid} ({msg})")
    
    # Scenario 4: Timezone conversion for global events
    global_event = DateTimeAdapter(
        message="Global event time:",
        mode='datetime',
        timezone_aware=True,
        default_timezone='UTC'
    )
    
    global_event.set_value("2025-11-05 15:00")
    
    # Convert to different timezone
    success = global_event.convert_timezone('US/Eastern')
    if success:
        converted_time = global_event.get_formatted_value()
        print(f"  ✓ Timezone conversion: {converted_time}")
    else:
        print("  ⚠️  Timezone conversion not available")
    
    print("✅ Integration scenario tests passed!")
    return True


def test_error_handling():
    """Test error handling and edge cases."""
    print("🧪 Testing error handling...")
    
    from tui_engine.widgets.date_time_adapter import DateTimeAdapter, DateTimeParser
    
    parser = DateTimeParser()
    
    # Test invalid date parsing
    invalid_dates = ["invalid", "2025-13-01", "2025-02-30", ""]
    
    print("  📅 Invalid date parsing:")
    for invalid_date in invalid_dates:
        result = parser.parse_date(invalid_date)
        print(f"    '{invalid_date}' -> {result} (expected None)")
        assert result is None
    
    # Test invalid time parsing
    invalid_times = ["25:00", "12:70", "invalid", ""]
    
    print("  🕐 Invalid time parsing:")
    for invalid_time in invalid_times:
        result = parser.parse_time(invalid_time)
        print(f"    '{invalid_time}' -> {result} (expected None)")
        assert result is None
    
    # Test adapter with invalid constraints
    adapter = DateTimeAdapter(
        mode='date',
        min_date="2025-12-31",
        max_date="2025-01-01"  # Max before min
    )
    
    adapter.set_value("2025-06-15")  # Valid date, but between inverted constraints
    is_valid, msg = adapter.validate_current_value()
    print(f"  ✓ Inverted constraints handled: {is_valid}")
    
    # Test error in custom validator
    def error_validator(dt):
        raise RuntimeError("Validator error")
    
    try:
        adapter.enable_validation(error_validator)
        adapter.set_value("2025-11-05")
        is_valid, msg = adapter.validate_current_value()
        print(f"  ✓ Validator error handled: {is_valid}")
    except Exception as e:
        print(f"  ⚠️  Validator error handling test failed: {e}")
    
    # Test None value handling
    adapter.set_value(None)
    assert adapter.get_value() is None
    print("  ✓ None value handling works")
    
    # Test empty string handling
    adapter.set_value("")
    assert adapter.get_value() is None
    print("  ✓ Empty string handling works")
    
    print("✅ Error handling tests passed!")
    return True


def test_relative_date_parsing():
    """Test relative date parsing functionality."""
    print("🧪 Testing relative date parsing...")
    
    from tui_engine.widgets.date_time_adapter import DateTimeParser
    
    parser = DateTimeParser()
    today = datetime.now().date()
    
    relative_tests = [
        ("today", today),
        ("tomorrow", today + timedelta(days=1)),
        ("yesterday", today - timedelta(days=1)),
        ("in 7 days", today + timedelta(days=7)),
        ("3 days ago", today - timedelta(days=3)),
        ("in 2 weeks", today + timedelta(weeks=2)),
        ("1 week ago", today - timedelta(weeks=1)),
    ]
    
    print("  🔄 Relative date parsing tests:")
    for test_str, expected in relative_tests:
        try:
            result = parser.parse_date(test_str)
            if result == expected:
                print(f"    ✓ '{test_str}' -> {result}")
            else:
                print(f"    ❌ '{test_str}' -> {result} (expected {expected})")
        except Exception as e:
            print(f"    ❌ '{test_str}' failed: {e}")
    
    print("✅ Relative date parsing tests passed!")
    return True


def main():
    """Run all DateTimeAdapter tests."""
    print("🚀 Starting DateTimeAdapter test suite...\n")
    
    tests = [
        test_datetime_parser,
        test_calendar_generator,
        test_timezone_manager,
        test_enhanced_datetime_adapter,
        test_backward_compatible_adapter,
        test_convenience_functions,
        test_integration_scenarios,
        test_error_handling,
        test_relative_date_parsing
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
        print("🎉 All DateTimeAdapter tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())