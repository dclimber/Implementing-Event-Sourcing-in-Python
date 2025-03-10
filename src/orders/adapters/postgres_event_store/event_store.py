import json
import uuid
from typing import Type

import sqlalchemy as sql
from sqlalchemy import exc, text

from orders.adapters.postgres_event_store import tables
from orders.domain import event_store, events, exceptions


class PostgreSQLEventStore(event_store.EventStore):

    def __init__(self, session: sql.orm.Session):
        self.session = session

    def load_stream(self, aggregate_uuid: uuid.UUID) -> event_store.EventsStream:
        try:
            aggregate = (
                self.session.query(tables.AggregateModel)
                .options(sql.orm.joinedload(tables.AggregateModel.events))
                .filter(tables.AggregateModel.uuid == str(aggregate_uuid))
                .one()
            )
        except exc.NoResultFound:
            raise Exception("Aggregate not found")

        events_objects = [
            self._translate_to_object(event_model) for event_model in aggregate.events
        ]
        return event_store.EventsStream(
            events=events_objects, version=aggregate.version
        )

    def append_to_stream(
        self,
        aggregate_uuid: uuid.UUID,
        expected_version: int,
        events: list[events.Event],
    ) -> None:
        connection = self.session.connection()

        if expected_version is not None:
            stmt = (
                tables.AggregateModel.__table__.update()
                .values(version=expected_version + len(events))
                .where(
                    (tables.AggregateModel.version == expected_version)
                    & (tables.AggregateModel.uuid == str(aggregate_uuid))
                )
            )
            result_proxy = connection.execute(stmt)
            if result_proxy.rowcount != 1:
                raise exceptions.ConcurrentStreamWriteError()
        else:
            stmt = tables.AggregateModel.__table__.insert().values(
                uuid=str(aggregate_uuid), version=len(events)
            )
            connection.execute(stmt)

        for event in events:
            event_as_dict = event.as_dict()
            connection.execute(
                tables.EventModel.__table__.insert().values(
                    uuid=str(uuid.uuid4()),
                    aggregate_uuid=str(aggregate_uuid),
                    name=event.__class__.__name__,
                    data=event_as_dict,
                )
            )
            payload = json.dumps(event_as_dict)
            notify_stmt = text(f"NOTIFY events, :payload")
            connection.execute(
                notify_stmt,
                {
                    "payload": (
                        f"{str(aggregate_uuid)}_{event.__class__.__name__}"
                        f"_{payload}"
                    )
                },
            )

    def _translate_to_object(self, event_model: tables.EventModel) -> events.Event:
        event_class: Type[events.Event] = getattr(events, event_model.name)
        return event_class(**event_model.data)
