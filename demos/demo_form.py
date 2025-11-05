"""Compatibly-named form demo: renamed from form_demo.py.

This is the same demo that writes `demos/form_output.json`. Kept logic and
imports but placed under the new module name expected by the main menu.
"""
import json
import sys
from pathlib import Path
from typing import Any, Dict

import tui_engine.factories as widgets
from tui_engine.container import Container, Element
from tui_engine.page import Page
from tui_engine.ptk_adapter import ApplicationWrapper, PTKAdapter


def _collect_values(root: Container) -> Dict[str, Any]:
    out = {}

    def walk(node: Any) -> None:
        if hasattr(node, "children"):
            for c in getattr(node, "children", []):
                walk(c)
        else:
            # Only include non-container elements
            try:
                val = node.get_value()
            except Exception:
                val = getattr(node, '_value', None)
            out[node.path] = val

    walk(root)
    return out


def run_demo() -> None:
    p = Page(title="Form demo")
    form = p.container("user_form")

    # Inputs with defaults
    name = widgets.input("name", value="Alice", enter_moves_focus=True)
    form.add(name)
    email = widgets.input("email", value="alice@example.com", enter_moves_focus=True)
    form.add(email)
    age = widgets.input("age", value="30", enter_moves_focus=True)
    form.add(age)

    # Instructions shown to the user (also rendered in the PTK UI)
    INSTRUCTIONS = (
        "Navigation: Tab / Shift+Tab to move between fields.\n"
        "Enter to accept / activate a button. Space to toggle checkboxes.\n"
        "Arrow keys to move in lists. Ctrl-C to cancel/quit.\n"
        "When running non-interactively the demo will fall back to console prompts."
    )
    # Add a non-editable text block to the form so the instructions are visible
    # inside the full-screen UI.
    try:
        form.add(widgets.text("instructions", INSTRUCTIONS))
    except Exception:
        pass

    # A checkbox_list style element (multi-select). We construct a raw
    # Element and attach options via metadata; adapters/factory will honor it.
    # Start without assigning a typed value to avoid static type warnings
    topics = Element("topics", variant="checkbox_list", focusable=True, value=None)
    topics.metadata['options'] = [("py", "Python"), ("ptk", "Prompt Toolkit"), ("ui", "TUI Engine")]
    form.add(topics)

    submit = widgets.button("Submit")
    form.add(submit)
    cancel = widgets.button("Cancel")
    form.add(cancel)

    output_path = Path(__file__).parent / "form_output.json"

    # Simple validation helper
    def validate_and_save() -> bool:
        vals = _collect_values(p.root)
        # very small validations
        if not vals.get('root.user_form.name'):
            print("Name is required")
            return False
        em = vals.get('root.user_form.email', "") or ""
        if "@" not in em:
            print("Email must contain @")
            return False
        # age must be integer
        try:
            int(vals.get('root.user_form.age', "0") or 0)
        except Exception:
            print("Age must be an integer")
            return False

        # Convert sets to lists for JSON
        for k, v in list(vals.items()):
            if isinstance(v, set):
                vals[k] = list(v)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(vals, f, indent=2)
        print(f"Saved form values to {output_path}")
        return True

    # Handlers for button clicks — in PTK mode these will be wired into the
    # runtime by the factory and adapters. The adapter variable will be bound
    # after creation; closures will read it at runtime.
    adapter = None

    def _on_submit() -> None:
        ok = validate_and_save()
        if ok:
            try:
                if adapter is not None:
                    adapter.app.stop()
            except Exception:
                pass

    def _on_cancel() -> None:
        print("Cancelled")
        try:
            if adapter is not None:
                adapter.app.stop()
        except Exception:
            pass

    # Attach handlers to elements
    try:
        submit.on_click = _on_submit
    except Exception:
        submit.metadata['on_click'] = _on_submit

    try:
        cancel.on_click = _on_cancel
    except Exception:
        cancel.metadata['on_click'] = _on_cancel

    # Attempt to run using prompt-toolkit via PTKAdapter; fall back to console
    adapter = PTKAdapter(p.root, p.page_state, p.events, app=ApplicationWrapper())
    root_container = adapter.build_real_layout(p.root)

    if root_container is None:
        # We assume prompt-toolkit and a TTY are always available in this
        # project. Fail fast to make issues obvious instead of falling back
        # to a non-interactive console UI.
        print("Error: prompt-toolkit layout could not be built. This demo requires prompt-toolkit and a TTY.", file=sys.stderr)
        sys.exit(1)

    # Launch the interactive PTK form — the environment is expected to be
    # a Linux terminal with prompt-toolkit installed.
    print("Launching interactive PTK form — use Tab to move focus, Enter to accept.")
    print(INSTRUCTIONS)
    # Debug helper removed for linting; use a debugger if you need to break here.
    adapter.app.run()


if __name__ == "__main__":
    run_demo()
