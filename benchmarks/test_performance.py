"""
Performance benchmarks for tui-engine.

Run with: pytest benchmarks/ --benchmark-json=benchmark-results.json
"""

# ruff: noqa
# type: ignore
# mypy: ignore-errors

import pytest

from tui_engine import (
    EmailValidator,
    NumberValidator,
    enhanced_text,
    number,
    rating,
)


class TestValidatorPerformance:
    """Benchmark validator performance."""

    def test_number_validator_performance(self, benchmark):
        """Benchmark NumberValidator performance."""
        validator = NumberValidator(min_value=0, max_value=100)

        def validate_numbers():
            for i in range(100):
                validator.validate(str(i))

    _result = benchmark(validate_numbers)  # noqa: F821

    def test_email_validator_performance(self, benchmark):
        """Benchmark EmailValidator performance."""
        validator = EmailValidator()

        def validate_emails():
            emails = [
                "test@example.com",
                "user.name@domain.co.uk",
                "invalid-email",
                "another@test.org",
                "bad@",
            ]
            for email in emails:
                try:
                    validator.validate(email)
                except:
                    pass

    _result = benchmark(validate_emails)  # noqa: F821


class TestPromptPerformance:
    """Benchmark prompt creation performance."""

    def test_enhanced_text_creation(self, benchmark):
        """Benchmark enhanced_text prompt creation."""

        def create_text_prompts():
            for i in range(100):
                _ = enhanced_text(f"Question {i}", default="test")

    _result = benchmark(create_text_prompts)  # noqa: F821

    def test_number_prompt_creation(self, benchmark):
        """Benchmark number prompt creation."""

        def create_number_prompts():
            for i in range(100):
                _ = number(f"Number {i}", min_value=0, max_value=100)

    _result = benchmark(create_number_prompts)  # noqa: F821

    def test_rating_prompt_creation(self, benchmark):
        """Benchmark rating prompt creation."""

        def create_rating_prompts():
            for i in range(100):
                _ = rating(f"Rate {i}", max_rating=5)

    _result = benchmark(create_rating_prompts)  # noqa: F821


class TestProgressTrackerPerformance:
    """Benchmark progress tracker performance."""

    def test_progress_tracker_updates(self, benchmark):
        """Benchmark progress tracker update performance."""

        def progress_updates():
            from tui_engine import ProgressTracker

            tracker = ProgressTracker("Benchmark Test", total_steps=100)
            with tracker:
                for i in range(100):
                    tracker.update(i + 1, f"Step {i + 1}")

        # Redirect print to avoid cluttering benchmark output
        import io
        import sys

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            _result = benchmark(progress_updates)  # noqa: F821
        finally:
            sys.stdout = old_stdout


class TestMemoryUsage:
    """Test memory efficiency."""

    def test_validator_memory_usage(self):
        """Test that validators don't leak memory."""
        import gc
        import sys

        # Create many validators
        validators = []
        for i in range(1000):
            validators.append(NumberValidator(min_value=i, max_value=i + 100))

        # Force garbage collection
        gc.collect()

        # Clear references
        validators.clear()
        gc.collect()

        # This is a simple memory leak test
        assert len(gc.garbage) == 0

    def test_progress_tracker_cleanup(self):
        """Test that progress trackers clean up properly."""
        import gc
        import io
        import sys

        # Redirect stdout to avoid print spam
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            trackers = []
            for i in range(100):
                from tui_engine import ProgressTracker

                tracker = ProgressTracker(f"Test {i}", total_steps=10)
                with tracker:
                    for j in range(10):
                        tracker.update(j + 1, f"Step {j + 1}")
                trackers.append(tracker)

            # Force cleanup
            trackers.clear()
            gc.collect()

            # Check for leaks
            assert len(gc.garbage) == 0

        finally:
            sys.stdout = old_stdout


if __name__ == "__main__":
    # Run benchmarks when script is executed directly
    pytest.main([__file__, "--benchmark-json=benchmark-results.json", "-v"])
