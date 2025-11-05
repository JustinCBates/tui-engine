import tui_engine.factories as widgets
from tui_engine.container import Container
from tui_engine.ptk_widget_factory import map_element_to_widget


def test_button_on_click_descriptor_present() -> None:
    root = Container('root')
    called = {}

    def handler() -> None:
        called['ok'] = True

    btn = widgets.button('ok', on_click=handler)
    root.add(btn)
    desc = map_element_to_widget(btn)
    assert desc['type'] == 'button'
    assert 'on_click' in desc
    assert desc['on_click'] is handler
