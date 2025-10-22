#!/usr/bin/env python3
"""First working prototype example for questionary-extended.

This script builds a minimal Page with an Assembly and two Components,
simulates answers (non-interactive), runs a tiny simulated bridge that
writes namespaced keys into PageState, and prints the flat results.

Run from the repository root with:
    python .\\examples\first_working_prototype.py
"""

import os
import sys
from typing import Dict

# Ensure local src package is importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.normpath(os.path.join(ROOT, "src"))
if SRC not in sys.path:
    sys.path.insert(0, SRC)

# Import minimal core pieces directly
import importlib.util


# Load core modules directly from source files to avoid executing package
# level imports in questionary_extended.__init__ (which may reference
# optional utilities not present in this prototype environment).
def _load_module_from_path(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    # Register module in sys.modules so relative imports inside the
    # module resolve to this module object and class identities remain
    # consistent across modules.
    sys.modules[name] = module
    spec.loader.exec_module(module)  # type: ignore
    return module


CORE_DIR = os.path.join(SRC, "questionary_extended", "core")

import types

# Create minimal package structure in sys.modules so that relative imports like
# `from .state import PageState` inside core modules resolve correctly when we
# load the modules directly from files.
pkg_name = "questionary_extended"
core_pkg_name = f"{pkg_name}.core"
if pkg_name not in sys.modules:
    pkg = types.ModuleType(pkg_name)
    pkg.__path__ = [os.path.join(SRC, pkg_name)]
    sys.modules[pkg_name] = pkg

if core_pkg_name not in sys.modules:
    core_pkg = types.ModuleType(core_pkg_name)
    core_pkg.__path__ = [CORE_DIR]
    sys.modules[core_pkg_name] = core_pkg

# Load modules under the package-qualified names so their relative imports work
page_mod = _load_module_from_path(
    "questionary_extended.core.page", os.path.join(CORE_DIR, "page.py")
)
assembly_mod = _load_module_from_path(
    "questionary_extended.core.assembly", os.path.join(CORE_DIR, "assembly.py")
)
component_mod = _load_module_from_path(
    "questionary_extended.core.component", os.path.join(CORE_DIR, "component.py")
)
state_mod = _load_module_from_path(
    "questionary_extended.core.state", os.path.join(CORE_DIR, "state.py")
)

Page = page_mod.Page
Assembly = assembly_mod.Assembly
Component = component_mod.Component
text = component_mod.text
select = component_mod.select
PageState = state_mod.PageState


class SimulatedBridge:
    """Simple non-interactive bridge that writes provided answers into PageState

    This bridge will namespace answers belonging to an Assembly using
    the pattern: "{assembly_name}.{component_name}" and will set global
    component answers as-is.
    """

    def __init__(self, state: PageState, answers: Dict[str, object]):
        self.state = state
        self.answers = answers

    def run(self, root_items):
        # Walk top-level items (Page.components) and set answers.
        for item in root_items:
            # Assembly instances have a `.name` and `.components`
            if isinstance(item, Assembly):
                asm_name = item.name
                for c in getattr(item, "components", []):
                    if isinstance(c, Component):
                        ans = self.answers.get(c.name)
                        # Namespace the key into assembly.field
                        key = f"{asm_name}.{c.name}"
                        self.state.set(key, ans)
            else:
                # Fallback: if item itself is a Component
                if isinstance(item, Component):
                    ans = self.answers.get(item.name)
                    self.state.set(item.name, ans)


def main():
    page = Page("Prototype Demo")

    # Create an assembly (namespace: person)
    asm = page.assembly("person")

    # Create components using convenience wrappers and attach them
    name_comp = text("name", message="Full name:")
    color_comp = select(
        "favorite_color", message="Favorite color:", choices=["red", "green", "blue"]
    )

    # Append components to the assembly's components list (method-chaining not implemented yet)
    asm.components.append(name_comp)
    asm.components.append(color_comp)

    # Simulated answers (non-interactive)
    answers = {
        "name": "Alice Example",
        "favorite_color": "green",
    }
    # Debug: inspect assembly/components types and identities
    print("DEBUG: assembly type:", type(asm))
    print("DEBUG: assembly is Assembly?:", isinstance(asm, Assembly))
    print("DEBUG: assembly.components:", asm.components)
    print("DEBUG: name_comp type:", type(name_comp))
    print("DEBUG: name_comp is Component?:", isinstance(name_comp, Component))
    print("DEBUG: page.state is PageState?:", isinstance(page.state, PageState))
    print("DEBUG: answers dict:", answers)

    # Run the simulated bridge which writes namespaced keys into PageState
    bridge = SimulatedBridge(page.state, answers)
    bridge.run(page.components)

    # Print the flat state (assembly namespacing should be present)
    result = page.state.get_all_state()
    print("Collected flat state:")
    for k, v in result.items():
        print(f"  {k}: {v}")

    # Basic assertion for demo purposes
    expected = {"person.name": "Alice Example", "person.favorite_color": "green"}
    assert result == expected, f"Unexpected result: {result} != {expected}"
    print("\nPrototype run successful — state matches expected output.")


if __name__ == "__main__":
    main()
