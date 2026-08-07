from dataclasses import FrozenInstanceError
from datetime import UTC
from uuid import UUID, uuid4

import pytest

from health_os.modules.identity.domain import Email, UserId, UserRegistered
from health_os.shared.domain import DomainEvent


def test_user_registered_is_domain_event() -> None:
    event = UserRegistered(
        user_id=UserId(uuid4()),
        email=Email("leo@example.com"),
    )

    assert isinstance(event, DomainEvent)


def test_user_registered_exposes_payload() -> None:
    user_id = UserId(uuid4())
    email = Email("leo@example.com")

    event = UserRegistered(user_id=user_id, email=email)

    assert event.user_id == user_id
    assert event.email == email


def test_user_registered_has_event_id() -> None:
    event = UserRegistered(
        user_id=UserId(uuid4()),
        email=Email("leo@example.com"),
    )

    assert isinstance(event.event_id, UUID)


def test_user_registered_has_occurred_at_in_utc() -> None:
    event = UserRegistered(
        user_id=UserId(uuid4()),
        email=Email("leo@example.com"),
    )

    assert event.occurred_at.tzinfo == UTC


def test_user_registered_is_immutable() -> None:
    event = UserRegistered(
        user_id=UserId(uuid4()),
        email=Email("leo@example.com"),
    )

    with pytest.raises(FrozenInstanceError):
        _set_attribute(event, "email", Email("other@example.com"))


def _set_attribute(target: object, name: str, value: object) -> None:
    setattr(target, name, value)
