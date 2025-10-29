"""PTK widget factory

Map domain elements (Element / ContainerElement) into prompt-toolkit widgets when
prompt-toolkit is available, or return a stable descriptor for headless/testing.
"""
from typing import Any, Dict

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
    from tui_engine.widgets.checkbox_list_adapter import CheckboxListAdapter  # type: ignore
except Exception:
    CheckboxListAdapter = None  # type: ignore

# Compatibility shims: prefer using our shim helpers which will return a real
# prompt-toolkit widget when available, or a tiny fallback otherwise.
try:
    from tui_engine.compat import maybe_checkboxlist, maybe_radiolist  # type: ignore
except Exception:
    maybe_checkboxlist = None  # type: ignore
    maybe_radiolist = None  # type: ignore


def _sync_widget_to_element(widget: Any, element: Any, variant: str) -> None:
    """Best-effort sync from a real prompt-toolkit widget into the domain element.

    This does not assume specific prompt-toolkit versions — it probes common
    attribute names (like `current_value`, `checked_values`, `current_values`)
    and updates `element._value` (or uses set_value if available). If the
    element exposes an `on_change` call-able, it will be invoked after sync.
    """
    try:
        val = None
        # RadioList typically exposes `current_value` or a similar attr
        if hasattr(widget, "current_value"):
            val = getattr(widget, "current_value")
        # Some CheckboxList implementations expose `checked_values` or
        # `current_values` as an iterable of selected keys
        elif hasattr(widget, "checked_values"):
            val = list(getattr(widget, "checked_values"))
        elif hasattr(widget, "current_values"):
            val = list(getattr(widget, "current_values"))
        # fallback: some widget may expose `values` or `selected` names
        elif hasattr(widget, "selected"):
            val = getattr(widget, "selected")

        if val is not None:
            # Normalize single-selection into scalar, multi-selection into list
            if variant == "checkbox_list":
                newv = list(val) if not isinstance(val, (list, set, tuple)) else list(val)
            else:
                newv = val

            # Prefer using set_value if the element offers it
            try:
                if hasattr(element, "set_value"):
                    element.set_value(newv)
                else:
                    setattr(element, "_value", newv)
                # mark dirty if available
                try:
                    element.mark_dirty()
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


def map_element_to_widget(element: Any) -> Dict[str, Any]:
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
        if hasattr(element, 'on_click'):
            desc['on_click'] = getattr(element, 'on_click')
        else:
            desc['on_click'] = getattr(element, 'metadata', {}).get('on_click')

        if _PTK_AVAILABLE and Button is not None:
            try:
                # Create raw button without binding so we can wrap it with
                # the adapter and then attach an adapter-aware handler.
                raw = Button(text=str(name), handler=None)

                # Try to create an adapter wrapper around the raw widget
                adapter = None
                try:
                    if ButtonAdapter is not None:
                        adapter = ButtonAdapter(raw, element)
                except Exception:
                    adapter = None

                # Apply runtime contract attributes to the underlying widget
                try:
                    setattr(raw, "_tui_path", path)
                except Exception:
                    pass
                try:
                    setattr(raw, "_tui_focusable", True)
                except Exception:
                    pass

                # If element exposes an on_click, wire the raw handler to call
                # adapter.click() (or element.on_click as a fallback).
                try:
                    if hasattr(element, 'on_click') and callable(getattr(element, 'on_click')):
                        def _handler():
                            try:
                                if adapter is not None:
                                    adapter.click()
                                else:
                                    try:
                                        element.on_click()
                                    except Exception:
                                        pass
                            except Exception:
                                pass

                        try:
                            setattr(raw, 'handler', _handler)
                        except Exception:
                            # If attribute is read-only, attempt to wrap via
                            # existing attribute names; ignore failures
                            try:
                                orig = getattr(raw, 'handler', None)
                                def _wrap(*a, __orig=orig, **kw):
                                    try:
                                        if callable(__orig):
                                            __orig(*a, **kw)
                                    finally:
                                        try:
                                            _handler()
                                        except Exception:
                                            pass
                                try:
                                    setattr(raw, 'handler', _wrap)
                                except Exception:
                                    pass
                            except Exception:
                                pass

                except Exception:
                    pass

                desc["ptk_widget"] = adapter or raw
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
                raw = TextArea(text=str(value) if value is not None else "")
                # Create the wrapper around the real widget
                try:
                    adapter = TextInputAdapter(raw)
                except Exception:
                    adapter = None

                # Apply runtime contract attributes to the underlying widget
                try:
                    setattr(raw, "_tui_path", path)
                except Exception:
                    pass
                try:
                    setattr(raw, "_tui_focusable", True)
                except Exception:
                    pass

                desc["ptk_widget"] = adapter
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
                            raw = maybe_radiolist(norm)
                        else:
                            from prompt_toolkit.widgets import RadioList
                            raw = RadioList(norm)

                        # If the shim returned a fallback (it sets __ptk_repr__),
                        # don't attempt to wrap it with an adapter that expects a
                        # real prompt-toolkit widget — just use the fallback as-is.
                        if hasattr(raw, "__ptk_repr__"):
                            w = raw
                        else:
                            if RadioListAdapter is not None:
                                try:
                                    w = RadioListAdapter(raw, element)
                                except Exception:
                                    w = raw
                            else:
                                w = raw
                    except Exception:
                        from prompt_toolkit.layout.controls import FormattedTextControl
                        from prompt_toolkit.layout.containers import Window

                        w = Window(content=FormattedTextControl(str(norm)))

                elif variant == 'checkbox_list':
                    # Prefer CheckboxList if present in this prompt-toolkit
                    # distribution. Not all versions expose it, so fall back
                    # to a simple Window representation when missing.
                    try:
                        # Use shim helper for CheckboxList to handle PTK
                        # distributions that don't export CheckboxList.
                        if maybe_checkboxlist is not None:
                            raw = maybe_checkboxlist(norm)
                        else:
                            from prompt_toolkit.widgets import CheckboxList
                            raw = CheckboxList(norm)

                        if hasattr(raw, "__ptk_repr__"):
                            w = raw
                        else:
                            if CheckboxListAdapter is not None:
                                try:
                                    w = CheckboxListAdapter(raw, element)
                                except Exception:
                                    w = raw
                            else:
                                w = raw
                    except Exception:
                        from prompt_toolkit.layout.controls import FormattedTextControl
                        from prompt_toolkit.layout.containers import Window

                        w = Window(content=FormattedTextControl(str(norm)))

                else:
                    # single checkbox or other compact controls
                    from prompt_toolkit.layout.controls import FormattedTextControl
                    from prompt_toolkit.layout.containers import Window

                    w = Window(content=FormattedTextControl(str(norm)))

                try:
                    setattr(w, '_tui_path', getattr(element, 'path', None))
                except Exception:
                    pass
                try:
                    setattr(w, '_tui_focusable', True)
                except Exception:
                    pass

                # Attach a best-effort sync helper so test harnesses or the
                # runtime can call `w._tui_sync()` to push widget state back to
                # the element. We also attempt to wrap any accept/handler
                # attributes if present so UI interactions trigger the sync.
                try:
                    def _do_sync():
                        _sync_widget_to_element(w, element, variant)

                    setattr(w, '_tui_sync', _do_sync)
                except Exception:
                    pass

                # If the widget supports an 'accept' or 'handler' hook, try to
                # wrap it so the element gets updated automatically on user
                # accept events. This is intentionally non-fatal and probes a
                # few common attribute names.
                try:
                    for attr in ('handler', 'accept_handler', 'accept', 'on_select'):
                        if hasattr(w, attr):
                            try:
                                orig = getattr(w, attr)

                                def _wrap(*a, __orig=orig, **kw):
                                    try:
                                        if callable(__orig):
                                            __orig(*a, **kw)
                                    finally:
                                        _sync_widget_to_element(w, element, variant)

                                try:
                                    setattr(w, attr, _wrap)
                                except Exception:
                                    # Some attributes are read-only; ignore
                                    pass
                            except Exception:
                                pass
                except Exception:
                    pass

                desc['ptk_widget'] = w
            except Exception:
                desc['ptk_widget'] = None
        else:
            desc['ptk_widget'] = None
        return desc

    # Default textual element
    value = getattr(element, "_value", None)
    desc.update({"type": "text", "text": str(value) if value is not None else ""})
    desc["ptk_widget"] = None
    return desc



    # Extended variants: select/radio/checkbox-list
    # Note: these are not separate branches above because variant is already
    # checked; we handle additional variants by analyzing element.variant early

