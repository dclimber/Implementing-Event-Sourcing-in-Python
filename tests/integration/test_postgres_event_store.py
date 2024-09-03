import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from orders.adapters.postgres_event_store.event_store import PostgreSQLEventStore
from orders.adapters.postgres_event_store.tables import Base
from orders.domain import events
from orders.domain.models import ConcurrentStreamWriteError


@pytest.fixture(scope="module")
def postgres():
    with PostgresContainer("postgres:13.3") as postgres:
        engine = create_engine(postgres.get_connection_url())
        Base.metadata.create_all(engine)
        yield engine


@pytest.fixture
def session(postgres):
    Session = sessionmaker(bind=postgres)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def event_store(session):
    return PostgreSQLEventStore(session=session)


def test_append_and_load_events(event_store):
    aggregate_uuid = uuid.uuid4()

    # Create an order and append events
    order_created = events.OrderCreated(user_id=1)
    status_changed = events.StatusChanged(new_status="confirmed")

    event_store.append_to_stream(
        aggregate_uuid=aggregate_uuid,
        expected_version=None,
        events=[order_created, status_changed],
    )

    # Load the event stream back
    event_stream = event_store.load_stream(aggregate_uuid)

    assert len(event_stream.events) == 2
    assert isinstance(event_stream.events[0], events.OrderCreated)
    assert isinstance(event_stream.events[1], events.StatusChanged)
    assert event_stream.version == 2


def test_concurrent_write_error(event_store):
    aggregate_uuid = uuid.uuid4()

    # Append initial event
    order_created = events.OrderCreated(user_id=1)
    event_store.append_to_stream(
        aggregate_uuid=aggregate_uuid,
        expected_version=None,
        events=[order_created],
    )

    # Simulate concurrent write with wrong version
    status_changed = events.StatusChanged(new_status="confirmed")
    with pytest.raises(ConcurrentStreamWriteError):
        event_store.append_to_stream(
            aggregate_uuid=aggregate_uuid,
            expected_version=0,  # incorrect expected version
            events=[status_changed],
        )
