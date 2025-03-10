import dataclasses
import functools
from typing import NoReturn

from orders.domain import event_store, events


def method_dispatch(func):
    dispatcher = functools.singledispatch(func)

    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)

    wrapper.register = dispatcher.register
    functools.update_wrapper(wrapper, func)
    return wrapper


@dataclasses.dataclass
class Order:
    user_id: int | None = None
    status: str = ""
    version: int = 0

    def __init__(self, event_stream: event_store.EventsStream):
        self.version = event_stream.version

        for event in event_stream.events:
            self.apply(event)

        self.changes = []

    @method_dispatch
    def apply(self, _: events.Event) -> NoReturn:
        raise ValueError("Unknown event!")

    @apply.register(events.OrderCreated)
    def _(self, event: events.OrderCreated) -> None:
        self.user_id = event.user_id
        self.status = "new"

    @apply.register(events.StatusChanged)
    def _(self, event: events.StatusChanged) -> None:
        self.status = event.new_status
