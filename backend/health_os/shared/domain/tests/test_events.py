from datetime import UTC, datetime
from uuid import UUID, uuid4

from health_os.shared.domain import DomainEvent


def test_domain_event_generates_identifier_and_timestamp() -> None:
    event = DomainEvent()

    assert isinstance(event.event_id, UUID)
    assert event.occurred_at.tzinfo == UTC


def test_domain_event_accepts_explicit_metadata() -> None:
    event_id = uuid4()
    occurred_at = datetime(2026, 8, 5, 12, 0, tzinfo=UTC)

    event = DomainEvent(event_id=event_id, occurred_at=occurred_at)

    assert event.event_id == event_id
    assert event.occurred_at == occurred_at
