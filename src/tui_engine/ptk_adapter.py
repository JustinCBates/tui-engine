"""PTKAdapter skeleton for Phase A/B.

This module provides a minimal ApplicationWrapper that will use prompt_toolkit
if available, but falls back to a headless/dummy implementation for CI and
headless unit tests. The PTKAdapter.build_layout() currently returns a
lightweight layout summary (a nested dict) that describes the domain tree.
Phase B will extend build_layout to produce prompt-toolkit containers.
"""
import asyncio
from typing import Any, Callable, Dict, List, Optional, Set

from tui_engine.focus import FocusRegistry
from tui_engine.ptk_widget_factory import map_element_to_widget


class ApplicationWrapper:
    """Small wrapper around prompt-toolkit Application; falls back to a dummy.

    API intentionally minimal: run(), stop(), invalidate(), create_background_task().
    """

    def __init__(self, app: Optional[Any] = None) -> None:
        # app may be a real prompt_toolkit Application or None
        self._app: Optional[Any] = app
        # background loop used when no running event loop is present
        self._bg_loop: Optional[Any] = None
        self._bg_thread: Optional[Any] = None
        # expose a public hook so tests can inject a real_app without touching
        # private attributes
        self._real_app: Optional[Any] = None
        # Visible/invalidated flag can be toggled by tests or consumers; define
        # it here to satisfy type-checkers and editor hovers that inspect
        # attributes on ApplicationWrapper instances.
        self.invalidated: bool = False
        # Optional storage for the last style mapping applied via adapter so
        # tests and consumers can inspect requested styles.
        self._last_style: Optional[Dict[str, str]] = None
        # Optional key_bindings and container references may be set later
        # by register_keybinding/register_application. Declare them here to
        # satisfy static analysis and editor hovers.
        self._key_bindings: Optional[Any] = None
        self._container: Optional[Any] = None

    def run(self, *args: Any, **kwargs: Any) -> Any:
        if self._app is not None:
            try:
                return self._app.run(*args, **kwargs)
            except Exception:
                return None
        # headless no-op
        return None

    def stop(self) -> Any:
        if self._app is not None:
            return self._app.exit()

    def invalidate(self) -> None:
        if self._app is not None:
            try:
                self._app.invalidate()
            except Exception:
                pass
        # headless: no-op

    def create_background_task(self, coro: Any) -> Any:
        # If there's a running loop in this thread, schedule on it.
        try:
            loop = asyncio.get_running_loop()
            return loop.create_task(coro)
        except RuntimeError:
            # No running loop in this thread; ensure a background loop is running
            try:
                return asyncio.run_coroutine_threadsafe(coro, self._ensure_background_loop())
            except Exception:
                # As a final fallback try to start a temporary loop to run the coro
                loop2 = asyncio.new_event_loop()
                try:
                    return loop2.run_until_complete(coro)
                finally:
                    try:
                        loop2.close()
                    except Exception:
                        pass

    def _ensure_background_loop(self) -> Any:
        """Start a background event loop in a thread and return it."""
        if self._bg_loop is not None:
            return self._bg_loop

        import threading

        loop = asyncio.new_event_loop()
        self._bg_loop = loop

        def _run() -> None:
            try:
                asyncio.set_event_loop(loop)
                loop.run_forever()
            except Exception:
                pass

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        self._bg_thread = t
        return loop

    def register_application(self, container: Any, key_bindings: Optional[Any] = None, full_screen: bool = False) -> bool:
        """If prompt_toolkit is available, create a real Application instance.

        This is a best-effort method: it constructs a prompt_toolkit Application
        using the provided container and key_bindings. If prompt_toolkit is not
        available, this is a no-op.
        """
        try:
            from prompt_toolkit.application import Application
            from prompt_toolkit.layout import Layout

            ptk_app: Any = Application(layout=Layout(container), full_screen=full_screen, key_bindings=key_bindings)
            self._app = ptk_app
            self._real_app = ptk_app
            self._key_bindings = key_bindings
            self._container = container
            return True
        except Exception:
            return False

    def register_keybinding(self, key: str, handler: Any, filter: Optional[Any] = None) -> bool:
        """Register a keybinding if prompt_toolkit is available; otherwise no-op.

        The handler signature is `handler(event)` following prompt_toolkit.
        """
        # If a key_bindings object has been injected, use it (DI-friendly)
        if hasattr(self, "_key_bindings") and self._key_bindings is not None:
            kb = self._key_bindings
        else:
            try:
                from prompt_toolkit.key_binding import KeyBindings
                kb = KeyBindings()
                self._key_bindings = kb
            except Exception:
                return False

        if filter is not None:
            kb.add(key, filter=filter)(handler)
        else:
            kb.add(key)(handler)

        # If we already have a constructed Application, try updating it.
        try:
            if hasattr(self, "_real_app") and self._real_app is not None:
                # Reconstructing the application with new key_bindings is safer;
                # if the application exposes a public API to add bindings in-place
                # we would prefer that. For now we attach to the stored key_bindings
                # and rely on consumers to call register_application again if needed.
                pass
        except Exception:
            pass
        return True

    def set_real_app(self, app: Any) -> None:
        """Dependency-injection helper: set the real prompt-toolkit Application
        instance that the wrapper should use. This avoids tests touching
        underscore attributes directly.
        """
        self._real_app = app
        self._app = app

    def set_key_bindings(self, kb: Any) -> None:
        """Dependency-injection helper to set a key_bindings object for tests
        to drive register_keybinding without importing prompt-toolkit.
        """
        self._key_bindings = kb

    def register_ctrlc(self, handler: Any) -> bool:
        """Best-effort register a Ctrl-C handler.

        If prompt-toolkit is available this registers a keybinding for Ctrl-C.
        Otherwise this method is a no-op to avoid changing process signal
        handlers in library code during tests.
        """
        try:
            # prompt-toolkit common binding name is 'c-c'
            return self.register_keybinding('c-c', handler)
        except Exception:
            return False


class PTKAdapter:
    """Adapter that maps domain tree -> representation used by prompt-toolkit.

    For now `build_layout` returns a nested dict describing the structure so
    tests can assert on it without needing a terminal or prompt_toolkit.
    """

    def __init__(self, page: Any, page_state: Any, events: Any, app: Optional[ApplicationWrapper] = None) -> None:
        self.page = page
        self.page_state = page_state
        self.events = events
        self.app: ApplicationWrapper = app if app is not None else ApplicationWrapper()
        self.cached_visibility: Dict[str, bool] = {}
        self.dependency_map: Dict[str, Set[str]] = {}
        # focus registry tracks focusable element paths and traverses them
        self.focus_registry = FocusRegistry()
        self._invalidate_scheduled = False
        # attempt to wire default focus keybindings (best-effort)
        try:
            self._setup_focus_keybindings()
        except Exception:
            # ignore failures in headless/no-ptk environments
            pass
        # mapping from element.path -> real prompt-toolkit widget (when created)
        self._path_to_widget: Dict[str, Any] = {}
        # mapping from element.path -> callable that will sync widget -> element
        # typically the callable is the widget._tui_sync attached by the
        # widget factory. Stored so adapter can call sync on accept/focus-change.
        self._path_to_sync: Dict[str, Callable[[], Any]] = {}

    def build_layout(self, root: Any) -> Dict[str, Any]:
        """Return a headless layout summary (nested dict) for the given root element.

        The returned structure is intentionally small and stable for tests:
        { 'type': 'container'|'leaf', 'name': str, 'variant': str, 'children': [...] }
        """

        def walk(node: Any) -> Dict[str, Any]:
            # detect container by presence of 'children' attribute
            if hasattr(node, 'children'):
                children = []
                for c in getattr(node, 'children', []):
                    if not getattr(c, 'visible', True):
                        continue
                    # register focusable children in the registry for traversal
                    if getattr(c, 'focusable', False):
                        try:
                            self.focus_registry.register(c)
                        except Exception:
                            pass
                    children.append(walk(c))
                return {
                    'type': 'container',
                    'name': getattr(node, 'name', ''),
                    'variant': getattr(node, 'variant', ''),
                    # alignment and sizing hints (may be None)
                    'align': getattr(node, 'align', None),
                    'min_height': getattr(node, 'min_height', None),
                    'max_height': getattr(node, 'max_height', None),
                    'offset': getattr(node, 'offset', None),
                    'children': children,
                }
            else:
                # register leaf if focusable
                if getattr(node, 'focusable', False):
                    try:
                        self.focus_registry.register(node)
                    except Exception:
                        pass
                return {
                    'type': 'leaf',
                    'name': getattr(node, 'name', ''),
                    'variant': getattr(node, 'variant', ''),
                    'min_height': getattr(node, 'min_height', None),
                    'max_height': getattr(node, 'max_height', None),
                    'offset': getattr(node, 'offset', None),
                }

        return walk(root)

    def wrap_with_visibility(self, container: Any, path: str) -> Any:
        # Phase B: when prompt-toolkit is available wrap the provided
        # container in a ConditionalContainer whose filter consults
        # self.cached_visibility[path]. Otherwise default the cached
        # visibility and return the original container.
        try:
            from prompt_toolkit.filters import Condition
            from prompt_toolkit.layout.containers import ConditionalContainer
        except Exception:
            # headless: ensure cached_visibility has a default and return
            # the original container
            try:
                self.cached_visibility.setdefault(path, True)
            except Exception:
                pass
            return container

        # Ensure a default visibility value exists for the path
        try:
            self.cached_visibility.setdefault(path, True)
        except Exception:
            pass

        # Build a Condition that reads the cached_visibility dictionary
        try:
            cond = Condition(lambda: bool(self.cached_visibility.get(path, True)))
            return ConditionalContainer(container, filter=cond)
        except Exception:
            # Fallback: return the raw container but keep cached_visibility
            return container

    def register_dependencies(self, path: str, keys: Any) -> None:
        for k in keys:
            self.dependency_map.setdefault(k, set()).add(path)

    def handle_state_change(self, changed_keys: List[str]) -> List[str]:
        # Phase B will recompute affected visibility and call mount/unmount hooks
        affected: set[str] = set()
        for k in changed_keys:
            affected.update(self.dependency_map.get(k, ()))
        return list(affected)

    def _schedule_invalidate(self) -> None:
        if not self._invalidate_scheduled:
            self._invalidate_scheduled = True
            # coalesce to next loop tick
            async def _do() -> None:
                await asyncio.sleep(0)
                self._invalidate_scheduled = False
                try:
                    self.app.invalidate()
                except Exception:
                    pass
            try:
                self.app.create_background_task(_do())
            except Exception:
                # no loop available — call invalidate synchronously
                try:
                    self.app.invalidate()
                except Exception:
                    pass
    def _setup_focus_keybindings(self) -> None:
        """Register Tab and Shift-Tab to move focus via the FocusRegistry.

        This is a best-effort helper: if ApplicationWrapper can't register
        keybindings (no prompt_toolkit available), it silently does nothing.
        """

        def _on_tab(event: Any = None) -> None:
            try:
                # sync the currently-focused widget before moving focus
                self._sync_focused_widget()
            except Exception:
                pass
            try:
                self.focus_registry.focus_next()
            except Exception:
                pass
            try:
                # Apply the focus to the real prompt-toolkit layout (if any)
                self._apply_focus_to_ptk()
            except Exception:
                pass
            try:
                self.app.invalidate()
            except Exception:
                pass

        def _on_shift_tab(event: Any = None) -> None:
            try:
                # sync before moving focus back
                self._sync_focused_widget()
            except Exception:
                pass
            try:
                self.focus_registry.focus_prev()
            except Exception:
                pass
            try:
                # Apply focus to PTK layout after registry change
                self._apply_focus_to_ptk()
            except Exception:
                pass
            try:
                self.app.invalidate()
            except Exception:
                pass

        # try common key names; register_keybinding is best-effort
        try:
            self.app.register_keybinding('tab', _on_tab)
        except Exception:
            pass
        try:
            # common representation for Shift+Tab in prompt_toolkit
            self.app.register_keybinding('s-tab', _on_shift_tab)
        except Exception:
            # fallback name
            try:
                self.app.register_keybinding('shift+tab', _on_shift_tab)
            except Exception:
                pass
        # As a fallback for environments where Tab is consumed by widgets
        # (for example TextArea), register alternate bindings that are less
        # likely to be intercepted: Ctrl-N / Ctrl-P for next/prev, and
        # Ctrl-M as an additional Enter/accept binding. These are registered
        # best-effort and won't break headless environments.
        try:
            self.app.register_keybinding('c-n', _on_tab)
        except Exception:
            pass
        try:
            self.app.register_keybinding('c-p', _on_shift_tab)
        except Exception:
            pass
        # 'enter'/_on_enter registration is handled below; register additional
        # alternate bindings afterwards where _on_enter is in scope.
        # Also register an 'enter' (accept) binding to trigger sync for the
        # current focused widget. This is best-effort and will no-op in
        # headless environments.
        try:
            def _on_enter(event: Any = None) -> None:
                try:
                    # Sync widget value first
                    self._sync_focused_widget()
                except Exception:
                    pass
                try:
                    # If the currently-focused element has an `on_click` handler,
                    # call it (useful for buttons). This bridges keyboard Enter
                    # to element-level actions.
                    focused = self.focus_registry.get_focused()
                    if focused:
                        elem = self._find_element_by_path(focused)
                        if elem is not None:
                            # If the element provides an explicit `on_enter` hook,
                            # call it and let the consumer control behavior.
                            ent = getattr(elem, 'on_enter', None)
                            if callable(ent):
                                try:
                                    ent()
                                    return
                                except Exception:
                                    pass

                            # Consumer can request Enter to move focus by setting
                            # metadata['enter_moves_focus'] = True or via factory.
                            try:
                                emf = getattr(elem, 'metadata', {}).get('enter_moves_focus', False)
                                if emf:
                                    try:
                                        self.focus_registry.focus_next()
                                        self._apply_focus_to_ptk()
                                        return
                                    except Exception:
                                        pass
                            except Exception:
                                pass

                            # Fallback to on_click for button-like elements
                            handler = getattr(elem, 'on_click', None)
                            if callable(handler):
                                try:
                                    handler()
                                except Exception:
                                    pass
                except Exception:
                    pass
            self.app.register_keybinding('enter', _on_enter)
            # Also register Ctrl-M as an alternate Enter/accept binding
            try:
                self.app.register_keybinding('c-m', _on_enter)
            except Exception:
                pass
        except Exception:
            pass

    def _sync_focused_widget(self) -> None:
        """Call the registered _tui_sync callable for the currently-focused element, if any."""
        try:
            focused = self.focus_registry.get_focused()
            if not focused:
                return
            sync = self._path_to_sync.get(focused)
            if sync is None:
                # No registered sync callable for this path
                return
            try:
                # Some sync callables will update the element directly. Others
                # may return a value which we should write back to the domain
                # element. Support both behaviors for robustness.
                ret = sync()
                if ret is not None:
                    # find the element in the page tree and write the value
                    elem = self._find_element_by_path(focused)
                    if elem is not None:
                        try:
                            if hasattr(elem, 'set_value'):
                                elem.set_value(ret)
                            else:
                                elem._value = ret
                            try:
                                elem.mark_dirty()
                            except Exception:
                                pass
                            # optional on_change handler
                            try:
                                handler = getattr(elem, 'on_change', None)
                                if callable(handler):
                                    handler(ret)
                            except Exception:
                                pass
                        except Exception:
                            pass
            except Exception:
                pass
        except Exception:
            pass

    def _find_element_by_path(self, path: str) -> Any:
        """Walk the page tree to find the element with the given dotted path."""
        try:
            root = self.page
            if root is None or path is None:
                return None

            # fast path: root has path matching
            if getattr(root, 'path', None) == path:
                return root

            def walk(node: Any) -> Any:
                if getattr(node, 'path', None) == path:
                    return node
                if hasattr(node, 'children'):
                    for c in getattr(node, 'children', []):
                        res = walk(c)
                        if res is not None:
                            return res
                return None

            return walk(root)
        except Exception:
            return None

    def register_widget_mapping(self, path: str, widget: Any) -> None:
        """Record mapping between domain element path and a real PTK widget.

        This allows the adapter to transfer keyboard focus from the FocusRegistry
        to the prompt-toolkit layout when available.
        """
        if path is None or widget is None:
            return
        try:
            self._path_to_widget[path] = widget
        except Exception:
            pass

    def _apply_focus_to_ptk(self) -> None:
        """If a real Application exists and we have a widget mapped for the
        currently-focused element path, focus that widget in the PTK layout.
        """
        try:
            focused = self.focus_registry.get_focused()
            if not focused:
                return
            widget = self._path_to_widget.get(focused)
            if widget is None:
                return
            # If ApplicationWrapper has a real app, try to set focus
            if hasattr(self.app, "_real_app") and self.app._real_app is not None:
                try:
                    app = self.app._real_app
                    # Some prompt-toolkit apps provide layout.focus(widget)
                    if hasattr(app, "layout") and hasattr(app.layout, "focus"):
                        # If widget is a wrapper (implements .ptk_widget), unwrap
                        try:
                            raw_widget = getattr(widget, 'ptk_widget', widget)
                        except Exception:
                            raw_widget = widget
                        try:
                            app.layout.focus(raw_widget)
                        except Exception:
                            # As a fallback, try calling focus() on the wrapper
                            try:
                                if hasattr(widget, 'focus') and callable(widget.focus):
                                    widget.focus()
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception:
            pass

    def build_real_layout(self, root: Any) -> Any:
        """Attempt to build a real prompt-toolkit layout from the domain tree.

        Returns the root prompt-toolkit container when successful, or None if
        prompt-toolkit is not available. This is best-effort and will not raise
        if prompt-toolkit is absent.
        """
        # Ensure the FocusRegistry is populated the same way the headless
        # layout builder would. This registers focusable elements so key
        # traversal (Tab/Shift-Tab) works even when we build the real
        # prompt-toolkit layout only.
        # Populate headless focus registry first so focusable elements are
        # registered before constructing the real prompt-toolkit layout.
        try:
            self.build_layout(root)
        except Exception:
            # best-effort: ignore failures but continue to attempt real build
            pass

        try:
            from prompt_toolkit.layout.containers import HSplit, VSplit, Window
            from prompt_toolkit.layout.controls import FormattedTextControl
        except Exception:
            return None

        def build(node: Any) -> Any:
            # container
            if hasattr(node, 'children'):
                widgets = []
                for c in getattr(node, 'children', []):
                    if not getattr(c, 'visible', True):
                        continue
                    w = build(c)
                    if w is not None:
                        widgets.append(w)
                if getattr(node, 'layout_hint', 'vertical') == 'horizontal':
                    return VSplit(widgets)
                return HSplit(widgets)

            # leaf
            desc = map_element_to_widget(node)
            w = desc.get('ptk_widget')
            if w is None:
                text = desc.get('text') or desc.get('value') or desc.get('label') or ''
                w = Window(content=FormattedTextControl(text))

            # If the factory returned an adapter/wrapper, the actual prompt-
            # toolkit widget to insert into the layout is the wrapper's
            # `.ptk_widget` attribute. Use layout_w for building the layout
            # while preserving `w` (the wrapper) for mapping/sync tasks.
            try:
                layout_w = getattr(w, 'ptk_widget', w)
            except Exception:
                layout_w = w

            # register mapping from element path to widget for focus transfer
            try:
                path = getattr(node, 'path', None)
                if path is not None:
                    # register the wrapper (if present) so adapter can later
                    # call its sync or focus methods. The layout uses
                    # `layout_w` which is the real PTK widget.
                    self.register_widget_mapping(path, w)
                    # If the widget exposes a _tui_sync callable, record it so
                    # the adapter can invoke it on accept or when focus
                    # changes. Also call it once to ensure initial widget ->
                    # element state synchronization.
                    try:
                        # Prefer wrapper _tui_sync if present, otherwise
                        # check the real layout widget for a sync helper.
                        sync_candidate = None
                        sync_candidate = getattr(w, '_tui_sync', None)
                        if sync_candidate is None:
                            sync_candidate = getattr(layout_w, '_tui_sync', None)

                        if sync_candidate is not None:
                            self._path_to_sync[path] = sync_candidate
                            try:
                                sync_candidate()
                            except Exception:
                                pass
                    except Exception:
                        pass
            except Exception:
                pass
            return layout_w

        root_container = build(root)

        # If the root (or Page) has floats attached, wrap the main layout
        # in a FloatContainer so overlays are rendered above the main UI.
        try:
            floats_attached = getattr(root, 'floats', None) or []
            if floats_attached:
                try:
                    from prompt_toolkit.layout.containers import Float, FloatContainer

                    float_list = []
                    for f in floats_attached:
                        try:
                            float_content = build(f)
                            top = f.metadata.get('top', None)
                            left = f.metadata.get('left', None)
                            right = f.metadata.get('right', None)
                            bottom = f.metadata.get('bottom', None)
                            float_list.append(Float(content=float_content, top=top, left=left, right=right, bottom=bottom))
                        except Exception:
                            pass
                    # Only wrap if we successfully built at least one Float
                    if float_list:
                        root_container = FloatContainer(root_container, floats=float_list)
                except Exception:
                    pass
        except Exception:
            pass

        # Do not force the root to expand vertically here. Keep the natural
        # size so each input renders as a single line unless individual
        # widgets request more space. This avoids occupying the whole terminal
        # height and keeps the layout compact.

        # Collect simple style mapping for frames/borders so tests and
        # consumers can inspect requested colors. This is a lightweight
        # convention: keys are selector-like strings ending with '.border'.
        try:
            styles: Dict[str, str] = {}
            def collect_styles(node: Any) -> None:
                try:
                    if getattr(node, 'border', False):
                        color = getattr(node, 'border_color', None)
                        if color:
                            p = getattr(node, 'path', None) or getattr(node, 'name', '')
                            key = f".{p}.border"
                            styles[key] = color
                except Exception:
                    pass
                try:
                    if hasattr(node, 'children'):
                        for c in getattr(node, 'children', []):
                            collect_styles(c)
                except Exception:
                    pass

            try:
                collect_styles(root)
            except Exception:
                pass
            # Expose the last computed style dict on the ApplicationWrapper
            try:
                self.app._last_style = styles
            except Exception:
                pass
        except Exception:
            pass

        # register Application with prompt-toolkit if possible
        try:
            keyb = getattr(self.app, '_key_bindings', None)
            self.app.register_application(root_container, key_bindings=keyb, full_screen=True)
        except Exception:
            pass

        # register Ctrl-C to stop the app (best-effort)
        try:
            self.app.register_ctrlc(lambda event=None: self.app.stop())
        except Exception:
            pass

        # apply focus mapping to real app if available
        try:
            self._apply_focus_to_ptk()
        except Exception:
            pass

        return root_container
