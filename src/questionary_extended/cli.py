"""
Command-line interface for questionary-extended.
"""

# COVERAGE_EXCLUDE: thin wrapper — do not add original logic here
# COVERAGE_EXCLUDE_ALLOW_COMPLEX: intentionally contains original logic; exempt from AST triviality checks

import sys

import click
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .prompts import (
    ProgressTracker,
    color,
    enhanced_text,
    number,
    rating,
    tree_select,
)
from .prompts import (
    date as date_prompt,
)
from .styles import THEMES, get_theme_names
from .utils import format_date, format_number

console = Console()


@click.group()
@click.version_option(version=__version__)
@click.option(
    "--theme",
    type=click.Choice(get_theme_names()),
    default="dark",
    help="Theme to use for prompts",
)
@click.pass_context
def cli(ctx: click.Context, theme: str) -> None:
    """
    Questionary Extended - Advanced CLI prompts and forms.

    Interactive command-line interface builder with enhanced input types,
    validation, styling, and workflow management.
    """
    ctx.ensure_object(dict)
    ctx.obj["theme"] = theme


@cli.command()
def demo() -> None:
    """Run an interactive demo of questionary-extended features."""
    console.print(
        Panel.fit(
            "[bold blue]Questionary Extended Demo[/bold blue]\n"
            "Experience the advanced prompt capabilities",
            border_style="blue",
        )
    )

    # Basic enhanced text
    name = enhanced_text("What's your name?").ask()
    console.print(f"Hello, [bold]{name}[/bold]!")

    # Numeric input
    age = number(
        "What's your age?", min_value=0, max_value=150, allow_float=False
    ).ask()

    if age:
        console.print(f"You are [bold]{age}[/bold] years old.")

    # Date input
    # Use the prompts.date helper (renamed to avoid collision with datetime.date)
    birthday = date_prompt(
        "When is your birthday?", max_date=None, format_str="%Y-%m-%d"
    ).ask()

    if birthday:
        console.print(f"Your birthday is [bold]{birthday}[/bold].")

    # Tree selection
    language = tree_select(
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
        console.print(f"Great choice: [bold]{language}[/bold]!")

    # Rating
    satisfaction = rating(
        "How satisfied are you with this demo?", max_rating=5, icon="⭐"
    ).ask()

    if satisfaction:
        console.print(f"Thanks for the [bold]{satisfaction}[/bold] star rating!")

    console.print("\n[green]Demo completed! 🎉[/green]")


@cli.command()
@click.option("--output", "-o", type=click.Path(), help="Save form data to file")
def form_builder() -> None:
    """Interactive form builder."""
    console.print("[bold]Interactive Form Builder[/bold]")

    # Build form definition
    form_questions = []

    while True:
        add_field = questionary.confirm("Add a field to your form?", default=True).ask()
        if not add_field:
            break

        field_name = questionary.text("Field name:").ask()
        field_type = questionary.select(
            "Field type:",
            choices=[
                "text",
                "number",
                "email",
                "date",
                "select",
                "checkbox",
                "confirm",
            ],
        ).ask()

        field_message = questionary.text("Field prompt:").ask()

        question = {"type": field_type, "name": field_name, "message": field_message}

        # Add type-specific options
        if field_type == "select":
            choices_input = questionary.text("Choices (comma-separated):").ask()
            question["choices"] = [c.strip() for c in choices_input.split(",")]

        form_questions.append(question)

    # Execute the form
    if form_questions:
        console.print("\n[bold]Running your form:[/bold]")
        results = questionary.prompt(form_questions)

        # Display results
        table = Table(title="Form Results")
        table.add_column("Field")
        table.add_column("Value")

        for key, value in results.items():
            table.add_row(key, str(value))

        console.print(table)


@cli.command()
def themes() -> None:
    """List available themes."""
    table = Table(title="Available Themes")
    table.add_column("Name", style="cyan")
    table.add_column("Primary Color", style="magenta")
    table.add_column("Description")

    for theme_name, theme in THEMES.items():
        table.add_row(
            theme_name,
            theme.palette.primary,
            f"A {theme.name.lower()} themed color scheme",
        )

    console.print(table)


@cli.command()
@click.argument(
    "prompt_type",
    type=click.Choice(["text", "number", "date", "select", "rating", "color"]),
)
def quick(prompt_type: str) -> None:
    """Quick prompt for testing different input types."""

    if prompt_type == "text":
        result = enhanced_text("Enter some text:").ask()

    elif prompt_type == "number":
        result = number("Enter a number:", min_value=0, max_value=1000).ask()
        if result:
            result = format_number(int(result), thousands_sep=True)

    elif prompt_type == "date":
        result = date_prompt("Enter a date:", format_str="%Y-%m-%d").ask()
        if result:
            result = format_date(result, "%B %d, %Y")

    elif prompt_type == "select":
        result = questionary.select(
            "Choose an option:", choices=["Option 1", "Option 2", "Option 3"]
        ).ask()

    elif prompt_type == "rating":
        result = rating("Rate this experience:", max_rating=5).ask()

    elif prompt_type == "color":
        result = color("Pick a color:", formats=["hex", "rgb"]).ask()

    if result:
        console.print(f"[green]Result:[/green] {result}")
    else:
        console.print("[yellow]No input provided[/yellow]")


@cli.command()
@click.option("--steps", "-s", default=3, help="Number of wizard steps")
def wizard_demo(steps: int) -> None:
    """Demonstrate wizard functionality."""

    with ProgressTracker("Wizard Demo", total_steps=steps) as progress:
        for i in range(1, steps + 1):
            progress.step(f"Step {i} of {steps}")

            result = questionary.text(f"Step {i} - Enter some data:").ask()

            if result:
                console.print(f"  Captured: [cyan]{result}[/cyan]")

            # Simulate some processing time
            import time

            time.sleep(0.5)

        progress.complete("Wizard completed successfully!")


def main() -> None:
    """Entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if (
    __name__ == "__main__"
):  # pragma: no cover - exercised only when running module as script
    main()
