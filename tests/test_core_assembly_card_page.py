def test_card_show_hide_and_parent():
    from questionary_extended.core.page import Page

    p = Page(title="Main")
    c = p.card("Card 1")

    assert c.visible is True
    c.hide()
    assert c.visible is False
    c.show()
    assert c.visible is True
    # parent access
    assert c.parent() is p


def test_assembly_event_handlers_and_parent():
    from questionary_extended.core.page import Page

    p = Page(title="Main")
    a = p.assembly("asm1")

    called = {}

    def on_change(field, handler):
        called['change'] = (field, handler)

    def validator(assembly):
        return None

    def on_complete_handler(value, assembly):
        called['complete'] = (value, assembly)

    # register handlers
    a.on_change('f1', lambda v, asm: None)
    a.on_validate(validator)
    a.on_complete('f2', on_complete_handler)

    # ensure handlers were recorded in event_handlers
    assert any(reg[0] == 'f1' for reg in a.event_handlers['change'])
    assert validator in a.event_handlers['validate']
    assert any(reg[0] == 'f2' for reg in a.event_handlers['complete'])

    # parent access
    assert a.parent() is p
