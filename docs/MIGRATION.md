Migration guide: Card/Section/Assembly -> ContainerElement

This guide explains how to update code that used the legacy Card/Section/Assembly
abstractions to the new `ContainerElement`-based API introduced in the
feature/demos branch.

Key changes
- The old `Card`, `Section`, and `Assembly` types were consolidated into a
  single `ContainerElement` class. This simplifies composition and reduces
  duplication in adapters.
- Leaf elements (text, input, button) are represented by `Element`.
- `ContainerElement.child(name, variant=...)` creates nested containers. Use
  `container.add(element)` to attach existing `Element` instances.

Examples
--------
Old (Card/Section style):

    card = Card('user')
    header = card.section('header')
    header.add_text('title', 'My App')

New:

    from tui_engine.container import ContainerElement

    root = ContainerElement('root')
    header = root.child('header')
    header.text('title', 'My App')

Handlers and callbacks
----------------------
- Buttons: pass `on_click` to `container.button(label, on_click=...)`.
- Input values: `Element.get_value()` / `Element.set_value()` are provided; use
  `element._value` for quick access in tests if necessary.

Adapter considerations
---------------------
- The PTK adapter expects `Element` leaves to have `variant` set to 'input',
  'button', 'text', 'select', etc. Container nodes should be `ContainerElement`.
- For DI-friendly testing, use `ApplicationWrapper.set_real_app(...)` and
  `set_key_bindings(...)` instead of monkeypatching internal attributes.

If you have code that needs help migrating, paste a short snippet and I can
provide the exact transformation.