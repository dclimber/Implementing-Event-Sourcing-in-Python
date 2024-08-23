import dataclasses
import functools
from typing import Optional


@dataclasses.dataclass(frozen=True)
class OrderCreated:
    user_id: int


@dataclasses.dataclass(frozen=True)
class StatusChanged:
    new_status: str


def method_dispatch(func):
    dispatcher = functools.singledispatch(func)

    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)

    wrapper.register = dispatcher.register
    functools.update_wrapper(wrapper, func)
    return wrapper


@dataclasses.dataclass()
class Order:
    user_id: Optional[int] = None
    status: str = ""

    def __init__(self, events: list):  # 1
        for event in events:
            self.apply(event)  # 2

        self.changes = []  # 3

    @method_dispatch
    def apply(self, event):
        raise ValueError("Unknown event!")

    @apply.register(OrderCreated)
    def _(self, event: OrderCreated):
        self.user_id = event.user_id
        self.status = "new"

    @apply.register(StatusChanged)
    def _(self, event: StatusChanged):
        self.status = event.new_status
