"""Interactive demo main menu.

Provides a simple numeric console menu to pick and run demos found in the
`demos` package (non-blocking and safe). Each demo module exposes a `run_demo()`
callable which will be imported and executed.
"""
import importlib
import sys
from pathlib import Path
from typing import Optional


def _ensure_demos_package() -> None:
    """Ensure the repo root (parent of this demos/ folder) is on sys.path.

    This makes `importlib.import_module('demos.x')` work even when the user
    runs the script with the current working directory set to `demos/`.
    """
    pkg = "demos"
    # Fast-path: already importable
    try:
        importlib.import_module(pkg)
        return
    except Exception:
        pass

    # Insert the parent of the demos package (project root) to sys.path so
    # Python can find `demos` as a top-level package when running from
    # inside the demos directory. Also add the common `src/` layout if present
    # so packages under `src/` (like `tui_engine`) are importable.
    repo_root = Path(__file__).resolve().parent.parent
    repo_root_str = str(repo_root)
    src_dir = repo_root / "src"
    src_dir_str = str(src_dir)

    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
    if src_dir.exists() and src_dir_str not in sys.path:
        sys.path.insert(0, src_dir_str)

DEMOS = [
    ("demo_form", "Form demo: fill a form that saves JSON"),
    ("demo_container", "Container demo: simple container render"),
]


def show_menu() -> None:
    print("TUI Engine - Demos")
    print("===================")
    for i, (name, desc) in enumerate(DEMOS, start=1):
        print(f"{i}. {desc} ({name})")
    print("0. Quit")


def choose_demo() -> Optional[str]:
    while True:
        try:
            choice = input("Choose demo number: ")
            if not choice:
                continue
            idx = int(choice)
            if idx == 0:
                print("Goodbye")
                return None
            if 1 <= idx <= len(DEMOS):
                return DEMOS[idx - 1][0]
            print("Invalid choice")
        except ValueError:
            print("Please enter a number")


def run() -> None:
    _ensure_demos_package()
    show_menu()
    sel = choose_demo()
    if sel is None:
        return

    # Import module from demos.<name> and call run_demo()
    mod_name = f"demos.{sel}"
    try:
        mod = importlib.import_module(mod_name)
    except Exception as e:
        print(f"Failed to import demo {mod_name}: {e}")
        return

    runner = getattr(mod, "run_demo", None)
    if runner is None or not callable(runner):
        print(f"Demo {mod_name} has no run_demo() entrypoint")
        return

    try:
        runner()
    except Exception as e:
        print(f"Demo {mod_name} failed: {e}")


if __name__ == "__main__":
    run()
