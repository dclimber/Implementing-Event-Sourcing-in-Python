import orders


def test_order_without_event_has_no_changes():
    order = orders.Order([])

    assert order.changes == []
    assert order.user_id is None
    assert order.status == ""


def test_order_gets_created_after_order_created_event():
    order_created = orders.OrderCreated(user_id=1)
    events = [order_created]

    order = orders.Order(events)

    assert order.user_id is not None
    assert isinstance(order.user_id, int)
    assert order.status == "new"


def test_error_is_raised_if_unknown_event_is_passed_in():
    order_created = orders.OrderCreated(user_id=1)
    events = [order_created]

    order = orders.Order(events)

    assert order.user_id is not None
    assert isinstance(order.user_id, int)
    assert order.status == "new"


def test_order_status_changes_after_status_changed_event():
    order_created = orders.OrderCreated(user_id=1)
    status_changed = orders.StatusChanged(new_status="confirmed")
    events = [order_created, status_changed]

    order = orders.Order(events)

    assert order.user_id is not None
    assert isinstance(order.user_id, int)
    assert order.status == "confirmed"
