from orders.domain import events
from orders.domain.models import EventsStream, Order


def test_order_without_event_has_no_changes():
    event_stream = EventsStream(events=[], version=0)
    order = Order(event_stream)

    assert order.changes == []
    assert order.user_id is None
    assert order.status == ""


def test_order_gets_created_after_order_created_event():
    order_created = events.OrderCreated(user_id=1)
    event_stream = EventsStream(events=[order_created], version=1)

    order = Order(event_stream)

    assert order.user_id == 1
    assert isinstance(order.user_id, int)
    assert order.status == "new"


def test_error_is_raised_if_unknown_event_is_passed_in():
    event_stream = EventsStream(events=[], version=0)
    order = Order(event_stream)

    try:
        order.apply("UnknownEvent")
        assert False, "Expected ValueError for unknown event"
    except ValueError:
        pass


def test_order_status_changes_after_status_changed_event():
    order_created = events.OrderCreated(user_id=1)
    status_changed = events.StatusChanged(new_status="confirmed")
    event_stream = EventsStream(events=[order_created, status_changed], version=2)

    order = Order(event_stream)

    assert order.user_id == 1
    assert isinstance(order.user_id, int)
    assert order.status == "confirmed"
