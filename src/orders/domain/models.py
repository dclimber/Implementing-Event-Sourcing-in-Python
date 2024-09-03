import abc
import dataclasses
import functools
import uuid
from typing import List, Optional

from orders.domain import events


@dataclasses.dataclass
class EventsStream:
    events: List[events.Event]
    version: int


class EventStore(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def load_stream(self, aggregate_uuid: uuid.UUID) -> EventsStream:
        pass

    @abc.abstractmethod
    def append_to_stream(
        self,
        aggregate_uuid: uuid.UUID,
        expected_version: Optional[int],
        events: List[events.Event],
    ) -> None:
        pass


class ConcurrentStreamWriteError(RuntimeError):
    pass


def method_dispatch(func):
    dispatcher = functools.singledispatch(func)

    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)

    wrapper.register = dispatcher.register
    functools.update_wrapper(wrapper, func)
    return wrapper


@dataclasses.dataclass
class Order:
    user_id: Optional[int] = None
    status: str = ""
    version: int = 0

    def __init__(self, event_stream: EventsStream):
        self.version = event_stream.version

        for event in event_stream.events:
            self.apply(event)

        self.changes = []

    @method_dispatch
    def apply(self, event: events.Event):
        raise ValueError("Unknown event!")

    @apply.register(events.OrderCreated)
    def _(self, event: events.OrderCreated):
        self.user_id = event.user_id
        self.status = "new"

    @apply.register(events.StatusChanged)
    def _(self, event: events.StatusChanged):
        self.status = event.new_status
