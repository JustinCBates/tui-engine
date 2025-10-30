Demo environment and run instructions
=================================

This folder contains interactive demo scripts that exercise the `tui-engine` package.
To make the demos easy to run for end-consumers we provide a small helper that
creates a Python virtual environment and installs the package and its runtime
dependencies.

Quick start
-----------

1. Create a demo virtual environment and install runtime dependencies:

```bash
cd demos
./setup_env.sh
```

2. Activate the virtual environment in your shell:

```bash
source .venv/bin/activate
```

3. Run an interactive demo (these require a real terminal / TTY):

```bash
python ../demos/demo_form.py
```

Notes
-----

- The `setup_env.sh` script creates a venv at `demos/.venv` by default and installs
  the package in editable mode (`pip install -e .`) so you can iterate on the
  code while using the demos.
- If you want development extras (linters, test deps, etc) run:

```bash
./setup_env.sh --dev
```

- If you prefer a different location for the virtual environment:

```bash
./setup_env.sh --venv ../.env
source ../.env/bin/activate
```

- To force recreation of the venv (useful to recover from a broken venv):

```bash
./setup_env.sh --recreate
```

TTY and prompt-toolkit
----------------------

Many of the demos use `prompt-toolkit` and expect to run in an interactive terminal.
If you run them in an environment without a real TTY (for example, some CI systems
or inside certain editors' limited consoles) the demo may fail. Use a normal terminal
or run inside a compatible emulator (e.g. GNOME Terminal, xterm, Alacritty, iTerm2,
or Windows WSL/PowerShell when appropriate).

When things go wrong
--------------------

- Make sure you have Python 3.8+ available as `python3` on PATH.
- If `setup_env.sh` fails, try removing the venv and re-running with `--recreate`.
- If you need to run tests or linters, use `./setup_env.sh --dev` and then run
  your tools from the activated venv (e.g. `pytest`, `ruff`, `mypy`).

More
----

See the project `pyproject.toml` for declared runtime dependencies and "optional"
extras. The demos are lightweight and should work once `prompt-toolkit` and the
dependencies listed in `pyproject.toml` are installed into the venv.
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
