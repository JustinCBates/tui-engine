"""Core prompt implementations - fundamental working versions."""

# COVERAGE_EXCLUDE: thin wrapper — do not add original logic here
# COVERAGE_EXCLUDE_ALLOW_COMPLEX: intentionally contains original logic; exempt from AST triviality checks

from types import TracebackType
from typing import Any, Callable, Dict, List, Optional, Type, Union

import questionary
from questionary import Question


class LazyQuestion:
    """A lightweight lazy wrapper around a questionary factory.

    Construction is cheap and does not create a prompt_toolkit
    PromptSession. Call .build() or .ask() to materialize and run the
    underlying question.
    """

    def __init__(
        self, factory: Callable[..., Question], *args: Any, **kwargs: Any
    ) -> None:
        self._factory = factory
        self._args = args
        self._kwargs = kwargs

    def build(self) -> Question:
        return self._factory(*self._args, **self._kwargs)

    def __call__(self) -> Question:
        return self.build()

    def ask(self, *args: Any, **kwargs: Any) -> Any:
        return self.build().ask(*args, **kwargs)

    def __repr__(self) -> str:  # helpful in tests/benchmarks
        factory_name = getattr(self._factory, "__name__", repr(self._factory))
        return (
            f"<LazyQuestion factory={factory_name} args={self._args} "
            f"kwargs={self._kwargs}>"
        )


def enhanced_text(
    message: str,
    default: str = "",
    multiline: bool = False,
    validator: Optional[Callable[..., Any]] = None,
    **kwargs: Any,
) -> "LazyQuestion | Question":
    """Enhanced text input - starting with a simple working version."""
    if validator is not None:
        kwargs["validate"] = validator
    return LazyQuestion(
        questionary.text, message, default=default, multiline=multiline, **kwargs
    )


def number(
    message: str,
    default: Optional[Union[int, float]] = None,
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    allow_float: bool = True,
    **kwargs: Any,
) -> "LazyQuestion | Question":
    """Numeric input with validation."""
    from .validators import NumberValidator

    validator = NumberValidator(
        min_value=min_value, max_value=max_value, allow_float=allow_float
    )

    default_str = str(default) if default is not None else ""
    clean_kwargs = {
        k: v for k, v in kwargs.items() if k not in ["validate", "validator"]
    }
    return LazyQuestion(
        questionary.text,
        message,
        default=default_str,
        validate=validator,
        **clean_kwargs,
    )


def integer(
    message: str,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    **kwargs: Any,
) -> "LazyQuestion | Question":
    return number(
        message, min_value=min_value, max_value=max_value, allow_float=False, **kwargs
    )


def form(questions: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
    # questionary.prompt returns a dict of answers
    return questionary.prompt(questions, **kwargs)


class ProgressTracker:
    """Simple progress tracker for multi-step operations."""

    def __init__(
        self, title: str, total: Optional[int] = None, total_steps: Optional[int] = None
    ) -> None:
        self.title: str = title
        self.total_steps: Optional[int] = total if total is not None else total_steps
        self.current_step: int = 0
        self.completed_steps: List[str] = []

    def __enter__(self) -> "ProgressTracker":
        print(f"🚀 Starting: {self.title}")
        print(f"   Total steps: {self.total_steps}")
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if exc_type is None:
            print("✅ Completed successfully!")
        else:
            print(f"❌ Failed: {exc_val}")

    def step(self, description: str) -> None:
        self.current_step += 1
        # Guard against division by None
        total = self.total_steps or 1
        progress = (self.current_step / total) * 100
        bar_length = 20
        filled_length = int(bar_length * self.current_step // total)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)

        print(
            f"   [{bar}] {self.current_step}/{total} ({progress:.1f}%) - {description}"
        )
        self.completed_steps.append(description)

    def update(self, step: int, description: str) -> None:
        self.current_step = step
        total = self.total_steps or 1
        progress = (self.current_step / total) * 100
        bar_length = 20
        filled_length = int(bar_length * self.current_step // total)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)

        print(
            f"   [{bar}] {self.current_step}/{total} ({progress:.1f}%) - {description}"
        )
        if description not in self.completed_steps:
            self.completed_steps.append(description)

    def complete(self, message: str = "All steps completed!") -> None:
        print(f"🎉 {message}")


# Expose class name following Python conventions


def confirm_enhanced(
    message: str, default: bool = True, **kwargs: Any
) -> "LazyQuestion | Question":
    """Enhanced confirmation prompt."""
    return LazyQuestion(questionary.confirm, message, default=default, **kwargs)


def select_enhanced(
    message: str, choices: List[Any], **kwargs: Any
) -> "LazyQuestion | Question":
    """Enhanced selection prompt."""
    return LazyQuestion(questionary.select, message, choices=choices, **kwargs)


def checkbox_enhanced(
    message: str, choices: List[Any], **kwargs: Any
) -> "LazyQuestion | Question":
    """Enhanced checkbox prompt."""
    return LazyQuestion(questionary.checkbox, message, choices=choices, **kwargs)
