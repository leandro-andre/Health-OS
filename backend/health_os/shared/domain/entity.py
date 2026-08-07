from typing import Generic, TypeVar

from health_os.shared.domain.events import DomainEvent

EntityId = TypeVar("EntityId")


class Entity(Generic[EntityId]):  # noqa: UP046
    def __init__(self, entity_id: EntityId) -> None:
        self._id = entity_id
        self._domain_events: list[DomainEvent] = []

    @property
    def id(self) -> EntityId:
        return self._id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False

        if type(self) is not type(other):
            return False

        return bool(self.id == other.id)

    def __hash__(self) -> int:
        return hash((type(self), self.id))

    @property
    def domain_events(self) -> tuple[DomainEvent, ...]:
        return tuple(self._domain_events)

    def register_domain_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        self._domain_events.clear()

    def pull_domain_events(self) -> tuple[DomainEvent, ...]:
        events = self.domain_events
        self.clear_domain_events()
        return events
