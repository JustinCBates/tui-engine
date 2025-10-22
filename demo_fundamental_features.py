#!/usr/bin/env python3
"""
🎯 Demo: Fundamental Features of Questionary Extended

This demo showcases the core functionality we've implemented so far:
- Enhanced text input with validation
- Number validation with custom ranges
- Star rating system
- Progress tracking
- Integrated validators

Run this demo to see questionary-extended in action!
"""

import time
from questionary_extended import (
    enhanced_text, 
    number, 
    rating,
    NumberValidator,
    EmailValidator
)


def main():
    """Demonstrate the fundamental features of questionary-extended."""
    
    print("🚀 Welcome to Questionary Extended - Fundamental Features Demo")
    print("=" * 60)
    
    # 1. Enhanced Text Input with Email Validation
    print("\n📧 1. Enhanced Text with Email Validation")
    print("-" * 40)
    
    email_validator = EmailValidator()
    email = enhanced_text(
        message="What's your email address?",
        validator=email_validator,
        placeholder="user@example.com",
        default="test@example.com"
    ).ask()
    
    if email:
        print(f"✅ Email captured: {email}")
    
    # 2. Number Input with Range Validation
    print("\n🔢 2. Number Input with Range Validation")
    print("-" * 40)
    
    age_validator = NumberValidator(min_value=0, max_value=120, allow_float=False)
    age = number(
        message="How old are you?",
        validator=age_validator,
        default=25
    ).ask()
    
    if age is not None:
        print(f"✅ Age captured: {age}")
    
    # 3. Star Rating System
    print("\n⭐ 3. Star Rating System")
    print("-" * 40)
    
    satisfaction = rating(
        message="How satisfied are you with questionary-extended so far?",
        max_rating=5,
        icon="⭐"
    ).ask()
    
    if satisfaction is not None:
        print(f"✅ Rating: {satisfaction}/5 stars")
        if satisfaction >= 4:
            print("🎉 Awesome! We're glad you like it!")
        elif satisfaction >= 3:
            print("😊 Thanks! We'll keep improving!")
        else:
            print("😔 We'll work harder to make it better!")
    
    # 4. Progress Tracking Demo
    print("\n📊 4. Progress Tracking Demo")
    print("-" * 40)
    
    # Simulate a multi-step process
    tasks = [
        "Initializing system",
        "Loading configuration", 
        "Processing user data",
        "Generating results",
        "Finalizing output"
    ]
    
    from questionary_extended import ProgressTracker

    with ProgressTracker("Demo Process", total_steps=len(tasks)) as tracker:
        for i, task in enumerate(tasks, 1):
            tracker.update(i, task)
            time.sleep(0.8)  # Simulate work
    
    print("✅ Progress tracking completed!")
    
    # 5. Summary
    print("\n🎯 Demo Summary")
    print("=" * 60)
    print(f"✉️  Email: {email}")
    print(f"🎂 Age: {age}")
    print(f"⭐ Rating: {satisfaction}/5")
    print("\n🚀 These are just the fundamental features!")
    print("   The full questionary-extended package will include:")
    print("   • Advanced date/time pickers")
    print("   • Color selection prompts") 
    print("   • Tree/hierarchical selection")
    print("   • Multi-step form builders")
    print("   • And much more!")
    
    print("\n🎉 Thanks for trying questionary-extended!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo cancelled. Thanks for trying questionary-extended!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your installation and try again.")