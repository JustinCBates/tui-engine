"""Example: Basic usage of questionary-extended."""

from datetime import date

import questionary_extended as qe


def main():
    """Demonstrate basic questionary-extended features."""

    print("🚀 Questionary Extended Examples")
    print("=" * 40)

    # Enhanced text input
    print("\n1. Enhanced Text Input")
    name = qe.enhanced_text(
        "What's your name?", placeholder="Enter your full name"
    ).ask()

    if name:
        print(f"Hello, {name}!")

    # Numeric input with validation
    print("\n2. Numeric Input")
    age = qe.number(
        "What's your age?", min_value=0, max_value=150, allow_float=False
    ).ask()

    if age:
        print(f"You are {age} years old.")

    # Date input
    print("\n3. Date Input")
    birthday = qe.date(
        "When is your birthday?", max_date=date.today(), format_str="%Y-%m-%d"
    ).ask()

    if birthday:
        print(f"Your birthday is {birthday}.")

    # Tree selection
    print("\n4. Tree Selection")
    language = qe.tree_select(
        "Choose a programming language:",
        choices={
            "Web Development": {
                "Frontend": ["JavaScript", "TypeScript", "Vue.js", "React"],
                "Backend": ["Node.js", "Python", "PHP", "Ruby"],
            },
            "Data Science": ["Python", "R", "Julia", "Scala"],
            "Mobile": ["Swift", "Kotlin", "Flutter", "React Native"],
        },
    ).ask()

    if language:
        print(f"Great choice: {language}!")

    # Rating input
    print("\n5. Rating Input")
    rating = qe.rating("How would you rate this demo?", max_rating=5, icon="⭐").ask()

    if rating:
        print(f"Thanks for the {rating} star rating!")

    # Grouped selection
    print("\n6. Grouped Selection")
    tool = qe.grouped_select(
        "Choose a development tool:",
        groups={
            "Editors": ["VS Code", "Vim", "Emacs", "Sublime Text"],
            "IDEs": ["PyCharm", "IntelliJ", "Eclipse", "Visual Studio"],
            "Terminals": ["Terminal", "iTerm2", "Hyper", "Windows Terminal"],
        },
    ).ask()

    if tool:
        print(f"Good choice: {tool}")

    print("\n✅ Demo completed!")


if __name__ == "__main__":
    main()
