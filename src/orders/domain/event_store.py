import abc
import dataclasses
import uuid

from . import events


@dataclasses.dataclass()
class EventsStream:
    events: list[events.Event]
    version: int


class EventStore(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def load_stream(self, aggregate_uuid: uuid.UUID) -> EventsStream:
        pass

    @abc.abstractmethod
    def append_to_stream(
        self,
        aggregate_uuid: uuid.UUID,
        expected_version: int | None,
        events: list[events.Event],
    ) -> None:
        pass
