"""DI-driven test verifying that PTKAdapter applies focus into a real app
using dependency injection only (no monkeypatching)."""
from tui_engine.container import ContainerElement
from tui_engine.ptk_adapter import PTKAdapter, ApplicationWrapper
from tui_engine.container import Element


class FakeLayout:
    def __init__(self):
        self.focus_called_with = None

    def focus(self, widget):
        self.focus_called_with = widget


class FakeApp:
    def __init__(self):
        self.layout = FakeLayout()


def test_apply_focus_to_ptk_via_injection():
    # Build domain tree with one focusable element
    root = ContainerElement('root')
    c = root.child('body')
    btn = c.button('ok')

    # Create adapter with an ApplicationWrapper that has a fake real app injected
    fake_app = FakeApp()
    wrapper = ApplicationWrapper(app=fake_app)
    # Use DI helper to set the real app instead of touching private attributes
    wrapper.set_real_app(fake_app)

    adapter = PTKAdapter(root, None, None, app=wrapper)

    # Map element path -> fake widget (the widget can be any object)
    fake_widget = object()
    adapter.register_widget_mapping(btn.path, fake_widget)

    # Register the element in the focus registry and set focus to it
    adapter.focus_registry.register(btn)
    adapter.focus_registry.set_focused(btn.path)

    # Now call the private method that applies focus into the PTK app
    adapter._apply_focus_to_ptk()

    # Assert that the fake app's layout.focus was called with our fake_widget
    assert fake_app.layout.focus_called_with is fake_widget
