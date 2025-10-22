"""Example: Working basic usage of questionary-extended."""


import questionary_extended as qe


def main():
    """Demonstrate working questionary-extended features."""

    print("🚀 Questionary Extended - Working Examples")
    print("=" * 45)

    # Enhanced text input
    print("\n1. Enhanced Text Input")
    name = qe.enhanced_text("What's your name?", default="John Doe").ask()

    if name:
        print(f"Hello, {name}!")

    # Numeric input with validation
    print("\n2. Numeric Input")
    age = qe.number(
        "What's your age?", min_value=0, max_value=150, allow_float=False
    ).ask()

    if age:
        try:
            age_int = int(age)
            print(f"You are {age_int} years old.")
        except ValueError:
            print("Invalid age entered.")

    # Integer input
    print("\n3. Integer Input")
    score = qe.integer("Enter a score (0-100):", min_value=0, max_value=100).ask()

    if score:
        try:
            score_int = int(score)
            print(f"Your score: {score_int}/100")
        except ValueError:
            print("Invalid score entered.")

    # Rating input
    print("\n4. Rating Input")
    rating = qe.rating("How would you rate this demo?", max_rating=5, icon="⭐").ask()

    if rating:
        print(f"Thanks for the {rating} star rating!")

    # Progress tracker
    print("\n5. Progress Tracker")
    with qe.ProgressTracker("Demo Process", total_steps=3) as progress:
        progress.step("Loading data...")
        import time

        time.sleep(1)

        progress.step("Processing...")
        time.sleep(1)

        progress.step("Finalizing...")
        time.sleep(1)

        progress.complete("Demo completed!")

    # Simple form using questionary directly
    print("\n6. Simple Form")
    import questionary

    form_data = questionary.form(
        full_name=questionary.text("Full Name:"),
        email=questionary.text("Email:"),
        experience=questionary.select(
            "Experience Level:",
            choices=["Beginner", "Intermediate", "Advanced", "Expert"],
        ),
    ).ask()

    if form_data:
        print("\n📋 Form Results:")
        for key, value in form_data.items():
            print(f"  {key}: {value}")

    print("\n✅ All examples completed successfully!")


if __name__ == "__main__":
    main()
