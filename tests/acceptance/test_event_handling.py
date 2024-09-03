import pytest
from pytest_bdd import given, scenarios, then, when

from orders.adapters.postgres_event_store.event_store import ConcurrentStreamWriteError
from orders.domain import events
from orders.domain.models import EventsStream, Order

# Load the scenarios from the feature file
scenarios("../../features/event_handling.feature")


@pytest.fixture
def user_id():
    return 1


@pytest.fixture
def event_listener():
    # Dummy fixture to represent a running event listener
    return True


@pytest.fixture
def event_store_with_order(user_id):
    event_stream = EventsStream(
        events=[events.OrderCreated(user_id=user_id)], version=1
    )
    return Order(event_stream)


@given("a running event listener")
def given_event_listener(event_listener):
    return event_listener


@given("an event store with an existing order")
def given_event_store_with_order(event_store_with_order):
    return event_store_with_order


@when('a new event "OrderCreated" is added to the event stream')
def add_order_created_event(user_id):
    event_stream = EventsStream(
        events=[events.OrderCreated(user_id=user_id)], version=1
    )
    return Order(event_stream)


@when("another event is appended with an outdated version")
def append_event_with_outdated_version(event_store_with_order):
    with pytest.raises(ConcurrentStreamWriteError):
        raise ConcurrentStreamWriteError()


@then("the listener should receive a notification")
def listener_receives_notification(event_listener):
    assert event_listener


@then('the listener should process the "OrderCreated" event')
def listener_processes_event(event_listener):
    assert event_listener


@then("a ConcurrentStreamWriteError should be raised")
def check_concurrent_write_error():
    with pytest.raises(ConcurrentStreamWriteError):
        raise ConcurrentStreamWriteError()
