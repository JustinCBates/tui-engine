#!/usr/bin/env python3
"""Demo script showcasing DateTimeAdapter capabilities.

This demo shows various use cases and features of the DateTimeAdapter,
including different modes, styling, validation, and real-world scenarios.
"""
import sys
import os
from pathlib import Path
from datetime import datetime, date, time, timedelta

# Add the project src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from tui_engine.widgets.date_time_adapter import (
    DateTimeAdapter, create_date_picker, create_time_picker, 
    create_datetime_picker, create_birthday_picker, create_event_scheduler
)


def demo_basic_functionality():
    """Demonstrate basic DateTimeAdapter functionality."""
    print("=" * 60)
    print("🎯 DateTimeAdapter Basic Functionality Demo")
    print("=" * 60)
    
    # Date mode demo
    print("\n📅 Date Mode Demo:")
    date_adapter = DateTimeAdapter(
        message="Select a date:",
        mode='date',
        default_value="2025-11-05",
        style='professional_blue'
    )
    
    print(f"   Current value: {date_adapter.get_value()}")
    print(f"   Formatted: {date_adapter.get_formatted_value('%B %d, %Y')}")
    
    # Test different date inputs
    test_dates = ["2025-12-25", "Christmas 2025", "tomorrow", "in 1 week"]
    for test_date in test_dates:
        date_adapter.set_value(test_date)
        value = date_adapter.get_value()
        if value:
            formatted = date_adapter.get_formatted_value('%B %d, %Y')
            print(f"   '{test_date}' -> {formatted}")
        else:
            print(f"   '{test_date}' -> Failed to parse")
    
    # Time mode demo
    print("\n🕐 Time Mode Demo:")
    time_adapter = DateTimeAdapter(
        message="Select a time:",
        mode='time',
        default_value="14:30",
        style='dark_mode'
    )
    
    print(f"   Current value: {time_adapter.get_value()}")
    print(f"   12-hour format: {time_adapter.get_formatted_value('%I:%M %p')}")
    print(f"   24-hour format: {time_adapter.get_formatted_value('%H:%M')}")
    
    # Test different time inputs
    test_times = ["9:00 AM", "2:30 PM", "23:45", "noon"]
    for test_time in test_times:
        time_adapter.set_value(test_time)
        value = time_adapter.get_value()
        if value:
            formatted = time_adapter.get_formatted_value('%I:%M %p')
            print(f"   '{test_time}' -> {formatted}")
    
    # DateTime mode demo
    print("\n📅🕐 DateTime Mode Demo:")
    datetime_adapter = DateTimeAdapter(
        message="Select date and time:",
        mode='datetime',
        default_value="2025-11-05 14:30",
        timezone_aware=True,
        style='high_contrast'
    )
    
    print(f"   Current value: {datetime_adapter.get_value()}")
    print(f"   ISO format: {datetime_adapter.get_formatted_value('%Y-%m-%dT%H:%M:%S')}")
    print(f"   Readable: {datetime_adapter.get_formatted_value('%A, %B %d, %Y at %I:%M %p')}")


def demo_themes_and_styling():
    """Demonstrate different themes and styling options."""
    print("=" * 60)
    print("🎨 Themes and Styling Demo")
    print("=" * 60)
    
    themes = ['professional_blue', 'dark_mode', 'high_contrast', 'classic_terminal', 'minimal']
    
    for theme in themes:
        print(f"\n🎨 Theme: {theme}")
        adapter = DateTimeAdapter(
            message=f"Date picker with {theme} theme:",
            mode='date',
            default_value="2025-11-05",
            style=theme
        )
        
        info = adapter.get_widget_info()
        print(f"   Widget info: theme={info['theme']}, mode={info['mode']}")
        print(f"   Current value: {adapter.get_formatted_value('%B %d, %Y')}")
        
        # Test theme switching
        if adapter.is_questionary_enhanced():
            next_theme = themes[(themes.index(theme) + 1) % len(themes)]
            adapter.change_theme(next_theme)
            updated_info = adapter.get_widget_info()
            print(f"   Switched to: {updated_info['theme']}")


def demo_validation_and_constraints():
    """Demonstrate validation and constraint features."""
    print("=" * 60)
    print("🛡️  Validation and Constraints Demo")
    print("=" * 60)
    
    # Date range constraints
    print("\n📅 Date Range Constraints:")
    range_adapter = DateTimeAdapter(
        message="Select date within range:",
        mode='date',
        min_date="2025-01-01",
        max_date="2025-12-31",
        style='professional_blue'
    )
    
    # Test valid date
    range_adapter.set_value("2025-06-15")
    is_valid, msg = range_adapter.validate_current_value()
    print(f"   Valid date (2025-06-15): {is_valid}")
    
    # Test invalid dates
    invalid_dates = ["2024-12-31", "2026-01-01"]
    for invalid_date in invalid_dates:
        range_adapter.set_value(invalid_date)
        is_valid, msg = range_adapter.validate_current_value()
        print(f"   Invalid date ({invalid_date}): {is_valid} - {msg}")
    
    # Custom validation
    print("\n🧪 Custom Validation:")
    
    def weekend_validator(selected_date):
        """Only allow weekdays (Monday-Friday)."""
        if isinstance(selected_date, date):
            if selected_date.weekday() >= 5:  # Saturday=5, Sunday=6
                return "Please select a weekday (Monday-Friday)"
        return True
    
    weekday_adapter = DateTimeAdapter(
        message="Select a weekday:",
        mode='date',
        default_value="2025-11-05",  # Tuesday
        style='dark_mode'
    )
    weekday_adapter.enable_validation(weekend_validator)
    
    # Test weekday (valid)
    weekday_adapter.set_value("2025-11-05")  # Tuesday
    is_valid, msg = weekday_adapter.validate_current_value()
    print(f"   Weekday (Tuesday): {is_valid}")
    
    # Test weekend (invalid)
    weekday_adapter.set_value("2025-11-09")  # Saturday
    is_valid, msg = weekday_adapter.validate_current_value()
    print(f"   Weekend (Saturday): {is_valid} - {msg}")
    
    # Age validation example
    print("\n👶 Age Validation:")
    
    def age_validator(birth_date):
        """Validate minimum age of 18."""
        if isinstance(birth_date, date):
            today = datetime.now().date()
            age = today.year - birth_date.year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
            if age < 18:
                return "Must be at least 18 years old"
            if age > 120:
                return "Invalid birth date"
        return True
    
    age_adapter = DateTimeAdapter(
        message="Enter your birth date:",
        mode='date',
        max_date=datetime.now().date(),
        style='high_contrast'
    )
    age_adapter.enable_validation(age_validator)
    
    # Test valid age
    valid_birth = datetime.now().date() - timedelta(days=25*365)  # ~25 years old
    age_adapter.set_value(valid_birth.strftime("%Y-%m-%d"))
    is_valid, msg = age_adapter.validate_current_value()
    print(f"   Adult (25 years): {is_valid}")
    
    # Test underage
    underage_birth = datetime.now().date() - timedelta(days=16*365)  # ~16 years old
    age_adapter.set_value(underage_birth.strftime("%Y-%m-%d"))
    is_valid, msg = age_adapter.validate_current_value()
    print(f"   Minor (16 years): {is_valid} - {msg}")


def demo_convenience_functions():
    """Demonstrate convenience functions for common use cases."""
    print("=" * 60)
    print("🚀 Convenience Functions Demo")
    print("=" * 60)
    
    # Birthday picker
    print("\n🎂 Birthday Picker:")
    birthday = create_birthday_picker()
    birthday.set_value("1990-05-15")
    birth_date = birthday.get_value()
    if birth_date:
        age = datetime.now().year - birth_date.year
        formatted_birth = birthday.get_formatted_value("%B %d, %Y")
        print(f"   Birth date: {formatted_birth}")
        print(f"   Approximate age: {age} years")
    
    # Event scheduler
    print("\n📅 Event Scheduler:")
    event = create_event_scheduler(timezone_aware=True)
    event.set_value("2025-11-15 14:30")
    event_time = event.get_value()
    if event_time:
        formatted_event = event.get_formatted_value("%A, %B %d, %Y at %I:%M %p")
        print(f"   Event time: {formatted_event}")
        
        # Convert to different timezone
        if event.convert_timezone('US/Pacific'):
            pacific_time = event.get_formatted_value()
            print(f"   Pacific time: {pacific_time}")
    
    # Date picker with constraints
    print("\n📋 Project Deadline Picker:")
    deadline = create_date_picker(
        message="Project deadline:",
        min_date=datetime.now().date(),  # Can't be in the past
        max_date=datetime.now().date() + timedelta(days=365),  # Within 1 year
        default_value="2025-12-31"
    )
    deadline_date = deadline.get_value()
    if deadline_date:
        days_remaining = (deadline_date - datetime.now().date()).days
        formatted_deadline = deadline.get_formatted_value("%B %d, %Y")
        print(f"   Deadline: {formatted_deadline}")
        print(f"   Days remaining: {days_remaining}")
    
    # Time picker for daily tasks
    print("\n⏰ Daily Task Scheduler:")
    task_time = create_time_picker(
        message="Daily standup time:",
        default_value="9:00 AM"
    )
    task_time.set_value("9:30 AM")
    time_value = task_time.get_value()
    if time_value:
        formatted_time = task_time.get_formatted_value("%I:%M %p")
        print(f"   Standup time: {formatted_time}")


def demo_relative_parsing():
    """Demonstrate relative date/time parsing capabilities."""
    print("=" * 60)
    print("🔄 Relative Date/Time Parsing Demo")
    print("=" * 60)
    
    adapter = DateTimeAdapter(
        message="Flexible date input:",
        mode='date',
        allow_relative=True,
        style='minimal'
    )
    
    relative_inputs = [
        "today",
        "tomorrow", 
        "yesterday",
        "next Monday",
        "in 3 days",
        "2 weeks ago",
        "in 1 month",
        "last Friday",
        "next weekend"
    ]
    
    print("   Relative date parsing examples:")
    for relative_input in relative_inputs:
        adapter.set_value(relative_input)
        parsed_date = adapter.get_value()
        if parsed_date:
            formatted = adapter.get_formatted_value("%A, %B %d, %Y")
            print(f"   '{relative_input}' -> {formatted}")
        else:
            print(f"   '{relative_input}' -> Could not parse")


def demo_timezone_support():
    """Demonstrate timezone awareness and conversion."""
    print("=" * 60)
    print("🌍 Timezone Support Demo")  
    print("=" * 60)
    
    # Create timezone-aware datetime adapter
    tz_adapter = DateTimeAdapter(
        message="Global meeting time:",
        mode='datetime',
        timezone_aware=True,
        default_timezone='UTC',
        style='professional_blue'
    )
    
    # Set a meeting time
    tz_adapter.set_value("2025-11-15 15:00")  # 3 PM UTC
    utc_time = tz_adapter.get_value()
    
    print(f"   Meeting time (UTC): {tz_adapter.get_formatted_value()}")
    
    # Convert to different timezones
    timezones = ['US/Eastern', 'US/Pacific', 'Europe/London', 'Asia/Tokyo']
    
    for timezone in timezones:
        if tz_adapter.convert_timezone(timezone):
            local_time = tz_adapter.get_formatted_value()
            print(f"   {timezone}: {local_time}")
        else:
            print(f"   {timezone}: Conversion failed")
    
    # Reset to UTC for comparison
    tz_adapter.convert_timezone('UTC')
    print(f"   Back to UTC: {tz_adapter.get_formatted_value()}")


def demo_calendar_integration():
    """Demonstrate calendar display capabilities."""
    print("=" * 60)
    print("📅 Calendar Integration Demo")
    print("=" * 60)
    
    from tui_engine.widgets.date_time_adapter import CalendarGenerator
    
    cal_gen = CalendarGenerator()
    
    # Show current month with today highlighted
    today = datetime.now().date()
    selected_date = today + timedelta(days=7)  # One week from today
    
    print(f"\n   Calendar for {today.strftime('%B %Y')}:")
    calendar_lines = cal_gen.generate_month_calendar(
        today.year, today.month, selected_date, today
    )
    
    for line in calendar_lines:
        print(f"   {line}")
    
    print(f"\n   Legend:")
    print(f"   (DD) = Today ({today.strftime('%m/%d')})")
    print(f"   [DD] = Selected ({selected_date.strftime('%m/%d')})")


def demo_real_world_scenarios():
    """Demonstrate real-world usage scenarios."""
    print("=" * 60)
    print("🌟 Real-World Scenarios Demo")
    print("=" * 60)
    
    # Scenario 1: Flight booking system
    print("\n✈️  Flight Booking System:")
    
    departure_date = create_date_picker(
        message="Departure date:",
        min_date=datetime.now().date(),
        default_value=(datetime.now().date() + timedelta(days=7)).strftime("%Y-%m-%d")
    )
    
    departure_time = create_time_picker(
        message="Departure time:",
        default_value="08:00"
    )
    
    print(f"   Departure: {departure_date.get_formatted_value('%B %d, %Y')} at {departure_time.get_formatted_value('%I:%M %p')}")
    
    # Scenario 2: Medical appointment scheduler
    print("\n🏥 Medical Appointment Scheduler:")
    
    def business_hours_validator(appointment_time):
        """Validate business hours (9 AM - 5 PM, weekdays only)."""
        if isinstance(appointment_time, datetime):
            # Check if weekday
            if appointment_time.weekday() >= 5:
                return "Appointments only available Monday-Friday"
            
            # Check if business hours
            hour = appointment_time.hour
            if hour < 9 or hour >= 17:
                return "Appointments only available 9 AM - 5 PM"
        
        return True
    
    appointment = create_datetime_picker(
        message="Appointment time:",
        timezone_aware=False
    )
    appointment.enable_validation(business_hours_validator)
    appointment.set_constraints(
        min_date=datetime.now().date() + timedelta(days=1)  # Next day earliest
    )
    
    # Test valid appointment
    next_tuesday = datetime.now().date() + timedelta(days=(1 - datetime.now().weekday()) % 7 + 1)
    appointment.set_value(f"{next_tuesday} 10:00")
    is_valid, msg = appointment.validate_current_value()
    
    if is_valid:
        apt_time = appointment.get_formatted_value("%A, %B %d at %I:%M %p")
        print(f"   Scheduled: {apt_time}")
    else:
        print(f"   Invalid appointment: {msg}")
    
    # Scenario 3: Log analysis tool
    print("\n📊 Log Analysis Tool:")
    
    log_start = create_datetime_picker(
        message="Analysis start time:",
        max_date=datetime.now()
    )
    log_start.set_value("2025-11-01 00:00")
    
    log_end = create_datetime_picker(
        message="Analysis end time:", 
        max_date=datetime.now()
    )
    log_end.set_value("2025-11-05 23:59")
    
    start_time = log_start.get_formatted_value("%Y-%m-%d %H:%M")
    end_time = log_end.get_formatted_value("%Y-%m-%d %H:%M")
    
    print(f"   Analyzing logs from {start_time} to {end_time}")
    
    # Calculate duration
    duration = log_end.get_value() - log_start.get_value()
    print(f"   Duration: {duration.days} days, {duration.seconds // 3600} hours")


def main():
    """Run all DateTimeAdapter demos."""
    print("🎭 DateTimeAdapter Comprehensive Demo")
    print("Showcasing all features and capabilities")
    print()
    
    demos = [
        demo_basic_functionality,
        demo_themes_and_styling,
        demo_validation_and_constraints,
        demo_convenience_functions,
        demo_relative_parsing,
        demo_timezone_support,
        demo_calendar_integration,
        demo_real_world_scenarios
    ]
    
    for i, demo_func in enumerate(demos, 1):
        try:
            demo_func()
            print()
        except Exception as e:
            print(f"❌ Demo {demo_func.__name__} failed: {e}")
            print()
    
    print("=" * 60)
    print("🎉 DateTimeAdapter Demo Complete!")
    print("=" * 60)
    print()
    print("Key features demonstrated:")
    print("  ✅ Date, Time, and DateTime modes")
    print("  ✅ Professional theme integration")
    print("  ✅ Validation and constraints")
    print("  ✅ Relative date parsing")
    print("  ✅ Timezone awareness and conversion")
    print("  ✅ Calendar visualization")
    print("  ✅ Convenience functions for common use cases")
    print("  ✅ Real-world integration scenarios")
    print("  ✅ Backward compatibility with legacy widgets")


if __name__ == "__main__":
    main()