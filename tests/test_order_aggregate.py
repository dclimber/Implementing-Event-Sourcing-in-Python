from orders.domain import events, models


def test_order_without_event_has_no_changes():
    order = models.Order([])

    assert order.changes == []
    assert order.user_id is None
    assert order.status == ""


def test_order_gets_created_after_order_created_event():
    order_created = models.OrderCreated(user_id=1)
    input_events = [order_created]

    order = models.Order(input_events)

    assert order.user_id is not None
    assert isinstance(order.user_id, int)
    assert order.status == "new"


def test_error_is_raised_if_unknown_event_is_passed_in():
    order_created = events.OrderCreated(user_id=1)
    input_events = [order_created]

    order = models.Order(input_events)

    assert order.user_id is not None
    assert isinstance(order.user_id, int)
    assert order.status == "new"


def test_order_status_changes_after_status_changed_event():
    order_created = events.OrderCreated(user_id=1)
    status_changed = events.StatusChanged(new_status="confirmed")
    input_events = [order_created, status_changed]

    order = models.Order(input_events)

    assert order.user_id is not None
    assert isinstance(order.user_id, int)
    assert order.status == "confirmed"
