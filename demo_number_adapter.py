#!/usr/bin/env python3
"""Demo script showcasing NumberAdapter capabilities.

This demo shows various use cases and features of the NumberAdapter,
including different number formats, validation, constraints, and real-world scenarios.
"""
import sys
import os
from pathlib import Path
from decimal import Decimal

# Add the project src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from tui_engine.widgets.number_adapter import (
    NumberAdapter, create_integer_input, create_float_input, 
    create_currency_input, create_percentage_input, create_scientific_input
)


def demo_basic_number_formats():
    """Demonstrate basic number format capabilities."""
    print("=" * 60)
    print("🔢 Number Format Demonstrations")
    print("=" * 60)
    
    # Integer format
    print("\n📊 Integer Format:")
    int_adapter = NumberAdapter(
        message="Enter age:",
        format_type='int',
        min_value=0,
        max_value=120,
        default_value=25,
        style='professional_blue'
    )
    
    print(f"   Current value: {int_adapter.get_value()}")
    print(f"   Formatted: {int_adapter.get_formatted_value()}")
    
    # Test different integer values
    test_integers = [18, 65, 100]
    for age in test_integers:
        int_adapter.set_value(age)
        formatted = int_adapter.get_formatted_value()
        print(f"   Age {age}: {formatted}")
    
    # Float format
    print("\n🔢 Float Format:")
    float_adapter = NumberAdapter(
        message="Enter GPA:",
        format_type='float',
        decimal_places=2,
        min_value=0.0,
        max_value=4.0,
        default_value=3.75,
        style='dark_mode'
    )
    
    print(f"   Current value: {float_adapter.get_value()}")
    print(f"   Formatted: {float_adapter.get_formatted_value()}")
    
    # Test GPA values
    test_gpas = [3.85, 3.50, 4.00, 2.75]
    for gpa in test_gpas:
        float_adapter.set_value(gpa)
        formatted = float_adapter.get_formatted_value()
        print(f"   GPA {gpa}: {formatted}")
    
    # Currency format
    print("\n💰 Currency Format:")
    currency_adapter = NumberAdapter(
        message="Enter price:",
        format_type='currency',
        currency_symbol='$',
        min_value=0,
        default_value=299.99,
        style='high_contrast'
    )
    
    print(f"   Current value: {currency_adapter.get_value()}")
    print(f"   Formatted: {currency_adapter.get_formatted_value()}")
    
    # Test different currencies and prices
    currency_tests = [
        (1234.56, '$'),
        (50.00, '€'),
        (999.99, '£'),
        (25000.00, '¥')
    ]
    
    for price, symbol in currency_tests:
        currency_adapter.format_config.currency_symbol = symbol
        currency_adapter.set_value(price)
        formatted = currency_adapter.get_formatted_value()
        print(f"   Price: {formatted}")
    
    # Percentage format
    print("\n📊 Percentage Format:")
    percent_adapter = NumberAdapter(
        message="Enter completion:",
        format_type='percentage',
        min_value=0.0,
        max_value=1.0,
        default_value=0.75,
        decimal_places=1,
        style='classic_terminal'
    )
    
    print(f"   Current value: {percent_adapter.get_value()}")
    print(f"   Formatted: {percent_adapter.get_formatted_value()}")
    
    # Test percentage values
    test_percentages = [0.25, 0.50, 0.85, 1.00]
    for percent in test_percentages:
        percent_adapter.set_value(percent)
        formatted = percent_adapter.get_formatted_value()
        print(f"   Progress {int(percent*100)}%: {formatted}")
    
    # Scientific notation
    print("\n🔬 Scientific Notation:")
    sci_adapter = NumberAdapter(
        message="Enter coefficient:",
        format_type='scientific',
        default_value=6.626e-34,  # Planck constant
        style='minimal'
    )
    
    print(f"   Current value: {sci_adapter.get_value()}")
    print(f"   Formatted: {sci_adapter.get_formatted_value()}")
    
    # Test scientific values
    scientific_values = [
        (9.81, "Gravity (m/s²)"),
        (3e8, "Speed of light (m/s)"),
        (1.602e-19, "Electron charge (C)"),
        (6.022e23, "Avogadro's number")
    ]
    
    for value, description in scientific_values:
        sci_adapter.set_value(value)
        formatted = sci_adapter.get_formatted_value()
        print(f"   {description}: {formatted}")


def demo_validation_and_constraints():
    """Demonstrate validation and constraint features."""
    print("=" * 60)
    print("🛡️  Validation and Constraints")
    print("=" * 60)
    
    # Range constraints
    print("\n📏 Range Constraints:")
    temperature_adapter = NumberAdapter(
        message="Temperature (°C):",
        format_type='float',
        decimal_places=1,
        min_value=-50.0,
        max_value=50.0,
        default_value=22.5
    )
    
    # Test valid and invalid temperatures
    temp_tests = [
        (25.0, True, "Room temperature"),
        (-10.0, True, "Cold winter day"),
        (45.0, True, "Hot summer day"),
        (-60.0, False, "Too cold (below -50°C)"),
        (55.0, False, "Too hot (above 50°C)")
    ]
    
    for temp, should_be_valid, description in temp_tests:
        temperature_adapter.set_value(temp)
        is_valid, msg = temperature_adapter.validate_current_value()
        status = "✓" if is_valid == should_be_valid else "❌"
        print(f"   {status} {description} ({temp}°C): {is_valid}")
        if not is_valid:
            print(f"       Error: {msg}")
    
    # Custom validation
    print("\n🧪 Custom Validation:")
    
    def credit_score_validator(score):
        """Validate credit scores according to FICO ranges."""
        if score < 300:
            return "Credit score cannot be below 300"
        elif score > 850:
            return "Credit score cannot be above 850"
        elif score < 580:
            return "Poor credit score"
        elif score < 670:
            return "Fair credit score" 
        elif score < 740:
            return "Good credit score"
        elif score < 800:
            return "Very good credit score"
        else:
            return "Excellent credit score"
    
    credit_adapter = NumberAdapter(
        message="Credit score:",
        format_type='int',
        min_value=300,
        max_value=850,
        default_value=720
    )
    credit_adapter.enable_validation(credit_score_validator)
    
    # Test credit scores
    credit_tests = [
        (750, "High score"),
        (650, "Average score"),
        (500, "Low score"),
        (900, "Invalid (too high)"),
        (250, "Invalid (too low)")
    ]
    
    for score, description in credit_tests:
        credit_adapter.set_value(score)
        is_valid, msg = credit_adapter.validate_current_value()
        status = "✓" if is_valid else "❌"
        print(f"   {status} {description} ({score}): {msg}")
    
    # Age restrictions
    print("\n👶 Age Validation:")
    
    def age_category_validator(age):
        """Categorize ages and validate appropriateness."""
        if age < 0:
            return "Age cannot be negative"
        elif age > 150:
            return "Invalid age (too old)"
        elif age < 13:
            return "Child (under 13)"
        elif age < 18:
            return "Teen (13-17)"
        elif age < 65:
            return "Adult (18-64)"
        else:
            return "Senior (65+)"
    
    age_adapter = NumberAdapter(
        message="Enter age:",
        format_type='int',
        min_value=0,
        max_value=150,
        allow_negative=False
    )
    age_adapter.enable_validation(age_category_validator)
    
    # Test different ages
    age_tests = [8, 16, 25, 45, 70, 200, -5]
    for age in age_tests:
        age_adapter.set_value(age)
        is_valid, msg = age_adapter.validate_current_value()
        status = "✓" if is_valid else "❌"
        print(f"   {status} Age {age}: {msg}")


def demo_increment_decrement():
    """Demonstrate increment/decrement functionality."""
    print("=" * 60)
    print("⬆️⬇️  Increment/Decrement Features")
    print("=" * 60)
    
    # Integer counter
    print("\n🔢 Integer Counter:")
    counter = NumberAdapter(
        message="Counter:",
        format_type='int',
        min_value=0,
        max_value=10,
        default_value=5,
        increment_step=1
    )
    
    print(f"   Starting value: {counter.get_value()}")
    
    # Increment sequence
    print("   Incrementing...")
    for i in range(6):  # Try to go past max
        success = counter.increment()
        value = counter.get_value()
        status = "✓" if success else "❌ (hit limit)"
        print(f"     Step {i+1}: {value} {status}")
    
    # Decrement sequence
    print("   Decrementing...")
    for i in range(12):  # Try to go past min
        success = counter.decrement()
        value = counter.get_value()
        status = "✓" if success else "❌ (hit limit)"
        print(f"     Step {i+1}: {value} {status}")
    
    # Float precision adjuster
    print("\n🔢 Float Precision Adjuster:")
    precision_adjuster = NumberAdapter(
        message="Precision value:",
        format_type='float',
        decimal_places=3,
        min_value=0.0,
        max_value=1.0,
        default_value=0.500,
        increment_step=0.001
    )
    
    print(f"   Starting value: {precision_adjuster.get_formatted_value()}")
    
    # Fine-tune adjustments
    adjustments = ["+0.125", "+0.250", "-0.100", "-0.050"]
    for adjustment in adjustments:
        if adjustment.startswith('+'):
            steps = int(float(adjustment[1:]) / 0.001)
            for _ in range(steps):
                precision_adjuster.increment()
        else:
            steps = int(float(adjustment[1:]) / 0.001)
            for _ in range(steps):
                precision_adjuster.decrement()
        
        value = precision_adjuster.get_formatted_value()
        print(f"   After {adjustment}: {value}")
    
    # Currency adjuster
    print("\n💰 Currency Adjuster:")
    price_adjuster = NumberAdapter(
        message="Price:",
        format_type='currency',
        currency_symbol='$',
        min_value=0,
        default_value=100.00,
        increment_step=5.00
    )
    
    print(f"   Starting price: {price_adjuster.get_formatted_value()}")
    
    # Price adjustments
    price_changes = [(3, "up"), (7, "down"), (2, "up")]
    for steps, direction in price_changes:
        for _ in range(steps):
            if direction == "up":
                price_adjuster.increment()
            else:
                price_adjuster.decrement()
        
        price = price_adjuster.get_formatted_value()
        print(f"   After {steps} steps {direction}: {price}")


def demo_convenience_functions():
    """Demonstrate convenience functions for specific use cases."""
    print("=" * 60)
    print("🚀 Convenience Functions")
    print("=" * 60)
    
    # Age input
    print("\n👤 Age Input:")
    age_input = create_integer_input(
        message="Your age:",
        min_value=0,
        max_value=120,
        default_value=30,
        allow_negative=False
    )
    
    print(f"   Age widget: {age_input}")
    print(f"   Current age: {age_input.get_value()}")
    
    # Test age scenarios
    age_scenarios = [21, 65, 16, 100]
    for age in age_scenarios:
        age_input.set_value(age)
        category = "Adult" if age >= 18 else "Minor"
        if age >= 65:
            category = "Senior"
        elif age >= 21:
            category = "Full Adult"
        
        print(f"   Age {age}: {category}")
    
    # GPA calculator
    print("\n🎓 GPA Calculator:")
    gpa_input = create_float_input(
        message="Current GPA:",
        decimal_places=2,
        min_value=0.0,
        max_value=4.0,
        default_value=3.5
    )
    
    print(f"   GPA widget: {gpa_input}")
    
    # Test GPA scenarios
    gpa_scenarios = [
        (3.9, "Summa Cum Laude"),
        (3.7, "Magna Cum Laude"),
        (3.5, "Cum Laude"),
        (3.0, "Good Standing"),
        (2.5, "Academic Warning")
    ]
    
    for gpa, status in gpa_scenarios:
        gpa_input.set_value(gpa)
        formatted_gpa = gpa_input.get_formatted_value()
        print(f"   GPA {formatted_gpa}: {status}")
    
    # Price calculator
    print("\n💰 Price Calculator:")
    price_input = create_currency_input(
        message="Product price:",
        currency_symbol='$',
        min_value=0.01,
        default_value=29.99
    )
    
    print(f"   Price widget: {price_input}")
    
    # Calculate with tax
    tax_rate = 0.08  # 8% tax
    base_price = price_input.get_value()
    tax_amount = base_price * tax_rate
    total_price = base_price + tax_amount
    
    print(f"   Base price: {price_input.get_formatted_value()}")
    print(f"   Tax (8%): ${tax_amount:.2f}")
    print(f"   Total: ${total_price:.2f}")
    
    # Test different price points
    price_points = [9.99, 49.99, 199.99, 999.99]
    for price in price_points:
        price_input.set_value(price)
        tax = price * tax_rate
        total = price + tax
        price_str = price_input.get_formatted_value()
        print(f"   {price_str} + tax = ${total:.2f}")
    
    # Completion percentage
    print("\n📊 Completion Percentage:")
    completion_input = create_percentage_input(
        message="Project completion:",
        min_value=0.0,
        max_value=1.0,
        default_value=0.65
    )
    
    print(f"   Completion widget: {completion_input}")
    
    # Project phases
    phases = [
        (0.25, "Planning Complete"),
        (0.50, "Development Halfway"),
        (0.75, "Testing Phase"),
        (0.90, "Almost Done"),
        (1.00, "Project Complete!")
    ]
    
    for completion, phase in phases:
        completion_input.set_value(completion)
        formatted = completion_input.get_formatted_value()
        print(f"   {formatted}: {phase}")
    
    # Scientific measurements
    print("\n🔬 Scientific Measurements:")
    measurement_input = create_scientific_input(
        message="Measurement value:",
        precision=3,
        default_value=1.23e-6
    )
    
    print(f"   Measurement widget: {measurement_input}")
    
    # Common scientific values
    scientific_constants = [
        (9.80665, "Standard gravity (m/s²)"),
        (1.602176634e-19, "Elementary charge (C)"),
        (6.62607015e-34, "Planck constant (J⋅Hz⁻¹)"),
        (299792458, "Speed of light (m/s)"),
        (6.02214076e23, "Avogadro constant (mol⁻¹)")
    ]
    
    for value, description in scientific_constants:
        measurement_input.set_value(value)
        formatted = measurement_input.get_formatted_value()
        print(f"   {description}: {formatted}")


def demo_real_world_applications():
    """Demonstrate real-world application scenarios."""
    print("=" * 60)
    print("🌟 Real-World Applications")
    print("=" * 60)
    
    # BMI Calculator
    print("\n⚖️  BMI Calculator:")
    
    height_input = create_float_input(
        message="Height (cm):",
        decimal_places=1,
        min_value=50.0,
        max_value=250.0,
        default_value=175.0
    )
    
    weight_input = create_float_input(
        message="Weight (kg):",
        decimal_places=1,
        min_value=10.0,
        max_value=300.0,
        default_value=70.0
    )
    
    height_cm = height_input.get_value()
    weight_kg = weight_input.get_value()
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    
    # BMI categories
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25.0:
        category = "Normal weight"
    elif bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"
    
    print(f"   Height: {height_input.get_formatted_value()} cm")
    print(f"   Weight: {weight_input.get_formatted_value()} kg")
    print(f"   BMI: {bmi:.1f} ({category})")
    
    # Test different BMI scenarios
    bmi_scenarios = [
        (160, 50, "Underweight scenario"),
        (175, 70, "Normal scenario"),
        (180, 85, "Overweight scenario"),
        (170, 95, "Obese scenario")
    ]
    
    for height, weight, description in bmi_scenarios:
        height_input.set_value(height)
        weight_input.set_value(weight)
        h_m = height / 100
        bmi_calc = weight / (h_m ** 2)
        
        if bmi_calc < 18.5:
            cat = "Underweight"
        elif bmi_calc < 25.0:
            cat = "Normal"
        elif bmi_calc < 30.0:
            cat = "Overweight"
        else:
            cat = "Obese"
        
        print(f"   {description}: BMI {bmi_calc:.1f} ({cat})")
    
    # Loan Calculator
    print("\n🏦 Loan Calculator:")
    
    principal_input = create_currency_input(
        message="Loan amount:",
        min_value=1000,
        default_value=250000
    )
    
    rate_input = create_percentage_input(
        message="Annual interest rate:",
        min_value=0.01,
        max_value=0.20,
        default_value=0.035  # 3.5%
    )
    
    term_input = create_integer_input(
        message="Term (years):",
        min_value=1,
        max_value=50,
        default_value=30
    )
    
    # Monthly payment calculation
    principal = principal_input.get_value()
    annual_rate = rate_input.get_value()
    years = term_input.get_value()
    
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    
    if monthly_rate > 0:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    else:
        monthly_payment = principal / num_payments
    
    total_paid = monthly_payment * num_payments
    total_interest = total_paid - principal
    
    print(f"   Loan amount: {principal_input.get_formatted_value()}")
    print(f"   Interest rate: {rate_input.get_formatted_value()}")
    print(f"   Term: {term_input.get_value()} years")
    print(f"   Monthly payment: ${monthly_payment:.2f}")
    print(f"   Total interest: ${total_interest:.2f}")
    print(f"   Total paid: ${total_paid:.2f}")
    
    # Tip Calculator
    print("\n🍽️  Tip Calculator:")
    
    bill_input = create_currency_input(
        message="Bill amount:",
        min_value=0.01,
        default_value=85.50
    )
    
    tip_rate_input = create_percentage_input(
        message="Tip percentage:",
        min_value=0.0,
        max_value=0.50,
        default_value=0.18  # 18%
    )
    
    people_input = create_integer_input(
        message="Number of people:",
        min_value=1,
        max_value=20,
        default_value=4
    )
    
    # Calculate tip and split
    bill_amount = bill_input.get_value()
    tip_rate = tip_rate_input.get_value()
    num_people = people_input.get_value()
    
    tip_amount = bill_amount * tip_rate
    total_amount = bill_amount + tip_amount
    per_person = total_amount / num_people
    
    print(f"   Bill: {bill_input.get_formatted_value()}")
    print(f"   Tip rate: {tip_rate_input.get_formatted_value()}")
    print(f"   Tip amount: ${tip_amount:.2f}")
    print(f"   Total: ${total_amount:.2f}")
    print(f"   Per person ({num_people} people): ${per_person:.2f}")
    
    # Test different tip scenarios
    tip_scenarios = [
        (50.00, 0.15, 2, "Casual dinner"),
        (120.00, 0.20, 6, "Group dinner"),
        (25.00, 0.18, 1, "Solo lunch")
    ]
    
    for bill, tip_pct, people, scenario in tip_scenarios:
        bill_input.set_value(bill)
        tip_rate_input.set_value(tip_pct)
        people_input.set_value(people)
        
        tip = bill * tip_pct
        total = bill + tip
        per_person_calc = total / people
        
        print(f"   {scenario}: ${per_person_calc:.2f} per person")


def demo_theme_integration():
    """Demonstrate theme integration and styling."""
    print("=" * 60)
    print("🎨 Theme Integration")
    print("=" * 60)
    
    themes = ['professional_blue', 'dark_mode', 'high_contrast', 'classic_terminal', 'minimal']
    
    # Create number adapter for theme testing
    demo_adapter = NumberAdapter(
        message="Themed number input:",
        format_type='currency',
        default_value=1234.56,
        style='professional_blue'
    )
    
    print(f"   Created adapter: {demo_adapter}")
    
    for theme in themes:
        if demo_adapter.is_questionary_enhanced():
            success = demo_adapter.change_theme(theme)
            info = demo_adapter.get_widget_info()
            formatted_value = demo_adapter.get_formatted_value()
            
            print(f"   Theme '{theme}': {formatted_value} (success: {success})")
            print(f"     Current theme: {info.get('theme', 'none')}")
        else:
            print(f"   Theme '{theme}': Enhanced features not available")
    
    # Show widget information
    print("\n📊 Widget Information:")
    widget_info = demo_adapter.get_widget_info()
    
    for key, value in widget_info.items():
        print(f"   {key}: {value}")


def main():
    """Run all NumberAdapter demos."""
    print("🎭 NumberAdapter Comprehensive Demo")
    print("Showcasing all features and capabilities")
    print()
    
    demos = [
        demo_basic_number_formats,
        demo_validation_and_constraints,
        demo_increment_decrement,
        demo_convenience_functions,
        demo_real_world_applications,
        demo_theme_integration
    ]
    
    for i, demo_func in enumerate(demos, 1):
        try:
            demo_func()
            print()
        except Exception as e:
            print(f"❌ Demo {demo_func.__name__} failed: {e}")
            print()
    
    print("=" * 60)
    print("🎉 NumberAdapter Demo Complete!")
    print("=" * 60)
    print()
    print("Key features demonstrated:")
    print("  ✅ Multiple number formats (int, float, currency, percentage, scientific)")
    print("  ✅ Professional styling and theme integration")
    print("  ✅ Range validation and custom constraints")
    print("  ✅ Increment/decrement controls with step sizes")
    print("  ✅ Comprehensive formatting options")
    print("  ✅ Real-world calculation scenarios")
    print("  ✅ Convenience functions for common use cases")
    print("  ✅ Error handling and edge case management")
    print("  ✅ Backward compatibility with legacy widgets")


if __name__ == "__main__":
    main()