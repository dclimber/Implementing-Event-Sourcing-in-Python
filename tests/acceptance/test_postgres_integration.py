import uuid

import pytest
from pytest_bdd import given, scenarios, then, when

from orders.adapters.postgres_event_store.event_store import PostgreSQLEventStore
from orders.domain import events

# Load the scenarios from the feature file
scenarios("../../features/postgres_integration.feature")


@pytest.fixture(scope="module")
def postgres():
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:13.3") as postgres:
        yield postgres


@pytest.fixture
def session(postgres):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from orders.adapters.postgres_event_store.tables import Base

    engine = create_engine(postgres.get_connection_url())
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def postgres_database(postgres):
    return postgres


@given("a PostgreSQL database")
def given_postgres_database(postgres_database):
    return postgres_database


@when("events are stored in the database", target_fixture="aggregate_uuid")
def when_events_stored_in_db(session):
    event_store = PostgreSQLEventStore(session)
    aggregate_uuid = uuid.uuid4()
    order_created = events.OrderCreated(user_id=1)
    event_store.append_to_stream(
        aggregate_uuid=aggregate_uuid,
        expected_version=None,
        events=[order_created],
    )
    return aggregate_uuid


@then("the events should be retrievable from the database")
def then_retrieve_events_from_db(session, aggregate_uuid):
    event_store = PostgreSQLEventStore(session)
    event_stream = event_store.load_stream(aggregate_uuid)
    assert len(event_stream.events) > 0


@then("the version of the event stream should match the number of stored events")
def then_check_event_stream_version(session, aggregate_uuid):
    event_store = PostgreSQLEventStore(session)
    event_stream = event_store.load_stream(aggregate_uuid)
    assert event_stream.version == len(event_stream.events)
