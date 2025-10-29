from tui_engine.container import ContainerElement
from tui_engine.ptk_widget_factory import map_element_to_widget


def test_checkbox_list_descriptor_and_real_widget_when_available():
    leaf = ContainerElement('multi')
    leaf.variant = 'checkbox_list'
    leaf.metadata['options'] = [('one', 'One'), ('two', 'Two'), ('three', 'Three')]
    setattr(leaf, '_value', ['two', 'three'])

    desc = map_element_to_widget(leaf)
    assert desc['type'] == 'checkbox_list'
    assert 'options' in desc and len(desc['options']) == 3
    assert isinstance(desc['selected'], set)
    assert 'two' in desc['selected']

    # If prompt-toolkit is installed and a real widget was constructed, it
    # should be tagged with the element path and be focusable. Otherwise
    # the mapping still must be deterministic for headless tests.
    widget = desc.get('ptk_widget')
    if widget is not None:
        assert getattr(widget, '_tui_path', None) == getattr(leaf, 'path', None)
        assert getattr(widget, '_tui_focusable', True) is True
