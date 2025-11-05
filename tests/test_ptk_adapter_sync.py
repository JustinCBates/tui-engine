from typing import Optional

import tui_engine.factories as widgets
from tui_engine.container import Container
from tui_engine.ptk_adapter import PTKAdapter
from tui_engine.ptk_widget_factory import map_element_to_widget


class FakeWidget:
    def __init__(self, current_value: Optional[str] = None) -> None:
        self.current_value: Optional[str] = current_value
        # allow assigning a string path later in tests
        self._tui_path: Optional[str] = None
        self._tui_focusable = True

    def _tui_sync(self) -> Optional[str]:
        # simulate that sync uses current_value
        return getattr(self, "current_value", None)


def test_adapter_calls_tui_sync_and_updates_element() -> None:
    root = Container('root')
    leaf = widgets.text('leaf', value='orig')
    root.add(leaf)
    # create a fake widget via factory descriptor
    desc = map_element_to_widget(leaf)
    # replace ptk_widget with our fake that exposes current_value
    fake = FakeWidget(current_value='newval')
    try:
        fake._tui_path = leaf.path
    except Exception:
        # Some fake widget shapes may not allow arbitrary attributes; ignore
        pass
    desc['ptk_widget'] = fake

    # Create adapter and register mapping as build_real_layout would
    adapter = PTKAdapter(root, None, None)
    adapter.register_widget_mapping(leaf.path, fake)
    # manually register sync mapping
    adapter._path_to_sync[leaf.path] = fake._tui_sync

    # ensure initial value unchanged
    assert leaf.get_value() == 'orig'

    # call adapter sync for focused widget (simulate focused)
    adapter.focus_registry.register(leaf)
    adapter.focus_registry.set_focused(leaf.path)
    adapter._sync_focused_widget()

    # after sync, element should have updated value
    assert leaf.get_value() == 'newval'
