import dataclasses


@dataclasses.dataclass(frozen=True)
class OrderCreated:
    user_id: int


@dataclasses.dataclass(frozen=True)
class StatusChanged:
    new_status: str


class Order:
    def __init__(self, events: list):  # 1
        for event in events:
            self.apply(event)  # 2

        self.changes = []  # 3

    def apply(self, event):
        if isinstance(event, OrderCreated):
            self.user_id = event.user_id
            self.status = "new"
        elif isinstance(event, StatusChanged):
            self.status = event.new_status
        else:
            raise ValueError("Unknown event!")

    def set_status(self, new_status: str):  # 5
        if new_status not in ("new", "paid", "confirmed", "shipped"):
            raise ValueError(f"{new_status} is not a correct status!")

        event = StatusChanged(new_status)  # 6
        self.apply(event)
        self.changes.append(event)  # 7

    @classmethod
    def create(cls, user_id: int):
        initial_event = OrderCreated(user_id)
        instance = cls([initial_event])
        instance.changes = [initial_event]
        return instance
