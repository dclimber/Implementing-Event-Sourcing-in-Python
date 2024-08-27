import json
import uuid
from typing import Type

import sqlalchemy as sql
import tables
from sqlalchemy import exc

from orders.domain import events, models


class PostgreSQLEventStore(models.EventStore):

    def __init__(self, session: sql.Session):
        # we rely on SQLAlchemy, so we need Session to be passed for future usage
        self.session = session

    def load_stream(self, aggregate_uuid: uuid.UUID):
        try:
            aggregate: tables.AggregateModel = (
                self.session.query(  # we query for aggregate with its events
                    tables.AggregateModel
                )
                .options(sql.joinedload("events"))
                .filter(tables.AggregateModel.uuid == str(aggregate_uuid))
                .one()
            )
        except exc.NoResultFound:
            # we do not allow sqlalchemy-specific exception to reach our code level
            # higher
            raise domain.NotFound

        # translate all events models to proper event objects (see part 1)
        events_objects = [
            self._translate_to_object(model) for model in aggregate.events
        ]
        version = aggregate.version

        return models.EventsStream(events_objects, int(version))

    def append_to_stream(
        self,
        aggregate_uuid: uuid.UUID,
        expected_version: int | None,
        events: list[events.Event],
    ):
        # returns connection within session (same transaction state)
        connection = self.session.connection()

        if expected_version:  # an update
            stmt = (
                tables.AggregateModel.__table__.update()
                .values(version=expected_version + 1)
                .where(
                    (tables.AggregateModel.version == expected_version)
                    & (tables.AggregateModel.uuid == str(aggregate_uuid))
                )
            )
            result_proxy = connection.execute(stmt)

            if result_proxy.rowcount != 1:  # 1
                raise models.ConcurrentStreamWriteError()
        else:  # new aggregate
            stmt = tables.AggregateModel.__table__.insert().values(
                uuid=str(aggregate_uuid), version=1
            )
            connection.execute(stmt)

        for event in events:
            aggregate_uuid_str = str(aggregate_uuid)
            event_as_dict = event.as_dict()

            connection.execute(
                tables.EventModel.__table__.insert().values(
                    uuid=str(uuid.uuid4()),
                    aggregate_uuid=aggregate_uuid_str,
                    name=event.__class__.__name__,
                    data=event_as_dict,
                )
            )

            payload = json.dumps(event_as_dict)
            connection.execute(
                "NOTIFY events, "
                f"'{aggregate_uuid_str}_{event.__class__.__name__}_{payload}'"
            )

    def _translate_to_object(self, event_model: tables.EventModel) -> events.Event:
        """Translates models to event classes instances."""
        class_name = event_model.name
        kwargs = event_model.data
        # assuming `events` is a module containing all events classes we can easily get
        # desired class by its name saved along with event data
        event_class: Type[events.Event] = getattr(events, str(class_name))
        return event_class(**kwargs)
