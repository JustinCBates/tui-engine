"""Interactive explorer for ALL questionary and questionary-extended components."""

import time
from datetime import date

import questionary

import questionary_extended as qe
from questionary_extended import (
    ColorPalette,
    DateValidator,
    EmailValidator,
    NumberValidator,
    RangeValidator,
    RegexValidator,
    URLValidator,
)

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
            "demo": lambda: demo_text(),
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
            "demo": lambda: demo_password(),
        },
        "enhanced_text": {
            "name": "Enhanced Text Input",
            "description": """
Extended text input with additional features from questionary-extended.

Usage:
  result = qe.enhanced_text("Enter text:", default="Hello").ask()

Features:
- Enhanced validation
- Better user experience
- Consistent with other qe components
- Future extensibility
            """.strip(),
            "demo": lambda: demo_enhanced_text(),
        },
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
- Clear error messages
- Type conversion
            """.strip(),
            "demo": lambda: demo_number(),
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
- No decimal places allowed
- Clear validation messages
            """.strip(),
            "demo": lambda: demo_integer(),
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
            "demo": lambda: demo_rating(),
        },
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
            "demo": lambda: demo_select(),
        },
        "checkbox": {
            "name": "Multiple Select (Checkbox)",
            "description": """
Select multiple options from a list with checkboxes.

Usage:
  skills = questionary.checkbox("Skills:", choices=["Python", "JS"]).ask()

Features:
- Multiple selection
- Select all/none shortcuts
- Pre-checked options
- Visual grouping with separators
            """.strip(),
            "demo": lambda: demo_checkbox(),
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
- Fast typing support
- Custom completion logic
            """.strip(),
            "demo": lambda: demo_autocomplete(),
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
            "demo": lambda: demo_rawselect(),
        },
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
            "demo": lambda: demo_confirm(),
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
            "demo": lambda: demo_email_validator(),
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
            "demo": lambda: demo_url_validator(),
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
- Clear error messages
- Format examples
            """.strip(),
            "demo": lambda: demo_date_validator(),
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
- Clear validation messages
- Type conversion
            """.strip(),
            "demo": lambda: demo_number_validator(),
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
            "demo": lambda: demo_range_validator(),
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
            "demo": lambda: demo_regex_validator(),
        },
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
- Standard date formats
- Custom formatting
            """.strip(),
            "demo": lambda: demo_format_date(),
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
            "demo": lambda: demo_format_number(),
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
            "demo": lambda: demo_theming(),
        },
        "progress_tracker": {
            "name": "Progress Tracker",
            "description": """
Track progress through multi-step operations with visual feedback.

Usage:
    with qe.ProgressTracker("Task", total_steps=3) as progress:
            progress.step("Step 1...")

Features:
- Visual progress bars
- Step descriptions
- Error handling
- Completion messages
            """.strip(),
            "demo": lambda: demo_progress_tracker(),
        },
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
- Sequential questions
- Data collection
- Result dictionary
            """.strip(),
            "demo": lambda: demo_form(),
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
- Path validation
            """.strip(),
            "demo": lambda: demo_path(),
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
            "demo": lambda: demo_press_key(),
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
            "demo": lambda: demo_print(),
        },
    },
}

# Backwards-compatible alias expected by tests
COMPONENTS = COMPONENT_CATALOG


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

    menu_choices.extend(
        [
            questionary.Separator("--- Actions ---"),
            "🚀 Run All Components Demo",
            "❌ Exit",
        ]
    )

    while True:
        print("\n" + "=" * 60)
        print("🎯 QUESTIONARY COMPONENT EXPLORER")
        print("=" * 60)
        print("Select a component to learn more about it:")

        choice = questionary.select(
            "Choose a component:",
            choices=menu_choices,
            instruction="(Use ↑↓ arrows, Enter to select)",
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

    print("\n" + "=" * 60)
    print(f"📖 {info['name']}")
    print("=" * 60)
    print(info["description"])

    # Show code sample
    print("\n" + "💻 CODE SAMPLE:")
    print("-" * 40)
    code_sample = get_code_sample(key)
    print(code_sample)

    print("\n" + "-" * 60)

    action = questionary.select(
        "What would you like to do?",
        choices=[
            "🎮 Run Basic Demo",
            "🔧 Explore Features Demo",
            "📝 Copy Code Sample",
            "🔙 Back to Menu",
        ],
    ).ask()

    if action == "🎮 Run Basic Demo":
        print(f"\n🎬 Running basic demo for {info['name']}...")
        print("-" * 40)
        try:
            info["demo"]()
            print("-" * 40)
            print("✅ Basic demo completed!")
        except Exception as e:
            print(f"❌ Demo error: {e}")

        questionary.press_any_key_to_continue("\nPress any key to continue...").ask()

    elif action == "🔧 Explore Features Demo":
        print(f"\n🔍 Exploring all features of {info['name']}...")
        print("-" * 50)
        try:
            run_feature_demo(key, info)
            print("-" * 50)
            print("✅ Feature exploration completed!")
        except Exception as e:
            print(f"❌ Feature demo error: {e}")

        questionary.press_any_key_to_continue("\nPress any key to continue...").ask()

    elif action == "📝 Copy Code Sample":
        print(f"\n📋 Code Sample for {info['name']}:")
        print("-" * 40)
        print(code_sample)
        print("-" * 40)
        print("💡 Tip: Copy the code above to use in your project!")

        questionary.press_any_key_to_continue("\nPress any key to continue...").ask()


def get_code_sample(component_key: str) -> str:
    """Get comprehensive code sample for a component."""

    samples = {
        "text": """import questionary

# Basic usage
name = questionary.text("Enter your name:").ask()

# With default value
name = questionary.text("Enter your name:", default="John").ask()

# With validation
name = questionary.text(
    "Enter your name:",
    validate=lambda x: len(x) > 0 or "Name cannot be empty"
).ask()

# Multiline text
bio = questionary.text("Bio:", multiline=True).ask()""",
        "password": """import questionary

# Basic password input
password = questionary.password("Enter password:").ask()

# With validation
password = questionary.password(
    "Enter password:",
    validate=lambda x: len(x) >= 8 or "Password must be 8+ characters"
).ask()""",
        "enhanced_text": """import questionary_extended as qe

# Basic enhanced text
text = qe.enhanced_text("Enter text:").ask()

# With default and validation
text = qe.enhanced_text(
    "Enter name:",
    default="Default User",
    validator=lambda x: len(x) > 0
).ask()""",
        "number": """import questionary_extended as qe

# Basic number input
age = qe.number("Enter age:").ask()

# With range validation
age = qe.number(
    "Enter age:",
    min_value=0,
    max_value=150,
    allow_float=False
).ask()

# Float with step
temperature = qe.number(
    "Temperature:",
    min_value=-50.0,
    max_value=50.0,
    step=0.5,
    allow_float=True
).ask()""",
        "integer": """import questionary_extended as qe

# Integer input with range
score = qe.integer(
    "Enter score:",
    min_value=0,
    max_value=100
).ask()""",
        "rating": """import questionary_extended as qe

# Basic 5-star rating
rating = qe.rating("Rate this:").ask()

# Custom scale and icon
rating = qe.rating(
    "Rate experience:",
    max_rating=10,
    icon="⭐",
    allow_zero=True
).ask()""",
        "select": """import questionary

# Basic selection
color = questionary.select(
    "Choose color:",
    choices=["Red", "Blue", "Green"]
).ask()

# With Choice objects and separators
choice = questionary.select(
    "Select option:",
    choices=[
        questionary.Separator("=== Colors ==="),
        questionary.Choice("Red", "red_value"),
        questionary.Choice("Blue", "blue_value"),
        questionary.Separator("=== Actions ==="),
        questionary.Choice("Exit", "exit")
    ]
).ask()""",
        "checkbox": """import questionary

# Multiple selection
skills = questionary.checkbox(
    "Select skills:",
    choices=["Python", "JavaScript", "Go", "Rust"]
).ask()

# With separators and pre-selected
skills = questionary.checkbox(
    "Select skills:",
    choices=[
        questionary.Separator("=== Backend ==="),
        questionary.Choice("Python", checked=True),
        "Go",
        questionary.Separator("=== Frontend ==="),
        "JavaScript",
        "TypeScript"
    ]
).ask()""",
        "autocomplete": """import questionary

languages = ["Python", "JavaScript", "Java", "C++", "Go"]

# Basic autocomplete
choice = questionary.autocomplete(
    "Language:",
    choices=languages
).ask()

# With custom completion
choice = questionary.autocomplete(
    "Language:",
    choices=languages,
    meta_information={
        "Python": "Easy to learn",
        "JavaScript": "Web development"
    }
).ask()""",
        "rawselect": """import questionary

# Simple numbered list
option = questionary.rawselect(
    "Choose:",
    choices=["Option A", "Option B", "Option C"]
).ask()""",
        "confirm": """import questionary

# Basic yes/no
confirmed = questionary.confirm("Continue?").ask()

# With default value
confirmed = questionary.confirm(
    "Delete file?",
    default=False
).ask()

# Custom yes/no text
confirmed = questionary.confirm(
    "Proceed?",
    default=True,
    instruction="(y/n)"
).ask()""",
        "email_validator": """import questionary
from questionary_extended import EmailValidator

# Email validation
email = questionary.text(
    "Email:",
    validate=EmailValidator()
).ask()

# Custom error message
email = questionary.text(
    "Email:",
    validate=EmailValidator()
).ask()""",
        "url_validator": """import questionary
from questionary_extended import URLValidator

# Basic URL validation
url = questionary.text(
    "Website URL:",
    validate=URLValidator()
).ask()

# Require HTTPS
url = questionary.text(
    "Secure URL:",
    validate=URLValidator(require_https=True)
).ask()""",
        "date_validator": """import questionary
from questionary_extended import DateValidator
from datetime import date

# Date validation
birthday = questionary.text(
    "Birthday (YYYY-MM-DD):",
    validate=DateValidator()
).ask()

# Custom format and range
birthday = questionary.text(
    "Birthday (MM/DD/YYYY):",
    validate=DateValidator(
        format_str="%m/%d/%Y",
        min_date=date(1900, 1, 1),
        max_date=date.today()
    )
).ask()""",
        "number_validator": """import questionary
from questionary_extended import NumberValidator

# Number validation
temp = questionary.text(
    "Temperature:",
    validate=NumberValidator(
        min_value=-50,
        max_value=50,
        allow_float=True
    )
).ask()""",
        "range_validator": """import questionary
from questionary_extended import RangeValidator

# Range validation
percentage = questionary.text(
    "Percentage:",
    validate=RangeValidator(0, 100, inclusive=True)
).ask()""",
        "regex_validator": """import questionary
from questionary_extended import RegexValidator

# Phone number validation
phone = questionary.text(
    "Phone (XXX-XXX-XXXX):",
    validate=RegexValidator(
        pattern=r"^\\d{3}-\\d{3}-\\d{4}$",
        message="Use format: XXX-XXX-XXXX"
    )
).ask()""",
        "format_date": """import questionary_extended as qe
from datetime import date

today = date.today()

# Different date formats
iso_date = qe.format_date(today, "%Y-%m-%d")
us_date = qe.format_date(today, "%m/%d/%Y")
full_date = qe.format_date(today, "%A, %B %d, %Y")""",
        "format_number": """import questionary_extended as qe

number = 1234567.89

# Various number formats
basic = qe.format_number(number)
separated = qe.format_number(number, thousands_sep=True)
currency = qe.format_number(number, currency="$", decimal_places=2)
percentage = qe.format_number(0.156, percentage=True, decimal_places=1)""",
        "theming": """import questionary_extended as qe

# Use built-in theme
theme = qe.THEMES["dark"]

# Create custom theme
custom_palette = qe.ColorPalette(
    primary="#00ff00",
    secondary="#ff00ff",
    success="#00ff00",
    error="#ff0000"
)

custom_theme = qe.create_theme(
    name="My Theme",
    palette=custom_palette
)""",
        "progress_tracker": """import questionary_extended as qe

# Basic progress tracking
with qe.ProgressTracker("Task", total_steps=3) as progress:
    progress.step("Step 1...")
    # do work
    progress.step("Step 2...")
    # do work
    progress.complete("Done!")""",
        "form": """import questionary
import questionary_extended as qe

# Complex form
data = questionary.form(
    name=questionary.text("Name:", validate=lambda x: len(x) > 0),
    email=questionary.text("Email:", validate=qe.EmailValidator()),
    age=qe.number("Age:", min_value=0, max_value=150),
    skills=questionary.checkbox("Skills:", choices=["Python", "JS"]),
    subscribe=questionary.confirm("Subscribe?", default=False)
).ask()""",
        "path": """import questionary

# File selection
file_path = questionary.path("Select file:").ask()

# Directory selection
dir_path = questionary.path("Select directory:", only_directories=True).ask()""",
        "press_key": """import questionary

# Pause execution
questionary.press_any_key_to_continue().ask()

# Custom message
questionary.press_any_key_to_continue("Press Enter to continue...").ask()""",
        "print": """import questionary

# Styled output
questionary.print("Success!", style="bold fg:green")
questionary.print("Warning!", style="bold fg:yellow")
questionary.print("Error!", style="bold fg:red")
questionary.print("Info", style="fg:blue italic")""",
    }

    return samples.get(component_key, "# Code sample not available")


def run_feature_demo(component_key: str, info: dict):
    """Run comprehensive feature demonstration for a component."""

    feature_demos = {
        "text": demo_text_features,
        "password": demo_password_features,
        "enhanced_text": demo_enhanced_text_features,
        "number": demo_number_features,
        "integer": demo_integer_features,
        "rating": demo_rating_features,
        "select": demo_select_features,
        "checkbox": demo_checkbox_features,
        "autocomplete": demo_autocomplete_features,
        "rawselect": demo_rawselect_features,
        "confirm": demo_confirm_features,
        "email_validator": demo_email_validator_features,
        "url_validator": demo_url_validator_features,
        "date_validator": demo_date_validator_features,
        "number_validator": demo_number_validator_features,
        "range_validator": demo_range_validator_features,
        "regex_validator": demo_regex_validator_features,
        "format_date": demo_format_date_features,
        "format_number": demo_format_number_features,
        "theming": demo_theming_features,
        "progress_tracker": demo_progress_tracker_features,
        "form": demo_form_features,
        "path": demo_path_features,
        "press_key": demo_press_key_features,
        "print": demo_print_features,
    }

    demo_function = feature_demos.get(component_key)
    if demo_function:
        demo_function()
    else:
        print(f"⚠️  No detailed feature demo available for {info['name']}")


# Feature demonstration functions
def demo_text_features():
    """Demonstrate all text input features."""

    print("🔹 Feature 1: Basic Text Input")
    name = questionary.text("Enter your name:").ask()
    print(f"   Result: {name}")

    print("\n🔹 Feature 2: Default Value")
    name = questionary.text("Enter name:", default="Default User").ask()
    print(f"   Result: {name}")

    print("\n🔹 Feature 3: Input Validation")
    name = questionary.text(
        "Enter non-empty name:", validate=lambda x: len(x) > 0 or "Name cannot be empty"
    ).ask()
    print(f"   Result: {name}")

    print("\n🔹 Feature 4: Multiline Input")
    bio = questionary.text("Enter bio (multiline):", multiline=True).ask()
    print(f"   Result: {bio}")


def demo_password_features():
    """Demonstrate password input features."""
    print("🔹 Password Input Features:")
    print("   • Hidden input (no echo)")
    print("   • Security-focused")
    print("   • Validation support")
    print("   (Skipping actual password demo for security)")


def demo_enhanced_text_features():
    """Demonstrate enhanced text features."""

    print("🔹 Feature 1: Basic Enhanced Text")
    text = qe.enhanced_text("Enter text:").ask()
    print(f"   Result: {text}")

    print("\n🔹 Feature 2: With Default Value")
    text = qe.enhanced_text("Enter text:", default="Enhanced Default").ask()
    print(f"   Result: {text}")


def demo_number_features():
    """Demonstrate number input features."""

    print("🔹 Feature 1: Basic Number Input")
    num = qe.number("Enter any number:").ask()
    print(f"   Result: {num}")

    print("\n🔹 Feature 2: Integer Only")
    age = qe.number("Enter age (integer):", allow_float=False).ask()
    print(f"   Result: {age}")

    print("\n🔹 Feature 3: Range Validation")
    score = qe.number("Score (0-100):", min_value=0, max_value=100).ask()
    print(f"   Result: {score}")


def demo_integer_features():
    """Demonstrate integer input features."""

    print("🔹 Feature 1: Integer with Range")
    score = qe.integer("Enter score (0-100):", min_value=0, max_value=100).ask()
    print(f"   Result: {score}")


def demo_rating_features():
    """Demonstrate rating input features."""

    print("🔹 Feature 1: 5-Star Rating")
    rating1 = qe.rating("Rate (5 stars):").ask()
    print(f"   Result: {rating1}/5")

    print("\n🔹 Feature 2: Custom Scale (10-point)")
    rating2 = qe.rating("Rate (10-point):", max_rating=10).ask()
    print(f"   Result: {rating2}/10")

    print("\n🔹 Feature 3: Custom Icon")
    rating3 = qe.rating("Rate with hearts:", icon="❤️", max_rating=3).ask()
    print(f"   Result: {rating3}/3 hearts")


def demo_select_features():
    """Demonstrate select features."""

    print("🔹 Feature 1: Basic Selection")
    color = questionary.select("Choose color:", choices=["Red", "Blue", "Green"]).ask()
    print(f"   Result: {color}")

    print("\n🔹 Feature 2: With Separators")
    choice = questionary.select(
        "Choose option:",
        choices=[
            questionary.Separator("=== Colors ==="),
            "Red",
            "Blue",
            "Green",
            questionary.Separator("=== Actions ==="),
            "Save",
            "Cancel",
        ],
    ).ask()
    print(f"   Result: {choice}")


def demo_checkbox_features():
    """Demonstrate checkbox features."""

    print("🔹 Feature 1: Basic Multiple Selection")
    skills = questionary.checkbox(
        "Select skills:", choices=["Python", "JavaScript", "Go", "Rust"]
    ).ask()
    print(f"   Result: {skills}")

    print("\n🔹 Feature 2: With Pre-selected Items")
    hobbies = questionary.checkbox(
        "Select hobbies:",
        choices=[
            questionary.Choice("Reading", checked=True),
            questionary.Choice("Gaming", checked=False),
            questionary.Choice("Coding", checked=True),
        ],
    ).ask()
    print(f"   Result: {hobbies}")


def demo_autocomplete_features():
    """Demonstrate autocomplete features."""

    languages = ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "TypeScript"]

    print("🔹 Feature 1: Basic Autocomplete")
    lang = questionary.autocomplete(
        "Language (type to filter):", choices=languages
    ).ask()
    print(f"   Result: {lang}")


def demo_rawselect_features():
    """Demonstrate raw select features."""

    print("🔹 Feature 1: Raw Selection Interface")
    option = questionary.rawselect(
        "Choose option (raw interface):", choices=["Option A", "Option B", "Option C"]
    ).ask()
    print(f"   Result: {option}")


def demo_confirm_features():
    """Demonstrate confirm features."""

    print("🔹 Feature 1: Basic Confirmation")
    result1 = questionary.confirm("Do you agree?").ask()
    print(f"   Result: {result1}")

    print("\n🔹 Feature 2: With Default Value")
    result2 = questionary.confirm("Delete file?", default=False).ask()
    print(f"   Result: {result2}")


def demo_email_validator_features():
    """Demonstrate email validator features."""

    print("🔹 Feature 1: Email Format Validation")
    email = questionary.text("Enter email:", validate=EmailValidator()).ask()
    print(f"   Valid email: {email}")


def demo_url_validator_features():
    """Demonstrate URL validator features."""

    print("🔹 Feature 1: Basic URL Validation")
    url1 = questionary.text("Enter URL:", validate=URLValidator()).ask()
    print(f"   Valid URL: {url1}")

    print("\n🔹 Feature 2: HTTPS Required")
    url2 = questionary.text(
        "Enter HTTPS URL:", validate=URLValidator(require_https=True)
    ).ask()
    print(f"   Valid HTTPS URL: {url2}")


def demo_date_validator_features():
    """Demonstrate date validator features."""

    print("🔹 Feature 1: ISO Date Format")
    date1 = questionary.text(
        "Date (YYYY-MM-DD):", validate=DateValidator(format_str="%Y-%m-%d")
    ).ask()
    print(f"   Valid date: {date1}")

    print("\n🔹 Feature 2: US Date Format with Range")
    date2 = questionary.text(
        "Birth date (MM/DD/YYYY):",
        validate=DateValidator(format_str="%m/%d/%Y", max_date=date.today()),
    ).ask()
    print(f"   Valid birth date: {date2}")


def demo_number_validator_features():
    """Demonstrate number validator features."""

    print("🔹 Feature 1: Float Range Validation")
    temp = questionary.text(
        "Temperature (-50 to 50°C):",
        validate=NumberValidator(min_value=-50, max_value=50, allow_float=True),
    ).ask()
    print(f"   Valid temperature: {temp}°C")

    print("\n🔹 Feature 2: Integer Only")
    count = questionary.text(
        "Count (0-1000):",
        validate=NumberValidator(min_value=0, max_value=1000, allow_float=False),
    ).ask()
    print(f"   Valid count: {count}")


def demo_range_validator_features():
    """Demonstrate range validator features."""

    print("🔹 Feature 1: Inclusive Range")
    pct1 = questionary.text(
        "Percentage (0-100):", validate=RangeValidator(0, 100, inclusive=True)
    ).ask()
    print(f"   Valid percentage: {pct1}%")


def demo_regex_validator_features():
    """Demonstrate regex validator features."""

    print("🔹 Feature 1: Phone Number Pattern")
    phone = questionary.text(
        "Phone (XXX-XXX-XXXX):",
        validate=RegexValidator(
            r"^\d{3}-\d{3}-\d{4}$", "Please use format: XXX-XXX-XXXX"
        ),
    ).ask()
    print(f"   Valid phone: {phone}")

    print("\n🔹 Feature 2: Custom Pattern (Letters only)")
    letters = questionary.text(
        "Letters only:", validate=RegexValidator(r"^[a-zA-Z]+$", "Only letters allowed")
    ).ask()
    print(f"   Valid input: {letters}")


def demo_format_date_features():
    """Demonstrate date formatting features."""

    today = date.today()

    print("🔹 Date Formatting Options:")
    formats = [
        ("%Y-%m-%d", "ISO format"),
        ("%m/%d/%Y", "US format"),
        ("%d/%m/%Y", "European format"),
        ("%A, %B %d, %Y", "Full format"),
        ("%b %d", "Short format"),
        ("%Y-%j", "Day of year"),
    ]

    for fmt, desc in formats:
        result = qe.format_date(today, fmt)
        print(f"   {desc}: {result}")


def demo_format_number_features():
    """Demonstrate number formatting features."""

    number = 1234567.89

    print("🔹 Number Formatting Options:")

    print(f"   Original: {number}")
    print(f"   Thousands separator: {qe.format_number(number, thousands_sep=True)}")
    print(f"   2 decimal places: {qe.format_number(number, decimal_places=2)}")
    print(f"   Currency: {qe.format_number(number, currency='$', decimal_places=2)}")
    print(
        f"   Percentage: {qe.format_number(0.1567, percentage=True, decimal_places=1)}"
    )
    print(f"   No decimals: {qe.format_number(number, decimal_places=0)}")


def demo_theming_features():
    """Demonstrate theming features."""

    print("🔹 Theming System Features:")

    print("\n   Built-in Themes:")
    for theme_name in qe.THEMES:
        theme = qe.THEMES[theme_name]
        print(f"     • {theme_name}: {theme.palette.primary}")

    print("\n   Custom Theme Creation:")
    custom_palette = ColorPalette(
        primary="#00ff00", secondary="#ff00ff", success="#4caf50", error="#f44336"
    )

    custom_theme = qe.create_theme("Demo Theme", palette=custom_palette)
    print(f"     Created: {custom_theme.name}")
    print(f"     Primary: {custom_theme.palette.primary}")
    print(f"     Success: {custom_theme.palette.success}")


def demo_progress_tracker_features():
    """Demonstrate progress tracker features."""

    print("🔹 Feature 1: Basic Progress Tracking")
    with qe.ProgressTracker("Basic Task", total_steps=3) as progress:
        progress.step("Initializing...")
        time.sleep(0.5)
        progress.step("Processing...")
        time.sleep(0.5)
        progress.step("Finalizing...")
        time.sleep(0.5)
        progress.complete("Done!")

    print("\n🔹 Feature 2: Error Handling")
    try:
        with qe.ProgressTracker("Task with Error", total_steps=2) as progress:
            progress.step("Step 1 successful...")
            time.sleep(0.5)
            progress.step("Step 2 will fail...")
            # Simulate error handling
            progress.complete("Handled gracefully!")
    except Exception:
        pass


def demo_form_features():
    """Demonstrate form features."""

    print("🔹 Feature 1: Mixed Input Types Form")
    form_data = questionary.form(
        name=questionary.text("Name:", validate=lambda x: len(x) > 0),
        age=qe.number("Age:", min_value=0, max_value=150, allow_float=False),
        subscribe=questionary.confirm("Subscribe?", default=False),
    ).ask()

    if form_data:
        print("   Form Results:")
        for key, value in form_data.items():
            print(f"     {key}: {value}")


def demo_path_features():
    """Demonstrate path features."""

    print("🔹 Path Selection Features:")
    print("   • File browser interface")
    print("   • Directory navigation")
    print("   • File filtering")
    print("   • Path validation")
    print("   (Requires file system - skipped in demo)")


def demo_press_key_features():
    """Demonstrate press key features."""

    print("🔹 Feature 1: Basic Press Any Key")
    questionary.press_any_key_to_continue("Press any key...").ask()
    print("   Key pressed!")

    print("\n🔹 Feature 2: Custom Message")
    questionary.press_any_key_to_continue("Press Enter to continue the demo...").ask()
    print("   Enter pressed!")


def demo_print_features():
    """Demonstrate print styling features."""

    print("🔹 Print Styling Features:")

    print("\n   Different Styles:")
    questionary.print("Success message!", style="bold fg:green")
    questionary.print("Warning message!", style="bold fg:yellow")
    questionary.print("Error message!", style="bold fg:red")
    questionary.print("Info message", style="fg:blue italic")
    questionary.print("Highlighted text", style="bg:yellow fg:black")
    questionary.print("Underlined text", style="underline")

    print("\n   Combining Styles:")
    questionary.print("Bold + Italic + Color", style="bold italic fg:magenta")
    questionary.print("Background + Foreground", style="bg:blue fg:white")

    print("\n   Available Colors:")
    colors = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    for color in colors:
        questionary.print(f"{color.capitalize()}", style=f"fg:{color}")

    print("\n   Text Decorations:")
    questionary.print("Bold text", style="bold")
    questionary.print("Italic text", style="italic")
    questionary.print("Underlined text", style="underline")
    questionary.print("Dim text", style="dim")


# Individual demo functions
def demo_text():
    """Demo basic text input."""
    name = questionary.text("What's your name?", default="Demo User").ask()
    print(f"✅ You entered: {name}")


def demo_password():
    """Demo password input."""
    print("💡 Password input would hide your typing")
    print("   (Skipping actual password prompt for security)")


def demo_enhanced_text():
    """Demo enhanced text input."""
    text = qe.enhanced_text("Enter some text:", default="Enhanced Demo").ask()
    print(f"✅ Enhanced text result: {text}")


def demo_number():
    """Demo number input."""
    age = qe.number(
        "Enter your age:", min_value=0, max_value=150, allow_float=False
    ).ask()
    if age:
        print(f"✅ Age entered: {age}")


def demo_integer():
    """Demo integer input."""
    score = qe.integer("Enter a score (0-100):", min_value=0, max_value=100).ask()
    if score:
        print(f"✅ Score entered: {score}")


def demo_rating():
    """Demo rating input."""
    rating = qe.rating("Rate this demo:", max_rating=5, icon="⭐").ask()
    if rating:
        print(f"✅ Rating: {rating}/5 stars")


def demo_select():
    """Demo single select."""
    color = questionary.select(
        "Choose your favorite color:",
        choices=["🔴 Red", "🔵 Blue", "🟢 Green", "🟡 Yellow", "🟣 Purple"],
    ).ask()
    print(f"✅ Selected: {color}")


def demo_checkbox():
    """Demo checkbox selection."""
    hobbies = questionary.checkbox(
        "Select your hobbies:",
        choices=[
            questionary.Separator("=== Indoor ==="),
            "📚 Reading",
            "🎮 Gaming",
            "🍳 Cooking",
            questionary.Separator("=== Outdoor ==="),
            "🥾 Hiking",
            "🚴 Cycling",
            "🏊 Swimming",
        ],
    ).ask()
    print(f"✅ Selected hobbies: {', '.join(hobbies) if hobbies else 'None'}")


def demo_autocomplete():
    """Demo autocomplete."""
    languages = [
        "Python",
        "JavaScript",
        "Java",
        "C++",
        "Go",
        "Rust",
        "TypeScript",
        "C#",
    ]
    language = questionary.autocomplete(
        "Choose a programming language (type to filter):", choices=languages
    ).ask()
    print(f"✅ Selected language: {language}")


def demo_rawselect():
    """Demo raw select."""
    option = questionary.rawselect(
        "Choose an option (raw interface):",
        choices=["Option A", "Option B", "Option C"],
    ).ask()
    print(f"✅ Selected: {option}")


def demo_confirm():
    """Demo confirmation."""
    confirmed = questionary.confirm("Do you like this demo?", default=True).ask()
    print(f"✅ Response: {'Yes' if confirmed else 'No'}")


def demo_email_validator():
    """Demo email validator."""
    email = questionary.text("Enter your email:", validate=EmailValidator()).ask()
    if email:
        print(f"✅ Valid email: {email}")


def demo_url_validator():
    """Demo URL validator."""
    url = questionary.text("Enter a website URL:", validate=URLValidator()).ask()
    if url:
        print(f"✅ Valid URL: {url}")


def demo_date_validator():
    """Demo date validator."""
    birthday = questionary.text(
        "Enter your birthday (YYYY-MM-DD):",
        validate=DateValidator(format_str="%Y-%m-%d", max_date=date.today()),
    ).ask()
    if birthday:
        print(f"✅ Valid date: {birthday}")


def demo_number_validator():
    """Demo number validator."""
    temp = questionary.text(
        "Enter temperature (-50 to 50°C):",
        validate=NumberValidator(min_value=-50, max_value=50, allow_float=True),
    ).ask()
    if temp:
        print(f"✅ Valid temperature: {temp}°C")


def demo_range_validator():
    """Demo range validator."""
    percentage = questionary.text(
        "Enter percentage (0-100):", validate=RangeValidator(0, 100)
    ).ask()
    if percentage:
        print(f"✅ Valid percentage: {percentage}%")


def demo_regex_validator():
    """Demo regex validator."""
    phone = questionary.text(
        "Enter phone number (XXX-XXX-XXXX):",
        validate=RegexValidator(
            r"^\d{3}-\d{3}-\d{4}$", "Please enter phone in format XXX-XXX-XXXX"
        ),
    ).ask()
    if phone:
        print(f"✅ Valid phone: {phone}")


def demo_format_date():
    """Demo date formatting."""
    today = date.today()
    formatted = qe.format_date(today, "%B %d, %Y")
    print(f"✅ Today formatted: {formatted}")

    # Show different formats
    formats = [
        ("%Y-%m-%d", "ISO format"),
        ("%m/%d/%Y", "US format"),
        ("%d/%m/%Y", "European format"),
        ("%A, %B %d, %Y", "Full format"),
    ]

    for fmt, desc in formats:
        result = qe.format_date(today, fmt)
        print(f"   {desc}: {result}")


def demo_format_number():
    """Demo number formatting."""
    number = 1234567.89

    print("✅ Number formatting examples:")
    print(f"   Original: {number}")
    print(f"   With separators: {qe.format_number(number, thousands_sep=True)}")
    print(f"   Currency: {qe.format_number(number, decimal_places=2, currency='$')}")
    print(
        f"   Percentage: {qe.format_number(0.1567, percentage=True, decimal_places=1)}"
    )


def demo_theming():
    """Demo theming system."""
    print("✅ Available themes:")
    for theme_name in qe.THEMES:
        print(f"   • {theme_name}")

    # Create custom theme
    custom_palette = ColorPalette(
        primary="#00ff00", secondary="#ff00ff", success="#00ff00", error="#ff0000"
    )

    custom_theme = qe.create_theme("Demo Theme", palette=custom_palette)
    print(f"\n   Created custom theme: {custom_theme.name}")
    print(f"   Primary color: {custom_theme.palette.primary}")


def demo_progress_tracker():
    """Demo progress tracker."""
    with qe.ProgressTracker("Demo Process", total_steps=4) as progress:
        progress.step("Initializing...")
        time.sleep(0.8)
        progress.step("Loading data...")
        time.sleep(0.8)
        progress.step("Processing...")
        time.sleep(0.8)
        progress.step("Finalizing...")
        time.sleep(0.8)
        progress.complete("✅ Process completed!")


def demo_form():
    """Demo form functionality."""
    form_data = questionary.form(
        name=questionary.text("Name:", validate=lambda x: len(x) > 0),
        email=questionary.text("Email:", validate=EmailValidator()),
        age=qe.number("Age:", min_value=13, max_value=120, allow_float=False),
        subscribe=questionary.confirm("Subscribe to newsletter?", default=False),
    ).ask()

    if form_data:
        print("✅ Form completed:")
        for key, value in form_data.items():
            print(f"   {key}: {value}")


def demo_path():
    """Demo path selection."""
    print("✅ Path selection would open a file browser")
    print("   (Skipping for demo - requires file system interaction)")


def demo_press_key():
    """Demo press any key."""
    print("✅ Press any key demonstration:")
    questionary.press_any_key_to_continue("Press any key to continue...").ask()
    print("   Key was pressed!")


def demo_print():
    """Demo styled print."""
    print("✅ Styled print examples:")
    questionary.print("Success message!", style="bold fg:green")
    questionary.print("Warning message!", style="bold fg:yellow")
    questionary.print("Error message!", style="bold fg:red")
    questionary.print("Info message!", style="fg:blue")


def run_full_demo():
    """Run a condensed version of all demos."""
    print("\n🚀 RUNNING CONDENSED FULL DEMO")
    print("=" * 50)

    with qe.ProgressTracker("Full Demo", total_steps=6) as progress:
        progress.step("Testing basic inputs...")
        demo_text()
        demo_number()

        progress.step("Testing selections...")
        demo_select()

        progress.step("Testing validations...")
        demo_email_validator()

        progress.step("Testing utilities...")
        demo_format_date()

        progress.step("Testing theming...")
        demo_theming()

        progress.complete("All components tested!")


def main():
    """Run the interactive component explorer."""

    print("🎯 QUESTIONARY COMPONENT EXPLORER")
    print("=" * 60)
    print("Welcome! This interactive tool lets you explore all")
    print("questionary and questionary-extended components.")
    print()

    try:
        show_component_menu()
    except KeyboardInterrupt:
        print("\n\n⚠️  Explorer interrupted by user")
        print("👋 Thanks for exploring questionary components!")
    except Exception as e:
        print(f"\n\n❌ Explorer error: {e}")


if __name__ == "__main__":
    main()
