#!/usr/bin/env python3
"""
Real-World Application Demo: Employee Management System

This demo showcases a complete employee management system using TUI Engine
with questionary integration, demonstrating real-world usage patterns.

Features demonstrated:
- Multi-step employee onboarding
- Employee data management
- Performance reviews
- System configuration
- Reporting and analytics
- Data export/import
- Role-based workflows
"""

import os
import sys
import json
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tui_engine.themes import TUIEngineThemes
from tui_engine.form_builder import (
    FormBuilder, FieldDefinition, FieldType, 
    create_registration_form, create_contact_form, DynamicForm
)
from tui_engine.validation import create_form_validator


@dataclass
class Employee:
    """Employee data model."""
    employee_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    department: str
    position: str
    start_date: str
    manager: str
    salary: float
    status: str = "active"
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = datetime.datetime.now().isoformat()


@dataclass
class PerformanceReview:
    """Performance review data model."""
    review_id: str
    employee_id: str
    reviewer_id: str
    review_period: str
    overall_rating: int
    goals_met: bool
    areas_of_strength: str
    areas_for_improvement: str
    career_goals: str
    reviewer_comments: str
    employee_comments: str
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()


class EmployeeManagementSystem:
    """Complete employee management system."""
    
    def __init__(self, data_dir: str = "hr_data"):
        """Initialize the management system."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.employees_file = self.data_dir / "employees.json"
        self.reviews_file = self.data_dir / "reviews.json"
        self.config_file = self.data_dir / "config.json"
        
        self.employees: Dict[str, Employee] = {}
        self.reviews: Dict[str, PerformanceReview] = {}
        self.config = {
            "theme": "professional_blue",
            "company_name": "TUI Corp",
            "hr_email": "hr@tuicorp.com",
            "departments": ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations"],
            "positions": {
                "Engineering": ["Software Engineer", "Senior Engineer", "Tech Lead", "Engineering Manager"],
                "Sales": ["Sales Rep", "Account Manager", "Sales Director"],
                "Marketing": ["Marketing Specialist", "Content Creator", "Marketing Manager"],
                "HR": ["HR Specialist", "HR Business Partner", "HR Director"],
                "Finance": ["Financial Analyst", "Accountant", "Finance Manager"],
                "Operations": ["Operations Specialist", "Operations Manager", "COO"]
            }
        }
        
        self.load_data()
    
    def load_data(self):
        """Load data from files."""
        # Load employees
        if self.employees_file.exists():
            with open(self.employees_file, 'r') as f:
                data = json.load(f)
                self.employees = {k: Employee(**v) for k, v in data.items()}
        
        # Load reviews
        if self.reviews_file.exists():
            with open(self.reviews_file, 'r') as f:
                data = json.load(f)
                self.reviews = {k: PerformanceReview(**v) for k, v in data.items()}
        
        # Load config
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
    
    def save_data(self):
        """Save data to files."""
        # Save employees
        with open(self.employees_file, 'w') as f:
            data = {k: asdict(v) for k, v in self.employees.items()}
            json.dump(data, f, indent=2)
        
        # Save reviews
        with open(self.reviews_file, 'w') as f:
            data = {k: asdict(v) for k, v in self.reviews.items()}
            json.dump(data, f, indent=2)
        
        # Save config
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def run_main_menu(self):
        """Run the main application menu."""
        while True:
            self.show_banner()
            print("\n🏢 EMPLOYEE MANAGEMENT SYSTEM")
            print("=" * 50)
            print("1. 👤 Employee Onboarding")
            print("2. 📋 Employee Management")
            print("3. 📊 Performance Reviews")
            print("4. 📈 Reports & Analytics")
            print("5. ⚙️  System Configuration")
            print("6. 💾 Data Management")
            print("7. 🔍 Search & Filter")
            print("8. 📤 Export Data")
            print("9. 📥 Import Data")
            print("0. 🚪 Exit")
            print("=" * 50)
            
            try:
                choice = input("Select option (0-9): ").strip()
                
                if choice == "0":
                    self.save_data()
                    print("👋 Goodbye! Data saved successfully.")
                    break
                elif choice == "1":
                    self.employee_onboarding_workflow()
                elif choice == "2":
                    self.employee_management_menu()
                elif choice == "3":
                    self.performance_review_workflow()
                elif choice == "4":
                    self.show_reports_analytics()
                elif choice == "5":
                    self.system_configuration()
                elif choice == "6":
                    self.data_management_menu()
                elif choice == "7":
                    self.search_filter_menu()
                elif choice == "8":
                    self.export_data()
                elif choice == "9":
                    self.import_data()
                else:
                    print("❌ Invalid choice. Please try again.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                self.save_data()
                print("\n👋 Exiting... Data saved.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_banner(self):
        """Show application banner."""
        print("\n" + "=" * 60)
        print(f"🏢 {self.config['company_name'].upper()} - EMPLOYEE MANAGEMENT SYSTEM")
        print("=" * 60)
        print(f"📊 Employees: {len(self.employees)} | Reviews: {len(self.reviews)}")
        print(f"🎨 Theme: {self.config['theme']} | Contact: {self.config['hr_email']}")
        print("=" * 60)
    
    def employee_onboarding_workflow(self):
        """Complete employee onboarding workflow."""
        print("\n👤 EMPLOYEE ONBOARDING WORKFLOW")
        print("=" * 50)
        print("This workflow will guide you through the complete onboarding process.")
        print("Steps: Personal Info → Work Details → IT Setup → System Access → Welcome")
        print()
        
        # Step 1: Personal Information
        print("📋 Step 1: Personal Information")
        print("-" * 30)
        
        personal_form = self.create_personal_info_form()
        
        print("Please complete the personal information form:")
        print(personal_form.render_form())
        
        # Simulate form filling (in real app, this would be interactive)
        employee_id = f"EMP{len(self.employees) + 1:04d}"
        
        personal_data = {
            "employee_id": employee_id,
            "first_name": input("First Name: "),
            "last_name": input("Last Name: "),
            "email": input("Email: "),
            "phone": input("Phone: "),
        }
        
        for field, value in personal_data.items():
            personal_form.set_field_value(field, value)
        
        if not personal_form.validate_form():
            print("❌ Personal information validation failed:")
            for error in personal_form.get_validation_errors():
                print(f"   • {error}")
            return
        
        print("✅ Personal information validated successfully!")
        
        # Step 2: Work Information
        print("\n📋 Step 2: Work Information")
        print("-" * 30)
        
        work_form = self.create_work_info_form()
        
        department = input(f"Department ({', '.join(self.config['departments'])}): ")
        if department not in self.config['departments']:
            print(f"❌ Invalid department. Using 'Engineering' as default.")
            department = "Engineering"
        
        positions = self.config['positions'].get(department, ["Specialist"])
        position = input(f"Position ({', '.join(positions)}): ")
        if position not in positions:
            position = positions[0]
        
        work_data = {
            "department": department,
            "position": position,
            "start_date": input("Start Date (YYYY-MM-DD): "),
            "manager": input("Manager Name: "),
            "salary": float(input("Annual Salary: ") or "50000"),
        }
        
        for field, value in work_data.items():
            work_form.set_field_value(field, value)
        
        if not work_form.validate_form():
            print("❌ Work information validation failed:")
            for error in work_form.get_validation_errors():
                print(f"   • {error}")
            return
        
        print("✅ Work information validated successfully!")
        
        # Step 3: IT Setup
        print("\n📋 Step 3: IT Setup")
        print("-" * 30)
        
        it_form = self.create_it_setup_form()
        
        it_data = {
            "laptop_preference": input("Laptop (mac/windows/linux): ") or "mac",
            "software_needs": input("Special software requirements: ") or "Standard development tools",
            "security_clearance": input("Security clearance needed (y/n): ").lower() == 'y',
            "remote_access": input("Remote access required (y/n): ").lower() == 'y',
        }
        
        for field, value in it_data.items():
            it_form.set_field_value(field, value)
        
        print("✅ IT setup configured successfully!")
        
        # Step 4: Create Employee Record
        print("\n📋 Step 4: Creating Employee Record")
        print("-" * 30)
        
        all_data = {**personal_data, **work_data}
        employee = Employee(**all_data)
        self.employees[employee_id] = employee
        
        print(f"✅ Employee record created: {employee.first_name} {employee.last_name} ({employee_id})")
        
        # Step 5: Welcome Package
        print("\n📋 Step 5: Welcome Package")
        print("-" * 30)
        
        self.generate_welcome_package(employee)
        
        print("🎉 Onboarding completed successfully!")
        print(f"📧 Welcome email sent to {employee.email}")
        print(f"🆔 Employee ID: {employee_id}")
        print(f"📅 Start Date: {employee.start_date}")
        
        # Save data
        self.save_data()
    
    def create_personal_info_form(self) -> DynamicForm:
        """Create personal information form."""
        builder = FormBuilder(self.config['theme'])
        schema = builder.create_form("personal_info", "Personal Information")
        
        fields = [
            FieldDefinition("employee_id", FieldType.TEXT, required=True, readonly=True),
            FieldDefinition("first_name", FieldType.TEXT, required=True, min_length=2),
            FieldDefinition("last_name", FieldType.TEXT, required=True, min_length=2),
            FieldDefinition("email", FieldType.EMAIL, required=True),
            FieldDefinition("phone", FieldType.PHONE, required=True),
            FieldDefinition("address", FieldType.TEXT, required=False),
            FieldDefinition("emergency_contact", FieldType.TEXT, required=True),
            FieldDefinition("emergency_phone", FieldType.PHONE, required=True),
        ]
        
        for field in fields:
            builder.add_field("personal_info", field)
        
        return builder.build_form("personal_info")
    
    def create_work_info_form(self) -> DynamicForm:
        """Create work information form."""
        builder = FormBuilder(self.config['theme'])
        schema = builder.create_form("work_info", "Work Information")
        
        dept_choices = {dept.lower(): dept for dept in self.config['departments']}
        
        fields = [
            FieldDefinition("department", FieldType.SELECT, 
                          choices=dept_choices, required=True),
            FieldDefinition("position", FieldType.TEXT, required=True),
            FieldDefinition("start_date", FieldType.DATE, required=True),
            FieldDefinition("manager", FieldType.TEXT, required=True),
            FieldDefinition("salary", FieldType.NUMBER, 
                          min_value=30000, max_value=500000, required=True),
            FieldDefinition("employment_type", FieldType.SELECT,
                          choices={"full_time": "Full Time", "part_time": "Part Time", 
                                 "contract": "Contract", "intern": "Intern"}),
            FieldDefinition("work_location", FieldType.SELECT,
                          choices={"office": "Office", "remote": "Remote", "hybrid": "Hybrid"}),
        ]
        
        for field in fields:
            builder.add_field("work_info", field)
        
        return builder.build_form("work_info")
    
    def create_it_setup_form(self) -> DynamicForm:
        """Create IT setup form."""
        builder = FormBuilder(self.config['theme'])
        schema = builder.create_form("it_setup", "IT Setup")
        
        fields = [
            FieldDefinition("laptop_preference", FieldType.SELECT,
                          choices={"mac": "MacBook", "windows": "Windows", "linux": "Linux"}),
            FieldDefinition("software_needs", FieldType.TEXT),
            FieldDefinition("security_clearance", FieldType.CHECKBOX,
                          label="Security clearance required"),
            FieldDefinition("remote_access", FieldType.CHECKBOX,
                          label="Remote access required"),
            FieldDefinition("mobile_device", FieldType.CHECKBOX,
                          label="Company mobile device needed"),
            FieldDefinition("parking_pass", FieldType.CHECKBOX,
                          label="Parking pass needed"),
        ]
        
        for field in fields:
            builder.add_field("it_setup", field)
        
        return builder.build_form("it_setup")
    
    def generate_welcome_package(self, employee: Employee):
        """Generate welcome package for new employee."""
        print(f"\n📦 WELCOME PACKAGE FOR {employee.first_name.upper()} {employee.last_name.upper()}")
        print("=" * 50)
        print(f"🏢 Welcome to {self.config['company_name']}!")
        print(f"👤 Employee ID: {employee.employee_id}")
        print(f"📧 Email: {employee.email}")
        print(f"🏬 Department: {employee.department}")
        print(f"💼 Position: {employee.position}")
        print(f"👨‍💼 Manager: {employee.manager}")
        print(f"📅 Start Date: {employee.start_date}")
        print()
        print("📋 Next Steps:")
        print("1. Complete IT equipment setup")
        print("2. Attend orientation session")
        print("3. Meet your team")
        print("4. Complete required training")
        print("5. Set up direct deposit")
        print()
        print(f"❓ Questions? Contact HR at {self.config['hr_email']}")
    
    def employee_management_menu(self):
        """Employee management menu."""
        while True:
            print("\n👥 EMPLOYEE MANAGEMENT")
            print("=" * 40)
            print("1. 📋 View All Employees")
            print("2. 👤 View Employee Details")
            print("3. ✏️  Edit Employee")
            print("4. ❌ Deactivate Employee")
            print("5. 🔄 Reactivate Employee")
            print("0. ⬅️  Back to Main Menu")
            print("=" * 40)
            
            choice = input("Select option (0-5): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.view_all_employees()
            elif choice == "2":
                self.view_employee_details()
            elif choice == "3":
                self.edit_employee()
            elif choice == "4":
                self.deactivate_employee()
            elif choice == "5":
                self.reactivate_employee()
            else:
                print("❌ Invalid choice.")
            
            input("\nPress Enter to continue...")
    
    def view_all_employees(self):
        """View all employees."""
        print("\n👥 ALL EMPLOYEES")
        print("=" * 80)
        
        if not self.employees:
            print("No employees found.")
            return
        
        # Header
        print(f"{'ID':<8} {'Name':<25} {'Department':<15} {'Position':<20} {'Status':<10}")
        print("-" * 80)
        
        # Employee rows
        for emp in self.employees.values():
            name = f"{emp.first_name} {emp.last_name}"
            print(f"{emp.employee_id:<8} {name:<25} {emp.department:<15} {emp.position:<20} {emp.status:<10}")
        
        print(f"\nTotal: {len(self.employees)} employees")
    
    def view_employee_details(self):
        """View detailed employee information."""
        employee_id = input("Enter Employee ID: ").strip()
        
        if employee_id not in self.employees:
            print(f"❌ Employee {employee_id} not found.")
            return
        
        emp = self.employees[employee_id]
        
        print(f"\n👤 EMPLOYEE DETAILS: {emp.first_name} {emp.last_name}")
        print("=" * 50)
        print(f"🆔 Employee ID: {emp.employee_id}")
        print(f"📧 Email: {emp.email}")
        print(f"📞 Phone: {emp.phone}")
        print(f"🏬 Department: {emp.department}")
        print(f"💼 Position: {emp.position}")
        print(f"👨‍💼 Manager: {emp.manager}")
        print(f"📅 Start Date: {emp.start_date}")
        print(f"💰 Salary: ${emp.salary:,.2f}")
        print(f"📊 Status: {emp.status}")
        print(f"📝 Created: {emp.created_at}")
        print(f"🔄 Updated: {emp.updated_at}")
        
        # Show related reviews
        emp_reviews = [r for r in self.reviews.values() if r.employee_id == employee_id]
        if emp_reviews:
            print(f"\n📊 Performance Reviews: {len(emp_reviews)}")
            for review in emp_reviews:
                print(f"   • {review.review_period}: {review.overall_rating}/5 stars")
    
    def edit_employee(self):
        """Edit employee information."""
        employee_id = input("Enter Employee ID to edit: ").strip()
        
        if employee_id not in self.employees:
            print(f"❌ Employee {employee_id} not found.")
            return
        
        emp = self.employees[employee_id]
        print(f"\n✏️  EDITING: {emp.first_name} {emp.last_name}")
        print("=" * 40)
        print("Leave blank to keep current value")
        
        # Create edit form
        builder = FormBuilder(self.config['theme'])
        schema = builder.create_form("edit_employee", "Edit Employee")
        
        fields = [
            FieldDefinition("first_name", FieldType.TEXT, default_value=emp.first_name),
            FieldDefinition("last_name", FieldType.TEXT, default_value=emp.last_name),
            FieldDefinition("email", FieldType.EMAIL, default_value=emp.email),
            FieldDefinition("phone", FieldType.PHONE, default_value=emp.phone),
            FieldDefinition("department", FieldType.SELECT, 
                          choices={d.lower(): d for d in self.config['departments']},
                          default_value=emp.department.lower()),
            FieldDefinition("position", FieldType.TEXT, default_value=emp.position),
            FieldDefinition("manager", FieldType.TEXT, default_value=emp.manager),
            FieldDefinition("salary", FieldType.NUMBER, default_value=emp.salary),
        ]
        
        for field in fields:
            builder.add_field("edit_employee", field)
        
        form = builder.build_form("edit_employee")
        
        # Simulate form interaction (in real app, this would be interactive)
        print("Current values are pre-filled. Enter new values or press Enter to keep current:")
        
        new_values = {}
        for field_name in ["first_name", "last_name", "email", "phone", "department", "position", "manager", "salary"]:
            current_value = getattr(emp, field_name)
            new_value = input(f"{field_name.replace('_', ' ').title()} [{current_value}]: ").strip()
            if new_value:
                new_values[field_name] = new_value
        
        # Update employee
        if new_values:
            for field, value in new_values.items():
                setattr(emp, field, value)
            emp.updated_at = datetime.datetime.now().isoformat()
            
            print(f"✅ Employee {employee_id} updated successfully!")
            self.save_data()
        else:
            print("ℹ️  No changes made.")
    
    def deactivate_employee(self):
        """Deactivate an employee."""
        employee_id = input("Enter Employee ID to deactivate: ").strip()
        
        if employee_id not in self.employees:
            print(f"❌ Employee {employee_id} not found.")
            return
        
        emp = self.employees[employee_id]
        
        if emp.status == "inactive":
            print(f"ℹ️  Employee {employee_id} is already inactive.")
            return
        
        confirm = input(f"⚠️  Deactivate {emp.first_name} {emp.last_name}? (y/N): ").strip().lower()
        if confirm == 'y':
            emp.status = "inactive"
            emp.updated_at = datetime.datetime.now().isoformat()
            print(f"✅ Employee {employee_id} deactivated.")
            self.save_data()
        else:
            print("❌ Deactivation cancelled.")
    
    def reactivate_employee(self):
        """Reactivate an employee."""
        employee_id = input("Enter Employee ID to reactivate: ").strip()
        
        if employee_id not in self.employees:
            print(f"❌ Employee {employee_id} not found.")
            return
        
        emp = self.employees[employee_id]
        
        if emp.status == "active":
            print(f"ℹ️  Employee {employee_id} is already active.")
            return
        
        emp.status = "active"
        emp.updated_at = datetime.datetime.now().isoformat()
        print(f"✅ Employee {employee_id} reactivated.")
        self.save_data()
    
    def performance_review_workflow(self):
        """Performance review workflow."""
        print("\n📊 PERFORMANCE REVIEW WORKFLOW")
        print("=" * 50)
        
        if not self.employees:
            print("❌ No employees found. Please add employees first.")
            return
        
        # Select employee
        print("📋 Available Employees:")
        for emp in self.employees.values():
            if emp.status == "active":
                print(f"   {emp.employee_id}: {emp.first_name} {emp.last_name} ({emp.department})")
        
        employee_id = input("\nEnter Employee ID for review: ").strip()
        
        if employee_id not in self.employees:
            print(f"❌ Employee {employee_id} not found.")
            return
        
        emp = self.employees[employee_id]
        
        if emp.status != "active":
            print(f"❌ Cannot review inactive employee.")
            return
        
        print(f"\n📊 Creating Performance Review for {emp.first_name} {emp.last_name}")
        print("-" * 50)
        
        # Create review form
        review_form = self.create_performance_review_form()
        
        # Generate review ID
        review_id = f"REV{len(self.reviews) + 1:04d}"
        
        print("Please complete the performance review:")
        print(review_form.render_form())
        
        # Simulate form filling
        review_data = {
            "review_id": review_id,
            "employee_id": employee_id,
            "reviewer_id": input("Reviewer Employee ID: "),
            "review_period": input("Review Period (e.g., 'Q1 2024'): "),
            "overall_rating": int(input("Overall Rating (1-5): ") or "3"),
            "goals_met": input("Goals Met (y/n): ").lower() == 'y',
            "areas_of_strength": input("Areas of Strength: "),
            "areas_for_improvement": input("Areas for Improvement: "),
            "career_goals": input("Career Goals: "),
            "reviewer_comments": input("Reviewer Comments: "),
            "employee_comments": input("Employee Comments: "),
        }
        
        # Create review record
        review = PerformanceReview(**review_data)
        self.reviews[review_id] = review
        
        print(f"\n✅ Performance review {review_id} created successfully!")
        print(f"📊 Overall Rating: {review.overall_rating}/5")
        print(f"🎯 Goals Met: {'Yes' if review.goals_met else 'No'}")
        
        self.save_data()
    
    def create_performance_review_form(self) -> DynamicForm:
        """Create performance review form."""
        builder = FormBuilder(self.config['theme'])
        schema = builder.create_form("performance_review", "Performance Review")
        
        fields = [
            FieldDefinition("overall_rating", FieldType.SELECT,
                          choices={"1": "1 - Poor", "2": "2 - Below Average", 
                                 "3": "3 - Average", "4": "4 - Good", "5": "5 - Excellent"},
                          required=True),
            FieldDefinition("goals_met", FieldType.CHECKBOX,
                          label="Employee met their goals"),
            FieldDefinition("areas_of_strength", FieldType.TEXT, required=True),
            FieldDefinition("areas_for_improvement", FieldType.TEXT, required=True),
            FieldDefinition("career_goals", FieldType.TEXT),
            FieldDefinition("reviewer_comments", FieldType.TEXT, required=True),
            FieldDefinition("employee_comments", FieldType.TEXT),
            FieldDefinition("development_plan", FieldType.TEXT),
            FieldDefinition("promotion_ready", FieldType.CHECKBOX,
                          label="Ready for promotion"),
            FieldDefinition("salary_increase", FieldType.NUMBER,
                          min_value=0, max_value=50000,
                          label="Recommended salary increase"),
        ]
        
        for field in fields:
            builder.add_field("performance_review", field)
        
        return builder.build_form("performance_review")
    
    def show_reports_analytics(self):
        """Show reports and analytics."""
        print("\n📈 REPORTS & ANALYTICS")
        print("=" * 50)
        
        if not self.employees:
            print("❌ No employee data available.")
            return
        
        # Employee statistics
        active_employees = sum(1 for emp in self.employees.values() if emp.status == "active")
        inactive_employees = len(self.employees) - active_employees
        
        print("👥 EMPLOYEE STATISTICS")
        print("-" * 30)
        print(f"Total Employees: {len(self.employees)}")
        print(f"Active: {active_employees}")
        print(f"Inactive: {inactive_employees}")
        
        # Department breakdown
        dept_counts = {}
        dept_salaries = {}
        for emp in self.employees.values():
            if emp.status == "active":
                dept_counts[emp.department] = dept_counts.get(emp.department, 0) + 1
                dept_salaries[emp.department] = dept_salaries.get(emp.department, []) + [emp.salary]
        
        print("\n🏬 DEPARTMENT BREAKDOWN")
        print("-" * 30)
        for dept, count in dept_counts.items():
            avg_salary = sum(dept_salaries[dept]) / len(dept_salaries[dept])
            print(f"{dept}: {count} employees, avg salary: ${avg_salary:,.2f}")
        
        # Performance review statistics
        if self.reviews:
            print("\n📊 PERFORMANCE REVIEW STATISTICS")
            print("-" * 30)
            total_reviews = len(self.reviews)
            avg_rating = sum(r.overall_rating for r in self.reviews.values()) / total_reviews
            goals_met_count = sum(1 for r in self.reviews.values() if r.goals_met)
            
            print(f"Total Reviews: {total_reviews}")
            print(f"Average Rating: {avg_rating:.2f}/5")
            print(f"Goals Met Rate: {goals_met_count/total_reviews*100:.1f}%")
        
        # Salary analysis
        if self.employees:
            salaries = [emp.salary for emp in self.employees.values() if emp.status == "active"]
            if salaries:
                print("\n💰 SALARY ANALYSIS")
                print("-" * 30)
                print(f"Average Salary: ${sum(salaries)/len(salaries):,.2f}")
                print(f"Minimum Salary: ${min(salaries):,.2f}")
                print(f"Maximum Salary: ${max(salaries):,.2f}")
    
    def system_configuration(self):
        """System configuration."""
        print("\n⚙️  SYSTEM CONFIGURATION")
        print("=" * 40)
        
        config_form = self.create_system_config_form()
        
        print("Current configuration:")
        for key, value in self.config.items():
            if key not in ['departments', 'positions']:
                print(f"   {key}: {value}")
        
        print("\nEnter new values (leave blank to keep current):")
        
        new_config = {}
        for key in ['company_name', 'hr_email', 'theme']:
            current = self.config.get(key, '')
            new_value = input(f"{key.replace('_', ' ').title()} [{current}]: ").strip()
            if new_value:
                new_config[key] = new_value
        
        if new_config:
            self.config.update(new_config)
            print("✅ Configuration updated!")
            self.save_data()
        else:
            print("ℹ️  No changes made.")
    
    def create_system_config_form(self) -> DynamicForm:
        """Create system configuration form."""
        builder = FormBuilder(self.config['theme'])
        schema = builder.create_form("system_config", "System Configuration")
        
        theme_choices = {theme: theme.replace('_', ' ').title() 
                        for theme in TUIEngineThemes.get_available_themes()}
        
        fields = [
            FieldDefinition("company_name", FieldType.TEXT, required=True),
            FieldDefinition("hr_email", FieldType.EMAIL, required=True),
            FieldDefinition("theme", FieldType.SELECT, choices=theme_choices),
            FieldDefinition("auto_save", FieldType.CHECKBOX,
                          label="Auto-save data"),
            FieldDefinition("backup_enabled", FieldType.CHECKBOX,
                          label="Enable automatic backups"),
            FieldDefinition("notification_email", FieldType.EMAIL,
                          label="Notification email"),
        ]
        
        for field in fields:
            builder.add_field("system_config", field)
        
        return builder.build_form("system_config")
    
    def data_management_menu(self):
        """Data management menu."""
        print("\n💾 DATA MANAGEMENT")
        print("=" * 30)
        print("1. 🗂️  Backup Data")
        print("2. 📂 Restore Data")
        print("3. 🗑️  Clear All Data")
        print("4. 📊 Data Statistics")
        print("0. ⬅️  Back")
        
        choice = input("Select option (0-4): ").strip()
        
        if choice == "1":
            self.backup_data()
        elif choice == "2":
            self.restore_data()
        elif choice == "3":
            self.clear_all_data()
        elif choice == "4":
            self.show_data_statistics()
    
    def backup_data(self):
        """Create data backup."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.data_dir / f"backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        import shutil
        
        # Copy data files
        for file in [self.employees_file, self.reviews_file, self.config_file]:
            if file.exists():
                shutil.copy2(file, backup_dir)
        
        print(f"✅ Data backed up to: {backup_dir}")
    
    def restore_data(self):
        """Restore data from backup."""
        backup_dirs = [d for d in self.data_dir.iterdir() 
                      if d.is_dir() and d.name.startswith("backup_")]
        
        if not backup_dirs:
            print("❌ No backups found.")
            return
        
        print("📂 Available backups:")
        for i, backup_dir in enumerate(backup_dirs, 1):
            print(f"   {i}. {backup_dir.name}")
        
        try:
            choice = int(input("Select backup to restore: ")) - 1
            if 0 <= choice < len(backup_dirs):
                selected_backup = backup_dirs[choice]
                confirm = input(f"⚠️  Restore from {selected_backup.name}? This will overwrite current data (y/N): ")
                
                if confirm.lower() == 'y':
                    import shutil
                    
                    # Restore files
                    for file_name in ["employees.json", "reviews.json", "config.json"]:
                        backup_file = selected_backup / file_name
                        if backup_file.exists():
                            shutil.copy2(backup_file, self.data_dir)
                    
                    # Reload data
                    self.load_data()
                    print("✅ Data restored successfully!")
                else:
                    print("❌ Restore cancelled.")
            else:
                print("❌ Invalid backup selection.")
        except ValueError:
            print("❌ Invalid input.")
    
    def clear_all_data(self):
        """Clear all data (with confirmation)."""
        confirm1 = input("⚠️  This will delete ALL employee data. Type 'DELETE' to confirm: ")
        if confirm1 != "DELETE":
            print("❌ Data deletion cancelled.")
            return
        
        confirm2 = input("⚠️  Are you absolutely sure? This cannot be undone. Type 'YES': ")
        if confirm2 != "YES":
            print("❌ Data deletion cancelled.")
            return
        
        # Clear data
        self.employees.clear()
        self.reviews.clear()
        
        # Remove files
        for file in [self.employees_file, self.reviews_file]:
            if file.exists():
                file.unlink()
        
        print("✅ All data cleared.")
    
    def show_data_statistics(self):
        """Show data statistics."""
        print("\n📊 DATA STATISTICS")
        print("=" * 30)
        
        print(f"Employee Records: {len(self.employees)}")
        print(f"Performance Reviews: {len(self.reviews)}")
        print(f"Departments: {len(self.config['departments'])}")
        
        # File sizes
        for file in [self.employees_file, self.reviews_file, self.config_file]:
            if file.exists():
                size_kb = file.stat().st_size / 1024
                print(f"{file.name}: {size_kb:.2f} KB")
        
        # Data integrity
        orphaned_reviews = sum(1 for r in self.reviews.values() 
                             if r.employee_id not in self.employees)
        if orphaned_reviews:
            print(f"⚠️  Orphaned reviews: {orphaned_reviews}")
        else:
            print("✅ Data integrity: OK")
    
    def search_filter_menu(self):
        """Search and filter menu."""
        print("\n🔍 SEARCH & FILTER")
        print("=" * 30)
        print("1. 📝 Search by Name")
        print("2. 🏬 Filter by Department")
        print("3. 💼 Filter by Position")
        print("4. 📊 Filter by Status")
        print("5. 📅 Filter by Start Date")
        print("0. ⬅️  Back")
        
        choice = input("Select option (0-5): ").strip()
        
        if choice == "1":
            self.search_by_name()
        elif choice == "2":
            self.filter_by_department()
        elif choice == "3":
            self.filter_by_position()
        elif choice == "4":
            self.filter_by_status()
        elif choice == "5":
            self.filter_by_start_date()
    
    def search_by_name(self):
        """Search employees by name."""
        query = input("Enter name to search: ").strip().lower()
        
        matches = []
        for emp in self.employees.values():
            full_name = f"{emp.first_name} {emp.last_name}".lower()
            if query in full_name:
                matches.append(emp)
        
        if matches:
            print(f"\n🔍 Found {len(matches)} match(es):")
            for emp in matches:
                print(f"   {emp.employee_id}: {emp.first_name} {emp.last_name} ({emp.department})")
        else:
            print("❌ No matches found.")
    
    def filter_by_department(self):
        """Filter employees by department."""
        dept = input(f"Enter department ({', '.join(self.config['departments'])}): ").strip()
        
        matches = [emp for emp in self.employees.values() 
                  if emp.department.lower() == dept.lower()]
        
        if matches:
            print(f"\n🏬 {dept} Department ({len(matches)} employees):")
            for emp in matches:
                print(f"   {emp.employee_id}: {emp.first_name} {emp.last_name} - {emp.position}")
        else:
            print(f"❌ No employees found in {dept} department.")
    
    def filter_by_position(self):
        """Filter employees by position."""
        position = input("Enter position: ").strip()
        
        matches = [emp for emp in self.employees.values() 
                  if position.lower() in emp.position.lower()]
        
        if matches:
            print(f"\n💼 Position '{position}' ({len(matches)} employees):")
            for emp in matches:
                print(f"   {emp.employee_id}: {emp.first_name} {emp.last_name} ({emp.department})")
        else:
            print(f"❌ No employees found with position matching '{position}'.")
    
    def filter_by_status(self):
        """Filter employees by status."""
        status = input("Enter status (active/inactive): ").strip().lower()
        
        matches = [emp for emp in self.employees.values() 
                  if emp.status == status]
        
        if matches:
            print(f"\n📊 {status.title()} Employees ({len(matches)}):")
            for emp in matches:
                print(f"   {emp.employee_id}: {emp.first_name} {emp.last_name} ({emp.department})")
        else:
            print(f"❌ No {status} employees found.")
    
    def filter_by_start_date(self):
        """Filter employees by start date range."""
        start_date = input("Enter start date (YYYY-MM-DD) or leave blank: ").strip()
        end_date = input("Enter end date (YYYY-MM-DD) or leave blank: ").strip()
        
        matches = []
        for emp in self.employees.values():
            emp_date = emp.start_date
            
            include = True
            if start_date and emp_date < start_date:
                include = False
            if end_date and emp_date > end_date:
                include = False
            
            if include:
                matches.append(emp)
        
        if matches:
            range_desc = f"from {start_date or 'beginning'} to {end_date or 'end'}"
            print(f"\n📅 Employees starting {range_desc} ({len(matches)}):")
            for emp in matches:
                print(f"   {emp.employee_id}: {emp.first_name} {emp.last_name} - {emp.start_date}")
        else:
            print("❌ No employees found in the specified date range.")
    
    def export_data(self):
        """Export data to various formats."""
        print("\n📤 EXPORT DATA")
        print("=" * 30)
        print("1. 📄 Export to JSON")
        print("2. 📊 Export to CSV")
        print("3. 📋 Export Employee Report")
        print("4. 📈 Export Analytics Report")
        print("0. ⬅️  Back")
        
        choice = input("Select export format (0-4): ").strip()
        
        if choice == "1":
            self.export_to_json()
        elif choice == "2":
            self.export_to_csv()
        elif choice == "3":
            self.export_employee_report()
        elif choice == "4":
            self.export_analytics_report()
    
    def export_to_json(self):
        """Export all data to JSON."""
        export_data = {
            "employees": {k: asdict(v) for k, v in self.employees.items()},
            "reviews": {k: asdict(v) for k, v in self.reviews.items()},
            "config": self.config,
            "export_date": datetime.datetime.now().isoformat()
        }
        
        filename = f"employee_data_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Data exported to: {filename}")
    
    def export_to_csv(self):
        """Export employee data to CSV."""
        filename = f"employees_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w') as f:
            # Header
            headers = ["Employee ID", "First Name", "Last Name", "Email", "Phone", 
                      "Department", "Position", "Manager", "Start Date", "Salary", "Status"]
            f.write(",".join(headers) + "\n")
            
            # Data rows
            for emp in self.employees.values():
                row = [
                    emp.employee_id, emp.first_name, emp.last_name, emp.email, emp.phone,
                    emp.department, emp.position, emp.manager, emp.start_date, 
                    str(emp.salary), emp.status
                ]
                f.write(",".join(f'"{field}"' for field in row) + "\n")
        
        print(f"✅ Employee data exported to: {filename}")
    
    def export_employee_report(self):
        """Export detailed employee report."""
        filename = f"employee_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"{self.config['company_name']} - EMPLOYEE REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary
            active_count = sum(1 for emp in self.employees.values() if emp.status == "active")
            f.write(f"SUMMARY\n")
            f.write(f"Total Employees: {len(self.employees)}\n")
            f.write(f"Active: {active_count}\n")
            f.write(f"Inactive: {len(self.employees) - active_count}\n\n")
            
            # Department breakdown
            dept_counts = {}
            for emp in self.employees.values():
                if emp.status == "active":
                    dept_counts[emp.department] = dept_counts.get(emp.department, 0) + 1
            
            f.write("DEPARTMENT BREAKDOWN\n")
            for dept, count in dept_counts.items():
                f.write(f"{dept}: {count} employees\n")
            f.write("\n")
            
            # Detailed employee list
            f.write("DETAILED EMPLOYEE LIST\n")
            f.write("-" * 60 + "\n")
            
            for emp in sorted(self.employees.values(), key=lambda x: x.last_name):
                f.write(f"Employee ID: {emp.employee_id}\n")
                f.write(f"Name: {emp.first_name} {emp.last_name}\n")
                f.write(f"Email: {emp.email}\n")
                f.write(f"Department: {emp.department}\n")
                f.write(f"Position: {emp.position}\n")
                f.write(f"Manager: {emp.manager}\n")
                f.write(f"Start Date: {emp.start_date}\n")
                f.write(f"Status: {emp.status}\n")
                f.write("-" * 40 + "\n")
        
        print(f"✅ Employee report exported to: {filename}")
    
    def export_analytics_report(self):
        """Export analytics report."""
        filename = f"analytics_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"{self.config['company_name']} - ANALYTICS REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Employee analytics
            active_employees = [emp for emp in self.employees.values() if emp.status == "active"]
            
            if active_employees:
                salaries = [emp.salary for emp in active_employees]
                f.write("SALARY ANALYTICS\n")
                f.write(f"Average Salary: ${sum(salaries)/len(salaries):,.2f}\n")
                f.write(f"Median Salary: ${sorted(salaries)[len(salaries)//2]:,.2f}\n")
                f.write(f"Min Salary: ${min(salaries):,.2f}\n")
                f.write(f"Max Salary: ${max(salaries):,.2f}\n\n")
            
            # Performance review analytics
            if self.reviews:
                ratings = [r.overall_rating for r in self.reviews.values()]
                f.write("PERFORMANCE REVIEW ANALYTICS\n")
                f.write(f"Total Reviews: {len(self.reviews)}\n")
                f.write(f"Average Rating: {sum(ratings)/len(ratings):.2f}/5\n")
                f.write(f"Highest Rating: {max(ratings)}/5\n")
                f.write(f"Lowest Rating: {min(ratings)}/5\n")
                
                goals_met = sum(1 for r in self.reviews.values() if r.goals_met)
                f.write(f"Goals Met Rate: {goals_met/len(self.reviews)*100:.1f}%\n\n")
            
            # Department analytics
            dept_stats = {}
            for emp in active_employees:
                if emp.department not in dept_stats:
                    dept_stats[emp.department] = {"count": 0, "salaries": []}
                dept_stats[emp.department]["count"] += 1
                dept_stats[emp.department]["salaries"].append(emp.salary)
            
            f.write("DEPARTMENT ANALYTICS\n")
            for dept, stats in dept_stats.items():
                avg_salary = sum(stats["salaries"]) / len(stats["salaries"])
                f.write(f"{dept}:\n")
                f.write(f"  Employees: {stats['count']}\n")
                f.write(f"  Avg Salary: ${avg_salary:,.2f}\n")
                f.write(f"  Salary Range: ${min(stats['salaries']):,.2f} - ${max(stats['salaries']):,.2f}\n\n")
        
        print(f"✅ Analytics report exported to: {filename}")
    
    def import_data(self):
        """Import data from JSON file."""
        filename = input("Enter filename to import: ").strip()
        
        if not os.path.exists(filename):
            print(f"❌ File {filename} not found.")
            return
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Validate data structure
            if 'employees' not in data:
                print("❌ Invalid file format: missing 'employees' section.")
                return
            
            confirm = input(f"⚠️  Import data from {filename}? This will overwrite current data (y/N): ")
            if confirm.lower() != 'y':
                print("❌ Import cancelled.")
                return
            
            # Import employees
            if 'employees' in data:
                self.employees = {k: Employee(**v) for k, v in data['employees'].items()}
                print(f"✅ Imported {len(self.employees)} employees")
            
            # Import reviews
            if 'reviews' in data:
                self.reviews = {k: PerformanceReview(**v) for k, v in data['reviews'].items()}
                print(f"✅ Imported {len(self.reviews)} reviews")
            
            # Import config
            if 'config' in data:
                self.config.update(data['config'])
                print("✅ Imported configuration")
            
            self.save_data()
            print("🎉 Data import completed successfully!")
            
        except json.JSONDecodeError:
            print("❌ Invalid JSON file.")
        except Exception as e:
            print(f"❌ Import error: {e}")


def main():
    """Main application entry point."""
    print("🚀 TUI Engine Real-World Demo: Employee Management System")
    print("This demo showcases a complete HR management system using TUI Engine.")
    print()
    
    try:
        # Initialize system
        ems = EmployeeManagementSystem()
        
        # Run main application
        ems.run_main_menu()
        
    except KeyboardInterrupt:
        print("\n👋 Application interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()