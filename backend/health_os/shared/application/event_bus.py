from typing import Protocol

from health_os.shared.domain import DomainEvent


class EventHandler(Protocol):
    def handle(self, event: DomainEvent) -> None: ...


class EventBus(Protocol):
    def register(
        self,
        event_type: type[DomainEvent],
        handler: EventHandler,
    ) -> None: ...

    def publish(self, event: DomainEvent) -> None: ...
