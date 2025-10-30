"""PTK widget factory

Map domain elements (Element / ContainerElement) into prompt-toolkit widgets when
prompt-toolkit is available, or return a stable descriptor for headless/testing.
"""
from typing import Any, Dict
from tui_engine.widgets.protocols import TuiWidgetProtocol
from tui_engine.interfaces import IElement

try:
    # Try best-effort import of common prompt-toolkit widgets
    from prompt_toolkit.widgets import Button, TextArea  # type: ignore
    _PTK_AVAILABLE = True
except Exception:
    Button = None  # type: ignore
    TextArea = None  # type: ignore
    _PTK_AVAILABLE = False

try:
    # Import the TextInputAdapter wrapper so the factory can return a
    # consistent wrapper instance when prompt-toolkit is available.
    from tui_engine.widgets.text_input_adapter import TextInputAdapter  # type: ignore
except Exception:
    TextInputAdapter = None  # type: ignore

try:
    # Import ButtonAdapter wrapper if present
    from tui_engine.widgets.button_adapter import ButtonAdapter  # type: ignore
except Exception:
    ButtonAdapter = None  # type: ignore

try:
    from tui_engine.widgets.radio_list_adapter import RadioListAdapter  # type: ignore
except Exception:
    RadioListAdapter = None  # type: ignore

try:
    from tui_engine.widgets.checkbox_list_adapter import (
        CheckboxListAdapter,  # type: ignore
    )
except Exception:
    CheckboxListAdapter = None  # type: ignore

# Compatibility shims: prefer using our shim helpers which will return a real
# prompt-toolkit widget when available, or a tiny fallback otherwise.
try:
    from tui_engine.compat import maybe_checkboxlist, maybe_radiolist  # type: ignore
except Exception:
    maybe_checkboxlist = None  # type: ignore
    maybe_radiolist = None  # type: ignore


def _build_fallback_widget(norm: list, variant: str, element: Any) -> Any | None:
    """Attempt to construct a minimal PTK-backed widget or adapter for
    extended variants. This is a best-effort helper used when the main
    construction path fails to yield a usable widget.
    """
    try:
        candidate = None
        if variant in ('select', 'radio'):
            if maybe_radiolist is not None:
                candidate = maybe_radiolist(norm)
            else:
                try:
                    from prompt_toolkit.widgets import RadioList
                    candidate = RadioList(norm)
                except Exception:
                    candidate = None

            if candidate is not None:
                try:
                    if RadioListAdapter is not None:
                        return RadioListAdapter(candidate, element)
                except Exception:
                    return candidate

        if variant == 'checkbox_list':
            if maybe_checkboxlist is not None:
                candidate = maybe_checkboxlist(norm)
            else:
                try:
                    from prompt_toolkit.widgets import CheckboxList
                    candidate = CheckboxList(norm)
                except Exception:
                    candidate = None

            if candidate is not None:
                try:
                    if CheckboxListAdapter is not None:
                        return CheckboxListAdapter(candidate, element)
                except Exception:
                    return candidate
    except Exception:
        return None
    return None


def _sync_widget_to_element(widget: TuiWidgetProtocol | Any, element: IElement | Any, variant: str) -> None:
    """Best-effort sync from a real prompt-toolkit widget into the domain element.

    This does not assume specific prompt-toolkit versions — it probes common
    attribute names (like `current_value`, `checked_values`, `current_values`)
    and updates `element._value` (or uses set_value if available). If the
    element exposes an `on_change` call-able, it will be invoked after sync.
    """
    try:
        val = None
        # RadioList typically exposes `current_value` or a similar attr
        if getattr(widget, "current_value", None) is not None:
            val = getattr(widget, "current_value")
        # Some CheckboxList implementations expose `checked_values` or
        # `current_values` as an iterable of selected keys
        elif getattr(widget, "checked_values", None) is not None:
            val = list(getattr(widget, "checked_values"))
        elif getattr(widget, "current_values", None) is not None:
            val = list(getattr(widget, "current_values"))
        # fallback: some widget may expose `values` or `selected` names
        elif getattr(widget, "selected", None) is not None:
            val = getattr(widget, "selected")

        if val is not None:
            # Normalize single-selection into scalar, multi-selection into list
            if variant == "checkbox_list":
                newv = list(val) if not isinstance(val, (list, set, tuple)) else list(val)
            else:
                newv = val

            # Prefer using set_value if the element offers it
            try:
                setter = getattr(element, "set_value", None)
                if callable(setter):
                    setter(newv)
                else:
                    try:
                        setattr(element, "_value", newv)
                    except Exception:
                        pass
                # mark dirty if available
                try:
                    mark = getattr(element, "mark_dirty", None)
                    if callable(mark):
                        mark()
                except Exception:
                    pass
            except Exception:
                # best-effort write; ignore failures
                try:
                    setattr(element, "_value", newv)
                except Exception:
                    pass

            # Call an optional change handler
            try:
                handler = getattr(element, "on_change", None)
                if callable(handler):
                    handler(newv)
            except Exception:
                pass
    except Exception:
        # Never let widget-sync break the adapter
        return


def map_element_to_widget(element: IElement | Any) -> Dict[str, Any]:
    """Return a descriptor or a real widget mapping for `element`.

    The returned dict contains stable keys useful for tests and headless layout
    summaries. If prompt-toolkit is installed, the mapping will also include a
    `ptk_widget` value holding the real widget instance.
    """
    if element is None:
        return {"type": "none", "path": None}

    name = getattr(element, "name", None)
    variant = getattr(element, "variant", None)
    path = getattr(element, "path", None)

    desc: Dict[str, Any] = {"path": path, "name": name, "variant": variant}

    # Button
    if variant == "button":
        desc.update({"type": "button", "label": name})
        desc['on_click'] = getattr(element, 'on_click', getattr(element, 'metadata', {}).get('on_click'))

        if _PTK_AVAILABLE and Button is not None:
            try:
                # Create raw button without binding so we can wrap it with
                # the adapter and then attach an adapter-aware handler.
                raw_button: TuiWidgetProtocol | Any = Button(text=str(name), handler=None)

                # Try to create an adapter wrapper around the raw widget
                adapter_button: TuiWidgetProtocol | Any = None
                try:
                    if ButtonAdapter is not None:
                        adapter_button = ButtonAdapter(raw_button, element)
                except Exception:
                    adapter_button = None

                # Apply runtime contract attributes to the underlying widget
                try:
                    setattr(raw_button, "_tui_path", path)
                except Exception:
                    pass
                try:
                    setattr(raw_button, "_tui_focusable", True)
                except Exception:
                    pass

                # If element exposes an on_click, wire the raw handler to call
                # adapter.click() (or element.on_click as a fallback).
                try:
                    if callable(getattr(element, 'on_click', None)):
                        def _handler() -> None:
                            try:
                                if adapter_button is not None:
                                    adapter_button.click()
                                else:
                                    try:
                                        getattr(element, 'on_click')()
                                    except Exception:
                                        pass
                            except Exception:
                                pass

                        try:
                            setattr(raw_button, 'handler', _handler)
                        except Exception:
                            # If attribute is read-only, attempt to wrap via
                            # existing attribute names; ignore failures
                            try:
                                orig = getattr(raw_button, 'handler', None)

                                def _wrap_handler(*a: Any, __orig: Any = orig, **kw: Any) -> None:
                                    try:
                                        if callable(__orig):
                                            __orig(*a, **kw)
                                    finally:
                                        try:
                                            _handler()
                                        except Exception:
                                            pass

                                try:
                                    setattr(raw_button, 'handler', _wrap_handler)
                                except Exception:
                                    pass
                            except Exception:
                                pass
                except Exception:
                    pass

                desc["ptk_widget"] = adapter_button or raw_button
            except Exception:
                desc["ptk_widget"] = None
        else:
            desc["ptk_widget"] = None
        return desc

    # Input
    if variant == "input":
        value = getattr(element, "_value", None)
        desc.update({"type": "input", "value": value})
        # If prompt-toolkit is available and our adapter wrapper imported,
        # construct a TextArea and wrap it with TextInputAdapter so the
        # adapter surface is consistent for PTK-backed inputs.
        if _PTK_AVAILABLE and TextArea is not None and TextInputAdapter is not None:
            try:
                # Use a single-line TextArea so the input behaves like a
                # standard form field (Enter accepts/moves focus instead of
                # inserting a newline). Disable wrapping to keep it compact.
                raw_input: TuiWidgetProtocol | Any = TextArea(
                    text=str(value) if value is not None else "",
                    multiline=False,
                    wrap_lines=False,
                )

                # Create the wrapper around the real widget
                adapter_input: TuiWidgetProtocol | Any = None
                try:
                    adapter_input = TextInputAdapter(raw_input)
                except Exception:
                    adapter_input = None

                # Apply runtime contract attributes to the underlying widget
                try:
                    setattr(raw_input, "_tui_path", path)
                except Exception:
                    pass
                try:
                    setattr(raw_input, "_tui_focusable", True)
                except Exception:
                    pass

                desc["ptk_widget"] = adapter_input
            except Exception:
                desc["ptk_widget"] = None
        else:
            desc["ptk_widget"] = None
        return desc

    # Extended variants: select / radio / checkbox_list / checkbox
    if variant in ("select", "radio", "checkbox_list", "checkbox"):
        opts = []
        try:
            opts = getattr(element, 'metadata', {}).get('options', [])
        except Exception:
            opts = []

        norm = []
        for o in opts:
            if isinstance(o, tuple) and len(o) >= 2:
                norm.append((o[0], o[1]))
            else:
                norm.append((o, str(o)))

        desc.update({'type': variant, 'options': norm})

        sel = getattr(element, '_value', None)
        if sel is None:
            sel = getattr(element, 'metadata', {}).get('selected')
        desc['selected'] = sel

        if variant == 'checkbox_list':
            multi = getattr(element, '_value', None)
            if multi is None:
                multi = getattr(element, 'metadata', {}).get('selected', [])
            try:
                desc['selected'] = set(multi)
            except Exception:
                desc['selected'] = set()

        if _PTK_AVAILABLE:
            # predeclare branch-local variables to avoid mypy 'no-redef' errors
            raw_radio: TuiWidgetProtocol | Any = None
            w_radio: TuiWidgetProtocol | Any = None
            raw_checkbox: TuiWidgetProtocol | Any = None
            w_checkbox: TuiWidgetProtocol | Any = None
            w_window: TuiWidgetProtocol | Any = None

            try:
                # Try to create a 'real' widget for the extended variants when
                # prompt-toolkit provides one. If not available or construction
                # fails, fall back to a textual Window so headless descriptors
                # remain stable.
                if variant in ('select', 'radio'):
                    try:
                        # Use shim helper which will return a real RadioList when
                        # prompt-toolkit supports it, or a small fallback object.
                        if maybe_radiolist is not None:
                            raw_radio = maybe_radiolist(norm)
                        else:
                            from prompt_toolkit.widgets import RadioList
                            raw_radio = RadioList(norm)

                        # If the shim returned a fallback (it sets __ptk_repr__),
                        # don't attempt to wrap it with an adapter that expects a
                        # real prompt-toolkit widget — just use the fallback as-is.
                        if hasattr(raw_radio, "__ptk_repr__"):
                            w_radio = raw_radio
                        else:
                            if RadioListAdapter is not None:
                                try:
                                    w_radio = RadioListAdapter(raw_radio, element)
                                except Exception:
                                    w_radio = raw_radio
                            else:
                                w_radio = raw_radio
                    except Exception:
                        from prompt_toolkit.layout.containers import Window
                        from prompt_toolkit.layout.controls import FormattedTextControl

                        w_window = Window(content=FormattedTextControl(str(norm)))

                elif variant == 'checkbox_list':
                    # Prefer CheckboxList if present in this prompt-toolkit
                    # distribution. Not all versions expose it, so fall back
                    # to a simple Window representation when missing.
                    try:
                        # Use shim helper for CheckboxList to handle PTK
                        # distributions that don't export CheckboxList.
                        if maybe_checkboxlist is not None:
                            raw_checkbox = maybe_checkboxlist(norm)
                        else:
                            from prompt_toolkit.widgets import CheckboxList
                            raw_checkbox = CheckboxList(norm)

                        if hasattr(raw_checkbox, "__ptk_repr__"):
                            w_checkbox = raw_checkbox
                        else:
                            if CheckboxListAdapter is not None:
                                try:
                                    w_checkbox = CheckboxListAdapter(raw_checkbox, element)
                                except Exception:
                                    w_checkbox = raw_checkbox
                            else:
                                w_checkbox = raw_checkbox
                    except Exception:
                        from prompt_toolkit.layout.containers import Window
                        from prompt_toolkit.layout.controls import FormattedTextControl

                        w_window = Window(content=FormattedTextControl(str(norm)))

                else:
                    # single checkbox or other compact controls
                    from prompt_toolkit.layout.containers import Window
                    from prompt_toolkit.layout.controls import FormattedTextControl

                    w_window = Window(content=FormattedTextControl(str(norm)))

                try:
                    # prefer whichever wrapper variable was actually created
                    candidate = w_radio if w_radio is not None else (w_checkbox if w_checkbox is not None else w_window)
                    if candidate is not None:
                        setattr(candidate, '_tui_path', getattr(element, 'path', None))
                except Exception:
                    pass
                try:
                    candidate = None
                    if 'w_radio' in locals():
                        candidate = w_radio
                    elif 'w_checkbox' in locals():
                        candidate = w_checkbox
                    else:
                        candidate = w_window
                    setattr(candidate, '_tui_focusable', True)
                except Exception:
                    pass

                # Attach a best-effort sync helper so test harnesses or the
                # runtime can call `w._tui_sync()` to push widget state back to
                # the element. We also attempt to wrap any accept/handler
                # attributes if present so UI interactions trigger the sync.
                try:
                    def _do_sync() -> None:
                        _sync_widget_to_element(candidate, element, variant)

                    try:
                        setattr(candidate, '_tui_sync', _do_sync)
                    except Exception:
                        pass
                except Exception:
                    pass

                # If the widget supports an 'accept' or 'handler' hook, try to
                # wrap it so the element gets updated automatically on user
                # accept events. This is intentionally non-fatal and probes a
                # few common attribute names.
                try:
                    for attr in ('handler', 'accept_handler', 'accept', 'on_select'):
                        if hasattr(candidate, attr):
                            try:
                                orig = getattr(candidate, attr)

                                def _wrap_accept(*a: Any, __orig: Any = orig, **kw: Any) -> None:
                                    try:
                                        if callable(__orig):
                                            __orig(*a, **kw)
                                    finally:
                                        _sync_widget_to_element(candidate, element, variant)
                                try:
                                    setattr(candidate, attr, _wrap_accept)
                                except Exception:
                                    # Some attributes are read-only; ignore
                                    pass
                            except Exception:
                                pass
                except Exception:
                    pass

                desc['ptk_widget'] = candidate
            except Exception:
                desc['ptk_widget'] = None

        # If construction above resulted in no widget (some PTK installs may
        # omit CheckboxList/RadioList), attempt a minimal fallback so callers
        # observing `ptk_widget` get a usable object rather than None.
        try:
            if desc.get('ptk_widget') is None and _PTK_AVAILABLE:
                try:
                    # Try shim helpers first
                    if variant in ('select', 'radio'):
                        candidate2 = maybe_radiolist(norm) if maybe_radiolist is not None else None
                    elif variant == 'checkbox_list':
                        candidate2 = maybe_checkboxlist(norm) if maybe_checkboxlist is not None else None
                    else:
                        candidate2 = None

                    if candidate2 is None and _PTK_AVAILABLE:
                        # Try importing concrete widget types as a final attempt
                        try:
                            if variant in ('select', 'radio'):
                                from prompt_toolkit.widgets import RadioList
                                candidate2 = RadioList(norm)
                            elif variant == 'checkbox_list':
                                from prompt_toolkit.widgets import CheckboxList
                                candidate2 = CheckboxList(norm)
                        except Exception:
                            candidate2 = None

                    if candidate2 is not None:
                        # Wrap with adapter if present. Annotate `wrapped` to avoid
                        # mypy inferring incompatible concrete adapter types.
                        wrapped: TuiWidgetProtocol | Any = candidate2
                        try:
                            if variant == 'checkbox_list' and CheckboxListAdapter is not None:
                                wrapped = CheckboxListAdapter(candidate2, element)
                            elif variant in ('select', 'radio') and RadioListAdapter is not None:
                                wrapped = RadioListAdapter(candidate2, element)
                            else:
                                wrapped = candidate2
                        except Exception:
                            wrapped = candidate2

                        try:
                            setattr(wrapped, '_tui_path', getattr(element, 'path', None))
                        except Exception:
                            pass
                        try:
                            setattr(wrapped, '_tui_focusable', True)
                        except Exception:
                            pass
                        try:
                            def _do_sync2() -> None:
                                _sync_widget_to_element(wrapped, element, variant)

                            setattr(wrapped, '_tui_sync', _do_sync2)
                        except Exception:
                            pass

                        desc['ptk_widget'] = wrapped
                except Exception:
                    # keep None if anything goes wrong
                    pass
        except Exception:
            pass
        return desc

    # Default textual element
    value = getattr(element, "_value", None)
    desc.update({"type": "text", "text": str(value) if value is not None else ""})
    desc["ptk_widget"] = None
    return desc



    # Extended variants: select/radio/checkbox-list
    # Note: these are not separate branches above because variant is already
    # checked; we handle additional variants by analyzing element.variant early

