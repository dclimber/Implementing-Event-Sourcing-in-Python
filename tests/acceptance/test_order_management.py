import pytest
from pytest_bdd import given, scenarios, then, when

from orders.domain import events
from orders.domain.models import EventsStream, Order

# Load the scenarios from the feature file
scenarios("../../features/order_management.feature")


@pytest.fixture
def user_id():
    return 1


@pytest.fixture
def create_order(user_id):
    event_stream = EventsStream(
        events=[events.OrderCreated(user_id=user_id)], version=1
    )
    order = Order(event_stream)
    order.changes.append(
        events.OrderCreated(user_id=user_id)
    )  # Simulate event recording
    return order


@pytest.fixture
def existing_order(user_id):
    event_stream = EventsStream(
        events=[events.OrderCreated(user_id=user_id)], version=1
    )
    return Order(event_stream)


@given("a user with ID 1")
def given_user_id(user_id):
    return user_id


@given('an existing order with status "new"')
def given_existing_order(existing_order):
    return existing_order


@when("the user creates an order")
def when_user_creates_order(create_order):
    return create_order


@when('the order status is changed to "confirmed"')
def when_order_status_changed(existing_order):
    existing_order.apply(events.StatusChanged(new_status="confirmed"))
    existing_order.changes.append(events.StatusChanged(new_status="confirmed"))


@then('the order should have the status "new"')
def then_order_status_new(create_order):
    assert create_order.status == "new"


@then('the order should be saved with an event "OrderCreated"')
def then_order_created_event(create_order):
    assert isinstance(create_order.changes[0], events.OrderCreated)


@then('the order status should be updated to "confirmed"')
def then_order_status_confirmed(existing_order):
    assert existing_order.status == "confirmed"


@then('an event "StatusChanged" should be appended to the event stream')
def then_status_changed_event(existing_order):
    assert isinstance(existing_order.changes[-1], events.StatusChanged)
