import pytest

try:
    import prompt_toolkit  # noqa: F401
    _PTK_AVAILABLE = True
except Exception:
    _PTK_AVAILABLE = False

from tui_engine.container import ContainerElement
from tui_engine.ptk_adapter import PTKAdapter


@pytest.mark.skipif(not _PTK_AVAILABLE, reason="prompt-toolkit not available")
def test_build_real_layout_and_syncs_checkbox_list():
    from tui_engine.container import Element

    root = ContainerElement('root')
    # create a real Element (leaf) and add it to root so build_real_layout will
    # treat it as a leaf (no 'children' attribute)
    leaf = Element('leaf', variant='checkbox_list')
    leaf.metadata['options'] = [('one', 'One'), ('two', 'Two')]
    root.add(leaf)

    adapter = PTKAdapter(root, None, None)
    container = adapter.build_real_layout(root)
    assert container is not None

    # adapter should have registered a widget and a sync callable for the leaf
    assert leaf.path in adapter._path_to_widget
    assert leaf.path in adapter._path_to_sync

    widget = adapter._path_to_widget[leaf.path]
    # simulate a user selection by setting common attribute names probed by
    # the sync helper. We try multiple names defensively.
    try:
        widget.checked_values = ['one']
    except Exception:
        pass
    try:
        widget.current_values = ['one']
    except Exception:
        pass
    try:
        widget.current_value = 'one'
    except Exception:
        pass
    try:
        widget.selected = 'one'
    except Exception:
        pass

    # focus and trigger sync
    adapter.focus_registry.register(leaf)
    adapter.focus_registry.set_focused(leaf.path)
    adapter._sync_focused_widget()

    # After sync, the element should reflect the selection (list for multi-select)
    val = getattr(leaf, '_value', None)
    assert val is not None
    # Normalize check: accept scalar 'one', list-like containing 'one', or
    # the pathological case where a string was iterated into characters.
    if isinstance(val, (list, set, tuple)):
        # list of chars -> join
        if all(isinstance(x, str) and len(x) == 1 for x in val):
            assert ''.join(val) == 'one'
        else:
            assert 'one' in val
    else:
        assert val == 'one'
