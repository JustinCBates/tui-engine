import importlib.util
import sys
from pathlib import Path


def _load_bridge_module():
    # Import via package so relative imports work and coverage attributes file
    import importlib

    mod = importlib.import_module("questionary_extended.integration.questionary_bridge")
    importlib.reload(mod)
    return mod


def test_direct_load_and_walk_components():
    mod = _load_bridge_module()

    # Use real Component/Card/Assembly classes so isinstance checks match
    from questionary_extended.core.component import Component
    from questionary_extended.core.card import Card
    from questionary_extended.core.assembly import Assembly

    inner_comp = Component("ic", "text")
    inner_asm = Assembly("inner", parent=None)
    inner_asm.components.append(inner_comp)
    card = Card("CardTitle", parent=None)
    card.components.append(Component("c1", "text"))
    card.components.append(inner_asm)

    from questionary_extended.core.state import PageState

    bridge = mod.QuestionaryBridge(state=PageState())

    # Use the bridge instance's _walk_components to enumerate components
    found = list(bridge._walk_components([card]))
    names = {getattr(c, "name", None) for c in found}
    assert "c1" in names and "ic" in names
