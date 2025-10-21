"""Example: Advanced form building with questionary-extended."""

import questionary_extended as qe
from questionary_extended import Choice, Separator


def build_user_profile_form():
    """Build a comprehensive user profile form."""
    
    form_questions = [
        # Personal Information
        {
            "type": "text",
            "name": "full_name",
            "message": "Full Name:",
            "validate": lambda text: len(text) > 0 or "Name is required"
        },
        {
            "type": "text", 
            "name": "email",
            "message": "Email Address:",
            "validate": qe.EmailValidator()
        },
        {
            "type": "number",
            "name": "age", 
            "message": "Age:",
            "min_value": 18,
            "max_value": 120,
            "allow_float": False
        },
        
        # Professional Information
        {
            "type": "select",
            "name": "experience_level",
            "message": "Experience Level:",
            "choices": [
                Choice("Junior (0-2 years)", "junior"),
                Choice("Mid-level (2-5 years)", "mid"),  
                Choice("Senior (5-10 years)", "senior"),
                Choice("Lead/Principal (10+ years)", "lead")
            ]
        },
        {
            "type": "checkbox",
            "name": "skills",
            "message": "Technical Skills:",
            "choices": [
                Separator("=== Frontend ==="),
                "JavaScript",
                "TypeScript", 
                "React",
                "Vue.js",
                Separator("=== Backend ==="),
                "Python",
                "Node.js",
                "Java",
                "Go",
                Separator("=== Database ==="),
                "PostgreSQL",
                "MongoDB", 
                "Redis"
            ]
        },
        
        # Preferences
        {
            "type": "select",
            "name": "work_style",
            "message": "Preferred work style:",
            "choices": ["Remote", "Hybrid", "On-site", "Flexible"]
        },
        {
            "type": "rating",
            "name": "collaboration_importance",
            "message": "How important is team collaboration?",
            "max_rating": 5
        },
        
        # Conditional questions
        {
            "type": "confirm",
            "name": "open_to_relocation", 
            "message": "Open to relocation?",
            "default": False
        },
        {
            "type": "text",
            "name": "preferred_locations",
            "message": "Preferred locations (comma-separated):",
            "when": lambda answers: answers.get("open_to_relocation", False)
        }
    ]
    
    return qe.form(form_questions)


def build_project_setup_wizard():
    """Build a multi-step project setup wizard."""
    
    steps = [
        qe.ProgressStep(
            name="project_type",
            description="Choose project type",
            question={
                "type": "select",
                "message": "What type of project?",
                "choices": ["Web Application", "Mobile App", "Desktop App", "CLI Tool", "Library"]
            }
        ),
        qe.ProgressStep(
            name="framework",
            description="Select framework", 
            question={
                "type": "select",
                "message": "Choose framework:",
                "choices": lambda answers: {
                    "Web Application": ["Django", "Flask", "FastAPI", "React", "Vue.js"],
                    "Mobile App": ["React Native", "Flutter", "Ionic"],
                    "Desktop App": ["Electron", "Tkinter", "PyQt"],
                    "CLI Tool": ["Click", "Typer", "Fire"],
                    "Library": ["Pure Python", "C Extension", "Cython"]
                }.get(answers.get("project_type"), [])
            }
        ),
        qe.ProgressStep(
            name="features",
            description="Select features",
            question={
                "type": "checkbox", 
                "message": "Which features do you need?",
                "choices": ["Database", "Authentication", "API", "Tests", "Documentation", "CI/CD"]
            }
        ),
        qe.ProgressStep(
            name="database",
            description="Configure database",
            question={
                "type": "select",
                "message": "Choose database:",
                "choices": ["PostgreSQL", "MySQL", "SQLite", "MongoDB", "None"],
                "when": lambda answers: "Database" in answers.get("features", [])
            }
        )
    ]
    
    return qe.wizard(steps, allow_back=True, save_progress=True)


def main():
    """Demonstrate advanced form and wizard functionality."""
    
    print("🚀 Advanced Forms & Wizards")
    print("=" * 40)
    
    # User Profile Form
    print("\n📋 User Profile Form")
    print("-" * 20)
    
    profile_data = build_user_profile_form().ask()
    
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
    
    project_config = build_project_setup_wizard().ask()
    
    if project_config:
        print("\n✅ Project configured successfully!")
        print("Configuration:")
        for key, value in project_config.items():
            print(f"  {key}: {value}")
    
    # Table Input Example  
    print("\n\n📊 Table Input Example")
    print("-" * 22)
    
    team_data = qe.table(
        "Enter team member information:",
        columns=[
            qe.Column(name="name", type=qe.ColumnType.TEXT, width=20, required=True),
            qe.Column(name="role", type=qe.ColumnType.SELECT, width=15, 
                     choices=["Developer", "Designer", "Manager", "QA"]),
            qe.Column(name="experience", type=qe.ColumnType.NUMBER, width=10, min_value=0, max_value=50)
        ],
        min_rows=1,
        max_rows=5
    ).ask()
    
    if team_data:
        print(f"\n✅ Team data collected: {len(team_data)} members")


if __name__ == "__main__":
    main()