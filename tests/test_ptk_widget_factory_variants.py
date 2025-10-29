from tui_engine.container import ContainerElement
from tui_engine.ptk_widget_factory import map_element_to_widget


def make_options():
    return [
        ("a", "Alpha"),
        ("b", "Bravo"),
        ("c", "Charlie"),
    ]


def test_select_descriptor_contains_options_and_selected():
    root = ContainerElement('root')
    el = root.child('sel')
    # make a leaf element to carry variant
    leaf = ContainerElement('leaf')
    # attach metadata for options
    leaf.variant = 'select'
    leaf.metadata['options'] = make_options()
    # use attribute assignment similar to Element to simulate value
    setattr(leaf, '_value', 'b')
    desc = map_element_to_widget(leaf)
    assert desc['type'] == 'select'
    assert 'options' in desc and len(desc['options']) == 3
    assert desc['selected'] == 'b'


def test_radio_descriptor_normalized():
    leaf = ContainerElement('r')
    leaf.variant = 'radio'
    leaf.metadata['options'] = ['x', 'y']
    desc = map_element_to_widget(leaf)
    assert desc['type'] == 'radio'
    assert desc['options'][0][0] == 'x'


def test_checkbox_list_selected_as_set():
    leaf = ContainerElement('cb')
    leaf.variant = 'checkbox_list'
    leaf.metadata['options'] = ['one', 'two']
    setattr(leaf, '_value', ['one'])
    desc = map_element_to_widget(leaf)
    assert desc['type'] == 'checkbox_list'
    assert isinstance(desc['selected'], set)
    assert 'one' in desc['selected']
