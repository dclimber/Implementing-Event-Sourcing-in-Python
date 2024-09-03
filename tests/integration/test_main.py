import asyncio
import uuid
from urllib.parse import urlparse

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from orders.adapters.postgres_event_store.event_store import PostgreSQLEventStore
from orders.adapters.postgres_event_store.tables import Base
from orders.domain import events
from orders.main import main


def convert_sqlalchemy_dsn_to_psycopg2(dsn):
    parsed = urlparse(dsn)
    return f"dbname={parsed.path[1:]} user={parsed.username} password={parsed.password} host={parsed.hostname} port={parsed.port}"


@pytest.fixture(scope="module")
def postgres():
    with PostgresContainer("postgres:13.3") as postgres:
        engine = create_engine(postgres.get_connection_url())
        Base.metadata.create_all(engine)
        yield postgres, engine


@pytest.fixture
def session(postgres):
    _, engine = postgres
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def event_store(session):
    return PostgreSQLEventStore(session=session)


@pytest.mark.asyncio
async def test_main_event_listener(event_store, postgres):
    postgres_instance, _ = postgres
    dsn = convert_sqlalchemy_dsn_to_psycopg2(postgres_instance.get_connection_url())

    aggregate_uuid = uuid.uuid4()

    # Append an event to trigger the notification
    order_created = events.OrderCreated(user_id=1)
    event_store.append_to_stream(
        aggregate_uuid=aggregate_uuid,
        expected_version=None,
        events=[order_created],
    )

    # Start the main listener in the background with the correct DSN
    loop = asyncio.get_event_loop()
    listener_task = loop.create_task(main(dsn=dsn))  # Pass the corrected DSN here

    # Allow some time for the listener to pick up the event
    await asyncio.sleep(5)

    # At this point, the listener should have received the NOTIFY event
    # Here, you would check if the event was handled correctly

    listener_task.cancel()  # Cancel the task to clean up

    try:
        await listener_task
    except asyncio.CancelledError:
        pass  # This is expected since we're cancelling the task
