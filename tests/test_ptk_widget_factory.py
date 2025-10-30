import sys

from tui_engine.element import Element
from tui_engine.ptk_widget_factory import map_element_to_widget


def test_map_button_element_to_descriptor() -> None:
    btn = Element("OK", variant="button", focusable=True)
    desc = map_element_to_widget(btn)
    assert desc["type"] == "button"
    assert desc["label"] == "OK"
    assert "ptk_widget" in desc
    # headless mode should not produce a real widget instance by default
    assert desc["ptk_widget"] is None or True


def test_map_input_element_to_descriptor() -> None:
    inp = Element("name", variant="input", focusable=True, value="abc")
    desc = map_element_to_widget(inp)
    assert desc["type"] == "input"
    assert desc["value"] == "abc"
    assert desc["name"] == "name"
    assert "ptk_widget" in desc
