TUI Engine demos
================

Recommended invocation (from the repository root):

```bash
python -m demos.main_menu
```

This will run the interactive main menu that lets you pick and run demos.

Requirements and behaviour
- The demos assume `prompt-toolkit` is installed in the environment.
- The demos require a real TTY (Linux terminal). They will fail fast if a
    prompt-toolkit full-screen layout cannot be constructed.

Convenience: you can also run the script directly from the `demos/` directory
with `python ./main_menu.py`. The `main_menu.py` script contains a small
helper that inserts the project root into `sys.path` so imports still work
when running from inside `demos/` — this is intentionally kept for
developer convenience.

Files
- `main_menu.py` - demo selector and runner
- `demo_form.py` - form demo (interactive, writes `form_output.json`)
- `demo_container.py` - simple container render demo
- `container_demo.py` - backward-compatible delegating wrapper
First working prototype example

This folder contains a minimal, non-interactive prototype demonstrating how
to assemble a Page, Assembly, and Components and write namespaced state into
the PageState object. The script `first_working_prototype.py` is safe to run in
CI because it simulates answers instead of requiring interactive input.

Run:

    python .\examples\first_working_prototype.py

This exercise demonstrates Task 12 (First Working Prototype) in the project's
todo list.
