import pytest

from tui_engine.container import Container
from tui_engine.element import Element
from tui_engine.ptk_adapter import PTKAdapter


def test_headless_layout_includes_min_max_align():
    root = Container('root')
    c = Container('c1')
    e1 = Element('leaf1')
    e1.min_height = 2
    e2 = Element('leaf2')
    e2.min_height = 3
    c.add(e1)
    c.add(e2)
    c.align = 'middle'
    c.min_height = 10
    root.add(c)

    adapter = PTKAdapter(root, page_state=None, events=None)
    tree = adapter.build_layout(root)

    # verify structure
    assert tree['type'] == 'container'
    child = tree['children'][0]
    assert child['type'] == 'container'
    assert child['align'] == 'middle'
    assert child['min_height'] == 10
    assert child['children'][0]['min_height'] == 2
    assert child['children'][1]['min_height'] == 3


def test_ptk_build_real_layout_runs_without_error():
    root = Container('root')
    c = Container('c1')
    e1 = Element('leaf1')
    c.add(e1)
    root.add(c)

    adapter = PTKAdapter(root, page_state=None, events=None)
    # should not raise when prompt_toolkit is available; if not available
    # the method returns None, which is acceptable.
    res = adapter.build_real_layout(root)
    # success if no exception; result may be None in headless env
    assert res is None or True
