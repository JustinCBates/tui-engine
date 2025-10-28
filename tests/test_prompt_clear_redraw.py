import time

from src.questionary_extended.core.page_base import PageBase
from src.questionary_extended.core.component_wrappers import set_last_prompt_clear_ts
from src.questionary_extended.core.component_wrappers import get_prompt_clear_events


class FakeBufferManager:
    def __init__(self):
        self.applied = None

    def allocate_space(self, name, space_req):
        return {'name': name}

    def reallocate_space(self, name, space_req):
        return {'name': name}

    def apply_buffer_delta(self, page_position, delta):
        # Record the delta applied
        self.applied = delta


def test_spatial_refresh_forces_redraw_on_prompt_clear():
    # Create a page with spatial layout and a body section containing a text
    page = PageBase("Test Page", use_spatial_layout=True)

    # Add a visible line in the body so page has content
    body = page.body_section()
    # Create an interactive component and attach it to the body
    from src.questionary_extended.core.component_wrappers import Component
    comp = Component('test_input', 'text', message='Enter:')
    body.add_element(comp)

    # Simulate all sections and children being clean (so calculate_buffer_changes would be empty)
    for sec in page._sections.values():
        sec._content_dirty = False
        for elem in sec.get_elements().values():
            if hasattr(elem, '_needs_render'):
                elem._needs_render = False

    # Attach a fake buffer manager to capture apply_buffer_delta calls
    fake_mgr = FakeBufferManager()
    page._buffer_manager = fake_mgr

    # Ensure no page_position exists so allocation path is executed
    if hasattr(page, '_page_position'):
        delattr(page, '_page_position')

    # Simulate a prompt clear having occurred and then trigger the component's
    # interactive prompt lifecycle which should propagate the event to the page.
    # Inject a fake questionary that simulates prompt-toolkit writing clear
    # sequences while the prompt is active. Activate the component so the
    # proxy can attribute the clear to this component's owning page.
    import sys, types
    fake_mod = types.SimpleNamespace()
    class FakePrompt:
        def __init__(self, kind, message, default=None, choices=None):
            self.kind = kind
            self.message = message
            self.default = default
            self.choices = choices
        def ask(self):
            import sys
            # emit alternate-screen + clear + cursor home
            sys.stdout.write('\x1b[?1049h')
            sys.stdout.write('\x1b[2J')
            sys.stdout.write('\x1b[H')
            sys.stdout.flush()
            return 'fake-answer' if self.kind != 'confirm' else True

    fake_mod.text = lambda message=None, default=None, **kwargs: FakePrompt('text', message or 'text', default=default)
    fake_mod.password = lambda message=None, **kwargs: FakePrompt('password', message or 'password')
    fake_mod.confirm = lambda message=None, default=None, **kwargs: FakePrompt('confirm', message or 'confirm', default=default)
    fake_mod.select = lambda message=None, choices=None, default=None, **kwargs: FakePrompt('select', message or 'select', default=default, choices=choices)

    saved = sys.modules.get('questionary')
    sys.modules['questionary'] = fake_mod
    try:
        comp.activate_for_input(0)
        comp.render_interactive_prompt()
        comp.deactivate()
    finally:
        if saved is not None:
            sys.modules['questionary'] = saved
        else:
            del sys.modules['questionary']

    # Now the page should have recorded the prompt clear handled timestamp
    assert getattr(page, '_last_prompt_clear_handled_ts', 0.0) > 0.0

    # Call spatial refresh - it should detect the prompt clear and force a redraw
    page._buffer_manager = fake_mgr
    try:
        delattr(page, '_page_position')
    except Exception:
        pass
    page._spatial_refresh()

    assert fake_mgr.applied is not None, "apply_buffer_delta should be called when prompt clear detected"
    assert hasattr(fake_mgr.applied, 'line_updates') and len(fake_mgr.applied.line_updates) > 0
