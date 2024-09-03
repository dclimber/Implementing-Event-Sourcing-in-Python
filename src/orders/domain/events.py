import abc
import dataclasses


@dataclasses.dataclass(frozen=True)
class Event(abc.ABC):

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class OrderCreated(Event):
    user_id: int


@dataclasses.dataclass(frozen=True)
class StatusChanged(Event):
    new_status: str
