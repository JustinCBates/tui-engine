"""Native prompt-toolkit alignment demo (clean, idiomatic).

This demo uses native prompt-toolkit widgets directly and avoids
overriding PTK layout behavior. The outer Frame owns the border and
children are constrained using PTK Dimensions/weight so they don't
force the outer border to misalign.

Run with:

    python demos/demo_alignment.py

Requires prompt-toolkit in your environment.
"""
from __future__ import annotations

try:
    from prompt_toolkit.application import Application
    from prompt_toolkit.application.current import get_app
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.filters import Condition
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import Float, FloatContainer, HSplit, Layout, VSplit
    from prompt_toolkit.layout.containers import ConditionalContainer, Window
    from prompt_toolkit.layout.dimension import Dimension
    from prompt_toolkit.styles import Style
    from prompt_toolkit.validation import ValidationError, Validator
    from prompt_toolkit.widgets import (
        Box,
        Button,
        CheckboxList,
        Frame,
        Label,
        RadioList,
        TextArea,
    )
except Exception:  # pragma: no cover - demo only
    raise


class NameValidator(Validator):
    def validate(self, document) -> None:
        text = document.text or ""
        if len(text.strip()) < 3:
            raise ValidationError(message="Enter at least 3 characters", cursor_position=len(text))


def build_app() -> Application:
    """Build and return the prompt-toolkit Application for the demo."""

    # No mutable state or completers needed — demo focuses on container only.

    # Build a three-column layout inside the Frame using Frames/Boxes so
    # each column can request expansion independently. This reproduces
    # the original demo contents while using weight-based Dimensions to
    # avoid forcing the outer Frame border to misalign.

    # Left: checkbox list
    checkbox = CheckboxList([
        ("x", "Enable feature X"),
        ("y", "Enable feature Y"),
        ("z", "Enable feature Z"),
    ])
    left = Frame(checkbox, title="Options", width=Dimension(weight=1), height=Dimension(weight=1))

    # Middle: split the single "Name" field into two single-line fields
    # (First and Last). Use `multiline=False` so Enter triggers the
    # TextArea's accept handler; handlers move focus to the next widget.
    description = TextArea(height=5, multiline=True)

    def _first_accept(buff):
        # Move focus to the last name field and indicate the buffer was
        # accepted by returning True.
        try:
            get_app().layout.focus(last_name)
        except Exception:
            pass
        return True


    def _last_accept(buff):
        # Move focus to the description area when last name is accepted.
        try:
            get_app().layout.focus(description)
        except Exception:
            pass
        return True


    first_name = TextArea(
        height=1,
        prompt="First: ",
        multiline=False,
        accept_handler=_first_accept,
    )

    last_name = TextArea(
        height=1,
        prompt="Last: ",
        multiline=False,
        accept_handler=_last_accept,
    )

    middle_inner = HSplit([
        Box(first_name, padding=0),
        Box(last_ , padding=0),
        Box(Label("Description:"), padding=0),
        Box(description, padding=0),
    ])
    middle = Frame(middle_inner, title="Input", width=Dimension(weight=2), height=Dimension(weight=1))

    # Right: radio list
    radio = RadioList([
        ("a", "Choice A"),
        ("b", "Choice B"),
        ("c", "Choice C"),
    ])
    right = Frame(radio, title="Select", width=Dimension(weight=1), height=Dimension(weight=1))

    # Footer: action buttons
    btn_ok = Button(text="OK", handler=lambda: get_app().exit(result=True))
    btn_cancel = Button(text="Cancel", handler=lambda: get_app().exit(result=False))
    footer = Box(VSplit([btn_ok, btn_cancel], padding=1), height=Dimension(preferred=3))

    # Main body: three columns in a VSplit, stacked above the footer.
    body = HSplit([
        VSplit([left, middle, right], padding=1),
        footer,
    ], padding=1)

    # Root Frame requests expansion so the Frame and its body occupy the
    # terminal's available space; children Frames use weight-based widths
    # so the layout engine can distribute space and keep borders aligned.
    root = Frame(body, title="Alignment Demo", width=Dimension(weight=1), height=Dimension(weight=1))

    # Key bindings
    kb = KeyBindings()

    @kb.add("tab")
    def _(event) -> None:  # move focus forward
        event.app.layout.focus_next()

    @kb.add("s-tab")
    def _(event) -> None:  # move focus backward
        event.app.layout.focus_previous()

    @kb.add("c-c")
    def _(event) -> None:  # exit on Ctrl-C
        """Allow Ctrl-C to close the demo cleanly (useful when running
        interactively in a terminal)."""
        event.app.exit()

    @kb.add("c-q")
    def _(event) -> None:  # exit on Ctrl-Q as well
        """Also allow Ctrl-Q to quit the demo."""
        event.app.exit()

    # App-level styling for frames (demonstrates mapping without per-widget overrides)
    style = Style.from_dict({
        "frame.border": "fg:#00aaff",
        "frame.label": "fg:#00aaff",
    })

    # Some terminals or IDEs intercept Ctrl-C/Ctrl-Q. Provide more
    # explicit, easy-to-hit alternatives that typically reach the app:
    @kb.add("escape")
    def _(event) -> None:  # exit on Escape
        event.app.exit()

    @kb.add("q")
    def _(event) -> None:  # exit on q
        event.app.exit()

    @kb.add("c-g")
    def _(event) -> None:  # exit on Ctrl-G
        event.app.exit()

    @kb.add("f10")
    def _(event) -> None:  # exit on F10
        event.app.exit()

    layout = Layout(root)
    app = Application(layout=layout, key_bindings=kb, full_screen=True, style=style)

    return app


def main() -> None:
    app = build_app()
    # Ensure Ctrl-C from the terminal sends the app an exit request.
    # Some terminals (or shells) can send SIGINT to the process directly,
    # so install a small signal handler that calls Application.exit().
    import signal

    def _sigint(signum, frame):
        try:
            app.exit()
        except Exception:
            # If exit fails for some reason, raise KeyboardInterrupt so the
            # process still terminates.
            raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _sigint)

    print("Launching native prompt-toolkit alignment demo — use Tab/Shift-Tab to move focus. (Ctrl-C/Ctrl-Q to quit)")
    try:
        app.run()
    except KeyboardInterrupt:
        # Allow a clean terminal return when SIGINT is delivered.
        pass


if __name__ == "__main__":
    main()
