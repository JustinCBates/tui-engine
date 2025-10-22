"""Interactive explorer for ALL questionary and questionary-extended components."""

import questionary_extended as qe
import questionary
from questionary_extended import (
    EmailValidator, DateValidator, URLValidator, NumberValidator, 
    RangeValidator, RegexValidator, Choice, Separator, Theme, ColorPalette
)
from datetime import date, datetime
import os


# Component definitions with descriptions and demos
COMPONENT_CATALOG = {
    "📝 Basic Input Components": {
        "text": {
            "name": "Text Input",
            "description": """
Basic text input prompt for collecting string data.

Usage:
  result = questionary.text("Enter your name:", default="John").ask()

Features:
- Default values
- Input validation
- Multiline support
- History navigation
            """.strip(),
            "demo": lambda: demo_text()
        },
        "password": {
            "name": "Password Input", 
            "description": """
Hidden text input for sensitive data like passwords.

Usage:
  password = questionary.password("Enter password:").ask()

Features:
- Hidden input (shows * or nothing)
- No echo to terminal
- Security-focused
- Can validate strength
            """.strip(),
            "demo": lambda: demo_password()
        },
        "enhanced_text": {
            "name": "Enhanced Text Input",
            "description": """
Extended text input with additional features from questionary-extended.

Usage:
  result = qe.enhanced_text("Enter text:", placeholder="Type here").ask()

Features:
- Placeholder text
- Auto-completion
- Input history
- Rich formatting support
            """.strip(),
            "demo": lambda: demo_enhanced_text()
        }
    },
    
    "🔢 Numeric Input Components": {
        "number": {
            "name": "Number Input",
            "description": """
Numeric input with validation and range checking.

Usage:
  age = qe.number("Age:", min_value=0, max_value=150, allow_float=False).ask()

Features:
- Min/max validation
- Float/integer modes
- Step increment support
- Formatting options
            """.strip(),
            "demo": lambda: demo_number()
        },
        "integer": {
            "name": "Integer Input",
            "description": """
Integer-only input (wrapper around number with allow_float=False).

Usage:
  score = qe.integer("Score:", min_value=0, max_value=100).ask()

Features:
- Integer validation only
- Range checking
- Step increments
- No decimal places
            """.strip(),
            "demo": lambda: demo_integer()
        },
        "rating": {
            "name": "Rating Input",
            "description": """
Star rating or scale input with visual feedback.

Usage:
  rating = qe.rating("Rate this:", max_rating=5, icon="⭐").ask()

Features:
- Customizable icons
- Variable scale (1-10)
- Visual star display
- Allow zero ratings option
            """.strip(),
            "demo": lambda: demo_rating()
        }
    },

    "🎯 Selection Components": {
        "select": {
            "name": "Single Select",
            "description": """
Select one option from a list of choices.

Usage:
  color = questionary.select("Choose color:", choices=["Red", "Blue"]).ask()

Features:
- Keyboard navigation
- Search/filter
- Custom choice objects
- Separators for grouping
            """.strip(),
            "demo": lambda: demo_select()
        },
        "checkbox": {
            "name": "Multiple Select (Checkbox)",
            "description": """
Select multiple options from a list with checkboxes.

Usage:
  skills = questionary.checkbox("Skills:", choices=["Python", "JS"]).ask()

Features:
- Multiple selection
- Select all/none
- Pre-checked options
- Visual grouping
            """.strip(),
            "demo": lambda: demo_checkbox()
        },
        "autocomplete": {
            "name": "Autocomplete",
            "description": """
Text input with auto-completion suggestions.

Usage:
  lang = questionary.autocomplete("Language:", choices=languages).ask()

Features:
- Fuzzy matching
- Dynamic suggestions
- Custom completion logic
- Fast typing support
            """.strip(),
            "demo": lambda: demo_autocomplete()
        },
        "rawselect": {
            "name": "Raw Select",
            "description": """
Plain selection interface without fancy formatting.

Usage:
  option = questionary.rawselect("Choose:", choices=["A", "B"]).ask()

Features:
- Simple numbered list
- No fancy UI
- Fast selection
- Keyboard shortcuts
            """.strip(),
            "demo": lambda: demo_rawselect()
        }
    },

    "✅ Confirmation Components": {
        "confirm": {
            "name": "Yes/No Confirmation",
            "description": """
Boolean confirmation prompt for yes/no questions.

Usage:
  confirmed = questionary.confirm("Continue?", default=True).ask()

Features:
- True/False return
- Default values
- Custom yes/no text
- Clear visual feedback
            """.strip(),
            "demo": lambda: demo_confirm()
        }
    },

    "🔐 Validation Components": {
        "email_validator": {
            "name": "Email Validator",
            "description": """
Validates email address format using regex patterns.

Usage:
  email = questionary.text("Email:", validate=EmailValidator()).ask()

Features:
- RFC-compliant validation
- Clear error messages
- Custom error text
- International domains
            """.strip(),
            "demo": lambda: demo_email_validator()
        },
        "url_validator": {
            "name": "URL Validator",
            "description": """
Validates URL format and optionally requires HTTPS.

Usage:
  url = questionary.text("URL:", validate=URLValidator(require_https=True)).ask()

Features:
- Protocol validation
- HTTPS enforcement option
- Domain validation
- Port support
            """.strip(),
            "demo": lambda: demo_url_validator()
        },
        "date_validator": {
            "name": "Date Validator",
            "description": """
Validates date format and ranges.

Usage:
  date = questionary.text("Date:", validate=DateValidator("%Y-%m-%d")).ask()

Features:
- Custom format strings
- Min/max date ranges
- Locale support
- Clear error messages
            """.strip(),
            "demo": lambda: demo_date_validator()
        },
        "number_validator": {
            "name": "Number Validator",
            "description": """
Validates numeric input with range checking.

Usage:
  temp = questionary.text("Temp:", validate=NumberValidator(-50, 50)).ask()

Features:
- Min/max ranges
- Float/integer modes
- Step validation
- Formatting options
            """.strip(),
            "demo": lambda: demo_number_validator()
        },
        "range_validator": {
            "name": "Range Validator",
            "description": """
Validates input falls within a specific range.

Usage:
  pct = questionary.text("Percent:", validate=RangeValidator(0, 100)).ask()

Features:
- Inclusive/exclusive ranges
- Multiple data types
- Custom error messages
- Type coercion
            """.strip(),
            "demo": lambda: demo_range_validator()
        },
        "regex_validator": {
            "name": "Regex Validator",
            "description": """
Validates input against custom regular expression patterns.

Usage:
  phone = questionary.text("Phone:", validate=RegexValidator(r"^\\d{3}-\\d{3}-\\d{4}$")).ask()

Features:
- Custom regex patterns
- Flags support
- Custom error messages
- Pattern examples
            """.strip(),
            "demo": lambda: demo_regex_validator()
        }
    },

    "🎨 Utility & Theming": {
        "format_date": {
            "name": "Date Formatting",
            "description": """
Format date objects into various string representations.

Usage:
  formatted = qe.format_date(date.today(), "%B %d, %Y")

Features:
- Multiple format strings
- Locale support
- Relative dates
- Custom formatting
            """.strip(),
            "demo": lambda: demo_format_date()
        },
        "format_number": {
            "name": "Number Formatting",
            "description": """
Format numbers with various options.

Usage:
  formatted = qe.format_number(1234.56, decimal_places=2, thousands_sep=True)

Features:
- Decimal places control
- Thousands separators
- Currency formatting
- Percentage mode
            """.strip(),
            "demo": lambda: demo_format_number()
        },
        "theming": {
            "name": "Theme System",
            "description": """
Customize the appearance with built-in and custom themes.

Usage:
  theme = qe.create_theme("Custom", palette=ColorPalette(primary="#ff0000"))

Features:
- 6 built-in themes
- Custom color palettes
- Component styling
- Theme inheritance
            """.strip(),
            "demo": lambda: demo_theming()
        },
        "progress_tracker": {
            "name": "Progress Tracker",
            "description": """
Track progress through multi-step operations with visual feedback.

Usage:
  with qe.progress_tracker("Task", total_steps=3) as progress:
      progress.step("Step 1...")

Features:
- Visual progress bars
- Step descriptions
- Error handling
- Completion messages
            """.strip(),
            "demo": lambda: demo_progress_tracker()
        }
    },

    "📋 Advanced Components": {
        "form": {
            "name": "Forms",
            "description": """
Combine multiple prompts into a single form with validation.

Usage:
  data = questionary.form(
      name=questionary.text("Name:"),
      age=qe.number("Age:")
  ).ask()

Features:
- Multiple input types
- Cross-field validation
- Conditional questions
- Data collection
            """.strip(),
            "demo": lambda: demo_form()
        },
        "path": {
            "name": "Path Selection",
            "description": """
File and directory selection with browser interface.

Usage:
  file_path = questionary.path("Select file:").ask()

Features:
- File browser
- Directory navigation
- File filtering
- Validation
            """.strip(),
            "demo": lambda: demo_path()
        },
        "press_key": {
            "name": "Press Any Key",
            "description": """
Pause execution until user presses any key.

Usage:
  questionary.press_any_key_to_continue("Press any key...").ask()

Features:
- Pause execution
- Custom messages
- Any key detection
- Flow control
            """.strip(),
            "demo": lambda: demo_press_key()
        },
        "print": {
            "name": "Styled Print",
            "description": """
Output styled text with colors and formatting.

Usage:
  questionary.print("Success!", style="bold fg:green")

Features:
- Color support
- Text styling
- Multiple styles
- Rich formatting
            """.strip(),
            "demo": lambda: demo_print()
        }
    }
}


def show_component_menu():
    """Show interactive menu of all components."""
    
    # Flatten component catalog for menu
    menu_choices = []
    component_map = {}
    
    for category, components in COMPONENT_CATALOG.items():
        menu_choices.append(questionary.Separator(f"--- {category} ---"))
        for key, info in components.items():
            choice_text = f"{info['name']}"
            menu_choices.append(choice_text)
            component_map[choice_text] = (key, info)
    
    menu_choices.extend([
        questionary.Separator("--- Actions ---"),
        "🚀 Run All Components Demo",
        "❌ Exit"
    ])
    
    while True:
        print("\n" + "="*60)
        print("🎯 QUESTIONARY COMPONENT EXPLORER")
        print("="*60)
        print("Select a component to learn more about it:")
        
        choice = questionary.select(
            "Choose a component:",
            choices=menu_choices,
            instruction="(Use ↑↓ arrows, Enter to select)"
        ).ask()
        
        if not choice:
            break
        elif choice == "❌ Exit":
            print("\n👋 Thanks for exploring questionary components!")
            break
        elif choice == "🚀 Run All Components Demo":
            run_full_demo()
        elif choice in component_map:
            key, info = component_map[choice]
            show_component_details(key, info)


def show_component_details(key: str, info: dict):
    """Show detailed information about a specific component."""
    
    print("\n" + "="*60)
    print(f"📖 {info['name']}")
    print("="*60)
    print(info['description'])
    print("\n" + "-"*60)
    
    action = questionary.select(
        "What would you like to do?",
        choices=[
            "🎮 Run Demo",
            "📝 Copy Usage Example", 
            "🔙 Back to Menu"
        ]
    ).ask()
    
    if action == "🎮 Run Demo":
        print(f"\n🎬 Running demo for {info['name']}...")
        print("-" * 40)
        try:
            info['demo']()
            print("-" * 40)
            print("✅ Demo completed!")
        except Exception as e:
            print(f"❌ Demo error: {e}")
        
        questionary.press_any_key_to_continue("\nPress any key to continue...").ask()
    
    elif action == "📝 Copy Usage Example":
        # Extract usage example from description
        lines = info['description'].split('\n')
        usage_lines = []
        in_usage = False
        
        for line in lines:
            if line.strip().startswith('Usage:'):
                in_usage = True
                continue
            elif in_usage and line.strip().startswith('Features:'):
                break
            elif in_usage:
                usage_lines.append(line)
        
        usage_text = '\n'.join(usage_lines).strip()
        print(f"\n📋 Usage Example for {info['name']}:")
        print("-" * 40)
        print(usage_text)
        print("-" * 40)
        print("💡 Tip: Copy the code above to use in your project!")
        
        questionary.press_any_key_to_continue("\nPress any key to continue...").ask()


# Individual demo functions
def demo_text():
    """Demo basic text input."""
    name = questionary.text("What's your name?", default="Demo User").ask()
    print(f"✅ You entered: {name}")
    
    # 2. Password input (hidden)
    print("\n2. Password Input")
    # password = questionary.password("Enter password:").ask()
    print("   (Skipping password input for demo)")
    
    # 3. Confirm (Yes/No)
    print("\n3. Confirmation")
    confirmed = questionary.confirm("Continue with demo?", default=True).ask()
    print(f"   Result: {confirmed}")
    
    if not confirmed:
        return
    
    # 4. Select (single choice)
    print("\n4. Select (Single Choice)")
    color = questionary.select(
        "Choose your favorite color:",
        choices=["Red", "Green", "Blue", "Yellow", "Purple"]
    ).ask()
    print(f"   Result: {color}")
    
    # 5. Checkbox (multiple choices)
    print("\n5. Checkbox (Multiple Choices)")
    hobbies = questionary.checkbox(
        "Select your hobbies:",
        choices=[
            questionary.Separator("=== Indoor ==="),
            "Reading",
            "Gaming", 
            "Cooking",
            questionary.Separator("=== Outdoor ==="),
            "Hiking",
            "Cycling",
            "Swimming"
        ]
    ).ask()
    print(f"   Result: {hobbies}")
    
    # 6. Autocomplete
    print("\n6. Autocomplete")
    programming_languages = ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "TypeScript"]
    language = questionary.autocomplete(
        "Choose a programming language:",
        choices=programming_languages
    ).ask()
    print(f"   Result: {language}")
    
    # 7. Path selection
    print("\n7. Path Selection")
    # file_path = questionary.path("Select a file:").ask()
    print("   (Skipping path selection for demo - would open file browser)")
    
    # 8. Raw select (no fancy UI)
    print("\n8. Raw Select")
    option = questionary.rawselect(
        "Choose an option (raw select):",
        choices=["Option A", "Option B", "Option C"]
    ).ask()
    print(f"   Result: {option}")
    
    # 9. Press any key to continue
    print("\n9. Press Any Key")
    questionary.press_any_key_to_continue("Press any key to continue...").ask()
    
    # 10. Print (styled output)
    print("\n10. Styled Print")
    questionary.print("This is styled output!", style="bold fg:green")


def demo_questionary_extended():
    """Demonstrate all questionary-extended components."""
    
    print("\n\n🔸 QUESTIONARY-EXTENDED COMPONENTS")
    print("=" * 50)
    
    # Enhanced text input
    print("\n1. Enhanced Text Input")
    enhanced_name = qe.enhanced_text(
        "Enhanced text input:",
        default="Enhanced User"
    ).ask()
    print(f"   Result: {enhanced_name}")
    
    # Numeric inputs
    print("\n2. Numeric Input")
    age = qe.number(
        "Enter your age:",
        min_value=0,
        max_value=120,
        allow_float=False
    ).ask()
    if age:
        print(f"   Result: {age}")
    
    print("\n3. Integer Input")
    score = qe.integer(
        "Enter a score (0-100):",
        min_value=0,
        max_value=100
    ).ask()
    if score:
        print(f"   Result: {score}")
    
    # Rating system
    print("\n4. Rating Input")
    rating = qe.rating(
        "Rate this demo:",
        max_rating=5,
        icon="⭐"
    ).ask()
    if rating:
        print(f"   Result: {rating}/5 stars")
    
    # Progress tracker
    print("\n5. Progress Tracker")
    with qe.progress_tracker("Demo Process", total_steps=3) as progress:
        import time
        progress.step("Step 1 - Initializing...")
        time.sleep(0.5)
        progress.step("Step 2 - Processing...")
        time.sleep(0.5) 
        progress.step("Step 3 - Finalizing...")
        time.sleep(0.5)
        progress.complete("Process completed!")


def demo_validators():
    """Demonstrate all validation components."""
    
    print("\n\n🔹 VALIDATION COMPONENTS")
    print("=" * 50)
    
    # Email validator
    print("\n1. Email Validator")
    email = questionary.text(
        "Enter your email:",
        validate=EmailValidator()
    ).ask()
    if email:
        print(f"   Valid email: {email}")
    
    # URL validator
    print("\n2. URL Validator")
    url = questionary.text(
        "Enter a website URL:",
        validate=URLValidator()
    ).ask()
    if url:
        print(f"   Valid URL: {url}")
    
    # Date validator
    print("\n3. Date Validator")
    birthday = questionary.text(
        "Enter your birthday (YYYY-MM-DD):",
        validate=DateValidator(format_str="%Y-%m-%d", max_date=date.today())
    ).ask()
    if birthday:
        print(f"   Valid date: {birthday}")
    
    # Number validator
    print("\n4. Number Validator")
    temperature = questionary.text(
        "Enter temperature (-50 to 50):",
        validate=NumberValidator(min_value=-50, max_value=50, allow_float=True)
    ).ask()
    if temperature:
        print(f"   Valid temperature: {temperature}")
    
    # Range validator  
    print("\n5. Range Validator")
    percentage = questionary.text(
        "Enter percentage (0-100):",
        validate=RangeValidator(0, 100)
    ).ask()
    if percentage:
        print(f"   Valid percentage: {percentage}")
    
    # Regex validator
    print("\n6. Regex Validator (Phone Number)")
    phone = questionary.text(
        "Enter phone number (XXX-XXX-XXXX):",
        validate=RegexValidator(
            r"^\d{3}-\d{3}-\d{4}$",
            "Please enter phone in format XXX-XXX-XXXX"
        )
    ).ask()
    if phone:
        print(f"   Valid phone: {phone}")


def demo_utility_functions():
    """Demonstrate utility functions."""
    
    print("\n\n🔸 UTILITY FUNCTIONS")
    print("=" * 50)
    
    # Date formatting
    print("\n1. Date Formatting")
    today = date.today()
    formatted_date = qe.format_date(today, "%B %d, %Y")
    print(f"   Today: {formatted_date}")
    
    # Number formatting
    print("\n2. Number Formatting")
    number = 1234567.89
    formatted_number = qe.format_number(number, decimal_places=2, thousands_sep=True)
    print(f"   Formatted: {formatted_number}")
    
    # Color parsing
    print("\n3. Color Parsing")
    try:
        color_info = qe.parse_color("#ff0000")
        print(f"   Color info: RGB{color_info.rgb}, HSL{color_info.hsl}")
    except Exception as e:
        print(f"   Color parsing: {e}")
    
    # Markdown rendering
    print("\n4. Markdown Rendering")
    markdown_text = "**Bold** text with *italic* and `code`"
    rendered = qe.render_markdown(markdown_text)
    print(f"   Rendered: {rendered}")


def demo_theming():
    """Demonstrate theming system."""
    
    print("\n\n🔹 THEMING SYSTEM")
    print("=" * 50)
    
    # Available themes
    print("\n1. Available Themes")
    for theme_name in qe.THEMES:
        print(f"   • {theme_name}")
    
    # Custom theme creation
    print("\n2. Custom Theme")
    custom_palette = ColorPalette(
        primary="#00ff00",
        secondary="#ff00ff",
        success="#00ff00",
        error="#ff0000"
    )
    
    custom_theme = qe.create_theme(
        name="Custom Demo Theme",
        palette=custom_palette
    )
    
    print(f"   Created theme: {custom_theme.name}")
    print(f"   Primary color: {custom_theme.palette.primary}")


def demo_advanced_forms():
    """Demonstrate advanced form capabilities."""
    
    print("\n\n🔸 ADVANCED FORMS")
    print("=" * 50)
    
    # Complex form with all components
    print("\n1. Comprehensive Form")
    
    form_result = questionary.form(
        # Basic inputs
        name=questionary.text("Full Name:", validate=lambda x: len(x) > 0),
        email=questionary.text("Email:", validate=EmailValidator()),
        
        # Enhanced inputs
        age=qe.number("Age:", min_value=13, max_value=120, allow_float=False),
        
        # Selections
        country=questionary.select("Country:", choices=["USA", "Canada", "UK", "Australia", "Other"]),
        interests=questionary.checkbox("Interests:", choices=["Technology", "Sports", "Music", "Travel", "Reading"]),
        
        # Confirmations
        subscribe=questionary.confirm("Subscribe to newsletter?", default=False),
        terms=questionary.confirm("Accept terms and conditions?", default=False)
    ).ask()
    
    if form_result:
        print("\n   📋 Form Results:")
        for key, value in form_result.items():
            if isinstance(value, list):
                print(f"     {key}: {', '.join(value)}")
            else:
                print(f"     {key}: {value}")


def main():
    """Run complete demonstration of all components."""
    
    print("🚀 COMPLETE QUESTIONARY & QUESTIONARY-EXTENDED DEMO")
    print("=" * 60)
    print("This demo covers ALL available components and features.")
    print()
    
    try:
        # Run all demonstrations
        demo_basic_questionary()
        demo_questionary_extended() 
        demo_validators()
        demo_utility_functions()
        demo_theming()
        demo_advanced_forms()
        
        print("\n\n✅ COMPLETE DEMO FINISHED!")
        print("=" * 60)
        print("All questionary and questionary-extended components demonstrated.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")


if __name__ == "__main__":
    main()