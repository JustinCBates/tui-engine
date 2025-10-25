from questionary_extended import ProgressTracker


def test_progress_tracker_export_and_instance():
    # Ensure the class is importable from the package
    assert ProgressTracker is not None

    # Instances should be instances of the exported class
    with ProgressTracker("test", total_steps=1) as p:
        assert isinstance(p, ProgressTracker)
from questionary_extended.prompts_core import ProgressTracker as CoreProgressTracker


def test_progress_tracker_alias_and_behavior():
    # Create instance and basic behavior using the canonical class
    p1 = CoreProgressTracker("Test", total_steps=3)
    assert isinstance(p1, ProgressTracker)

    # Basic usage: stepping should increase current_step
    assert p1.current_step == 0
    p1.step("step1")
    assert p1.current_step == 1

    # update sets step directly
    p1.update(3, "final")
    assert p1.current_step == 3

    # complete doesn't raise
    p1.complete("done")
