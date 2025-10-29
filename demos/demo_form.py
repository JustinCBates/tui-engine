"""Compatibly-named form demo: renamed from form_demo.py.

This is the same demo that writes `demos/form_output.json`. Kept logic and
imports but placed under the new module name expected by the main menu.
"""
import json
from pathlib import Path
from typing import Any

from tui_engine.page import Page
from tui_engine.container import ContainerElement, Element
from tui_engine.ptk_adapter import PTKAdapter, ApplicationWrapper


def _collect_values(root: ContainerElement) -> dict:
    out = {}

    def walk(node):
        if hasattr(node, 'children'):
            for c in getattr(node, 'children', []):
                walk(c)
        else:
            # Only include non-container elements
            try:
                val = getattr(node, 'get_value')()
            except Exception:
                val = getattr(node, '_value', None)
            out[node.path] = val

    walk(root)
    return out


def run_demo():
    p = Page(title="Form demo")
    form = p.container("user_form")

    # Inputs with defaults
    name = form.input("name", value="Alice")
    email = form.input("email", value="alice@example.com")
    age = form.input("age", value="30")

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
        form.text("instructions", INSTRUCTIONS)
    except Exception:
        # If the form API doesn't expose `text()` in some runtime, we still
        # ensure instructions are printed in the console fallback below.
        pass

    # A checkbox_list style element (multi-select). We construct a raw
    # Element and attach options via metadata; adapters/factory will honor it.
    topics = Element("topics", variant="checkbox_list", focusable=True, value=set())
    topics.metadata['options'] = [("py", "Python"), ("ptk", "Prompt Toolkit"), ("ui", "TUI Engine")]
    form.add(topics)

    submit = form.button("Submit")
    cancel = form.button("Cancel")

    output_path = Path(__file__).parent / "form_output.json"

    # Simple validation helper
    def validate_and_save():
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

    def _on_submit():
        ok = validate_and_save()
        if ok:
            try:
                if adapter is not None:
                    adapter.app.stop()
            except Exception:
                pass

    def _on_cancel():
        print("Cancelled")
        try:
            if adapter is not None:
                adapter.app.stop()
        except Exception:
            pass

    # Attach handlers to elements
    try:
        setattr(submit, 'on_click', _on_submit)
    except Exception:
        submit.metadata['on_click'] = _on_submit

    try:
        setattr(cancel, 'on_click', _on_cancel)
    except Exception:
        cancel.metadata['on_click'] = _on_cancel

    # Attempt to run using prompt-toolkit via PTKAdapter; fall back to console
    adapter = PTKAdapter(p.root, p.page_state, p.events, app=ApplicationWrapper())
    root_container = adapter.build_real_layout(p.root)

    if root_container is not None:
        print("Launching interactive PTK form — use Tab to move focus, Enter to accept.")
        print(INSTRUCTIONS)
        try:
            adapter.app.run()
        except Exception:
            pass
    else:
        # headless interactive fallback
        print("Prompt-toolkit not available — falling back to console prompts.")
        print(INSTRUCTIONS)
        # Simple sequential prompts with defaults and validation
        def prompt_input(elem: Element, label: str):
            cur = elem.get_value()
            while True:
                resp = input(f"{label} [{cur}]: ")
                if resp == "":
                    resp = cur
                elem.set_value(resp)
                return

        prompt_input(name, "Name")
        prompt_input(email, "Email")
        prompt_input(age, "Age")

        # topics multi-select simple console interface
        opts = topics.metadata.get('options', [])
        print("Select topics (comma-separated indexes):")
        for i, (_, lbl) in enumerate(opts, start=1):
            print(f"  {i}. {lbl}")
        sel = input("Selected (e.g. 1,3) []: ")
        chosen = set()
        if sel.strip():
            for part in sel.split(','):
                try:
                    idx = int(part.strip()) - 1
                    if 0 <= idx < len(opts):
                        chosen.add(opts[idx][0])
                except Exception:
                    pass
        topics.set_selected_values(chosen) if hasattr(topics, 'set_selected_values') else topics.set_value(chosen)

        # Final validation and save
        if validate_and_save():
            print(f"Saved: {output_path}")


if __name__ == "__main__":
    run_demo()
