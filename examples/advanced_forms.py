"""Example: Advanced form building with questionary-extended."""

import questionary_extended as qe
import questionary
from questionary_extended import EmailValidator


def build_user_profile_form():
    """Build a comprehensive user profile form."""
    
    # Use questionary's form functionality with our validators
    form_data = questionary.form(
        full_name=questionary.text(
            "Full Name:",
            validate=lambda text: len(text) > 0 or "Name is required"
        ),
        email=questionary.text(
            "Email Address:",
            validate=EmailValidator()
        ),
        age=qe.number(
            "Age:",
            min_value=18,
            max_value=120,
            allow_float=False
        ),
        experience_level=questionary.select(
            "Experience Level:",
            choices=[
                "Junior (0-2 years)",
                "Mid-level (2-5 years)",  
                "Senior (5-10 years)",
                "Lead/Principal (10+ years)"
            ]
        ),
        skills=questionary.checkbox(
            "Technical Skills:",
            choices=[
                questionary.Separator("=== Frontend ==="),
                "JavaScript",
                "TypeScript", 
                "React",
                "Vue.js",
                questionary.Separator("=== Backend ==="),
                "Python",
                "Node.js",
                "Java",
                "Go",
                questionary.Separator("=== Database ==="),
                "PostgreSQL",
                "MongoDB", 
                "Redis"
            ]
        ),
        work_style=questionary.select(
            "Preferred work style:",
            choices=["Remote", "Hybrid", "On-site", "Flexible"]
        ),
        open_to_relocation=questionary.confirm(
            "Open to relocation?",
            default=False
        )
    ).ask()
    
    # Handle conditional question
    if form_data and form_data.get("open_to_relocation"):
        preferred_locations = questionary.text(
            "Preferred locations (comma-separated):"
        ).ask()
        form_data["preferred_locations"] = preferred_locations
    
    return form_data


def build_project_setup_wizard():
    """Build a multi-step project setup wizard."""
    
    # Step 1: Project Type
    project_type = questionary.select(
        "What type of project?",
        choices=["Web Application", "Mobile App", "Desktop App", "CLI Tool", "Library"]
    ).ask()
    
    if not project_type:
        return None
    
    # Step 2: Framework (based on project type)
    framework_choices = {
        "Web Application": ["Django", "Flask", "FastAPI", "React", "Vue.js"],
        "Mobile App": ["React Native", "Flutter", "Ionic"],
        "Desktop App": ["Electron", "Tkinter", "PyQt"],
        "CLI Tool": ["Click", "Typer", "Fire"],
        "Library": ["Pure Python", "C Extension", "Cython"]
    }
    
    framework = questionary.select(
        "Choose framework:",
        choices=framework_choices.get(project_type, [])
    ).ask()
    
    if not framework:
        return None
    
    # Step 3: Features
    features = questionary.checkbox(
        "Which features do you need?",
        choices=["Database", "Authentication", "API", "Tests", "Documentation", "CI/CD"]
    ).ask()
    
    if not features:
        features = []
    
    # Step 4: Database (conditional)
    database = None
    if "Database" in features:
        database = questionary.select(
            "Choose database:",
            choices=["PostgreSQL", "MySQL", "SQLite", "MongoDB", "None"]
        ).ask()
    
    return {
        "project_type": project_type,
        "framework": framework,
        "features": features,
        "database": database
    }


def main():
    """Demonstrate advanced form and wizard functionality."""
    
    print("🚀 Advanced Forms & Wizards")
    print("=" * 40)
    
    # User Profile Form
    print("\n📋 User Profile Form")
    print("-" * 20)
    
    profile_data = build_user_profile_form()
    
    if profile_data:
        print("\n✅ Profile created successfully!")
        print("Profile Summary:")
        for key, value in profile_data.items():
            if isinstance(value, list):
                print(f"  {key}: {', '.join(value)}")
            else:
                print(f"  {key}: {value}")
    
    # Project Setup Wizard
    print("\n\n🧙‍♂️ Project Setup Wizard")
    print("-" * 25)
    
    with qe.progress_tracker("Project Setup", total_steps=4) as progress:
        progress.step("Selecting project type...")
        project_config = build_project_setup_wizard()
        
        if project_config:
            progress.step("Validating configuration...")
            progress.step("Creating project structure...")
            progress.complete("Project setup complete!")
            
            print("\n✅ Project configured successfully!")
            print("Configuration:")
            for key, value in project_config.items():
                if value:
                    if isinstance(value, list):
                        print(f"  {key}: {', '.join(value)}")
                    else:
                        print(f"  {key}: {value}")
        else:
            print("Project setup cancelled.")
    
    # Rating Example
    print("\n\n⭐ Experience Rating")
    print("-" * 18)
    
    overall_rating = qe.rating(
        "How would you rate this experience?",
        max_rating=5,
        icon="⭐"
    ).ask()
    
    if overall_rating:
        print(f"\n✅ Thank you for rating: {overall_rating}/5 stars!")


if __name__ == "__main__":
    main()