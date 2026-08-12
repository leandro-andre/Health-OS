import pytest

from health_os.modules.identity.application import RegisterUser, RegisterUserInput
from health_os.modules.identity.domain import Email, UserRegistered
from health_os.modules.identity.infrastructure import DjangoUserRepository
from health_os.modules.identity.infrastructure.user_id_generator import (
    UUIDUserIdGenerator,
)
from health_os.shared.domain import DomainEvent
from health_os.shared.infrastructure import InMemoryEventBus

pytestmark = pytest.mark.django_db


class RecordingHandler:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def handle(self, event: DomainEvent) -> None:
        self.events.append(event)


def test_register_user_integrates_repository_database_and_event_bus() -> None:
    repository = DjangoUserRepository()
    event_bus = InMemoryEventBus()
    handler = RecordingHandler()
    event_bus.register(UserRegistered, handler)
    use_case = RegisterUser(
        user_repository=repository,
        user_id_generator=UUIDUserIdGenerator(),
        event_bus=event_bus,
    )

    output = use_case.execute(
        RegisterUserInput(
            email="LEO@example.com",
            full_name="Leandro  Andre",
        ),
    )

    restored_user = repository.get_by_id(output.user_id)

    assert restored_user is not None
    assert restored_user.id == output.user_id
    assert restored_user.email == Email("leo@example.com")
    assert restored_user.domain_events == ()
    assert len(handler.events) == 1
    event = handler.events[0]
    assert isinstance(event, UserRegistered)
    assert event.user_id == output.user_id
    assert event.email == Email("leo@example.com")
