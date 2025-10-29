from typing import Any, Optional

try:
    from prompt_toolkit.widgets import TextArea  # type: ignore
    _PTK_AVAILABLE = True
except Exception:
    TextArea = None  # type: ignore
    _PTK_AVAILABLE = False


class TextInputAdapter:
    """Adapter/wrapper for single-line/multi-line text input widgets.

    Implements a small interface similar to ValueWidgetProtocol.
    This wrapper abstracts differences between real prompt-toolkit widgets and
    lightweight fakes used in tests.
    """

    def __init__(self, element: Optional[Any] = None, widget: Optional[Any] = None):
        self.element = element
        # If a widget is provided, use it. Otherwise, create a TextArea when PTK
        # is available. If neither is available, create a simple fake object.
        if widget is not None:
            self.widget = widget
        else:
            if _PTK_AVAILABLE and TextArea is not None:
                initial = None
                try:
                    initial = getattr(element, 'get_value', None) and element.get_value()
                except Exception:
                    initial = None
                self.widget = TextArea(text=str(initial) if initial is not None else "")
            else:
                class _Fake:
                    def __init__(self, text=""):
                        self.text = text

                initial = None
                try:
                    initial = getattr(element, 'get_value', None) and element.get_value()
                except Exception:
                    initial = None
                self.widget = _Fake(text=str(initial) if initial is not None else "")

        # runtime contract attributes
        try:
            setattr(self.widget, '_tui_path', getattr(element, 'path', None))
        except Exception:
            pass
        try:
            setattr(self.widget, '_tui_focusable', True)
        except Exception:
            pass

    # Expose the underlying PTK widget for adapter compatibility
    @property
    def ptk_widget(self):
        return self.widget

    def focus(self) -> None:
        # If the wrapped widget has a focus method or similar, call it.
        try:
            if hasattr(self.widget, 'focus'):
                self.widget.focus()
        except Exception:
            pass

    def _tui_sync(self) -> Optional[Any]:
        """Read widget content and return it. Adapter may apply returned value.

        The method is intentionally simple: it reads common attribute names like
        `text` (TextArea) and returns the string value.
        """
        try:
            # prompt-toolkit TextArea uses `.text`
            if hasattr(self.widget, 'text'):
                return getattr(self.widget, 'text')
            # some widgets may expose `.get_text()` or `.content`
            if hasattr(self.widget, 'get_text') and callable(getattr(self.widget, 'get_text')):
                return getattr(self.widget, 'get_text')()
            if hasattr(self.widget, 'content'):
                return str(getattr(self.widget, 'content'))
        except Exception:
            pass
        return None

    def get_value(self) -> Any:
        try:
            v = self._tui_sync()
            if v is None and self.element is not None:
                try:
                    return self.element.get_value()
                except Exception:
                    return None
            return v
        except Exception:
            return None

    def set_value(self, value: Any) -> None:
        try:
            if hasattr(self.widget, 'text'):
                try:
                    setattr(self.widget, 'text', str(value) if value is not None else "")
                except Exception:
                    # TextArea.text may be a property; try calling a setter if present
                    try:
                        self.widget.text = str(value) if value is not None else ""
                    except Exception:
                        pass
            # Also write to element if present
            if self.element is not None:
                try:
                    if hasattr(self.element, 'set_value'):
                        self.element.set_value(value)
                    else:
                        setattr(self.element, '_value', value)
                        try:
                            self.element.mark_dirty()
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass
