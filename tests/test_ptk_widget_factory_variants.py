from tui_engine.container import Container
from tui_engine.ptk_widget_factory import map_element_to_widget


def make_options() -> list[tuple[str, str]]:
    return [
        ("a", "Alpha"),
        ("b", "Bravo"),
        ("c", "Charlie"),
    ]


def test_select_descriptor_contains_options_and_selected() -> None:
    root = Container('root')
    _el = root.child('sel')
    # make a leaf element to carry variant
    leaf = Container('leaf')
    # attach metadata for options
    leaf.variant = 'select'
    leaf.metadata['options'] = make_options()
    # use attribute assignment similar to Element to simulate value
    leaf._value = 'b'
    desc = map_element_to_widget(leaf)
    assert desc['type'] == 'select'
    assert 'options' in desc and len(desc['options']) == 3
    assert desc['selected'] == 'b'


def test_radio_descriptor_normalized() -> None:
    leaf = Container('r')
    leaf.variant = 'radio'
    leaf.metadata['options'] = ['x', 'y']
    desc = map_element_to_widget(leaf)
    assert desc['type'] == 'radio'
    assert desc['options'][0][0] == 'x'


def test_checkbox_list_selected_as_set() -> None:
    leaf = Container('cb')
    leaf.variant = 'checkbox_list'
    leaf.metadata['options'] = ['one', 'two']
    leaf._value = ['one']
    desc = map_element_to_widget(leaf)
    assert desc['type'] == 'checkbox_list'
    assert isinstance(desc['selected'], set)
    assert 'one' in desc['selected']
