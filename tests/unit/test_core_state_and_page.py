from pathlib import Path
from tests.helpers.test_helpers import load_module_from_path

# load core modules via helper so package and relative imports resolve correctly
state_mod = load_module_from_path(
    "questionary_extended.core.state",
    Path("src/questionary_extended/core/state.py").resolve(),
)

page_mod = load_module_from_path(
    "questionary_extended.core.page",
    Path("src/questionary_extended/core/page.py").resolve(),
)


def test_pagestate_namespace_and_clear():
    ps = state_mod.PageState()
    ps.set("x", 1)
    assert ps.get("x") == 1
    ps.set("asm.f", 2)
    assert ps.get("asm.f") == 2
    assert ps.get_assembly_state("asm")["f"] == 2
    allstate = ps.get_all_state()
    assert "asm.f" in allstate and allstate["x"] == 1
    assert ps.has_key("x")
    assert ps.has_key("asm.f")
    ps.clear_assembly("asm")
    assert not ps.has_key("asm.f")
    ps.clear_all()
    assert not ps.has_key("x")


def test_page_card_and_assembly_creation():
    pg = page_mod.Page("T")
    card = pg.card("C")
    assert card.title == "C"
    assert card in pg.components
    assembly = pg.assembly("A")
    assert assembly in pg.components
    # Card hide/show
    card.hide()
    assert card.visible is False
    card.show()
    assert card.visible is True
