from typing import Generic, TypeVar

from health_os.shared.domain.entity import Entity

EntityId = TypeVar("EntityId")


class AggregateRoot(Entity[EntityId], Generic[EntityId]):  # noqa: UP046
    pass
