from tui_engine.container import ContainerElement
from tui_engine.ptk_widget_factory import map_element_to_widget


def test_button_on_click_descriptor_present():
    root = ContainerElement('root')
    called = {}

    def handler():
        called['ok'] = True

    btn = root.button('ok', on_click=handler)
    desc = map_element_to_widget(btn)
    assert desc['type'] == 'button'
    assert 'on_click' in desc
    assert desc['on_click'] is handler
