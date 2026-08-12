from inspect import getattr_static
from uuid import uuid4

from health_os.modules.identity.domain import (
    Email,
    FullName,
    User,
    UserId,
    UserRegistered,
)
from health_os.shared.domain import AggregateRoot


def test_user_is_aggregate_root() -> None:
    user = User(
        user_id=UserId(uuid4()),
        email=Email("leo@example.com"),
        full_name=FullName("Leandro André"),
    )

    assert isinstance(user, AggregateRoot)


def test_user_register_creates_user_with_received_values() -> None:
    user_id = UserId(uuid4())
    email = Email("leo@example.com")
    full_name = FullName("Leandro André")

    user = User.register(user_id=user_id, email=email, full_name=full_name)

    assert user.id == user_id
    assert user.email == email
    assert user.full_name == full_name


def test_user_exposes_id() -> None:
    user_id = UserId(uuid4())

    user = User(
        user_id=user_id,
        email=Email("leo@example.com"),
        full_name=FullName("Leandro André"),
    )

    assert user.id == user_id


def test_user_exposes_email() -> None:
    email = Email("leo@example.com")

    user = User(
        user_id=UserId(uuid4()),
        email=email,
        full_name=FullName("Leandro André"),
    )

    assert user.email == email


def test_user_exposes_full_name() -> None:
    full_name = FullName("Leandro André")

    user = User(
        user_id=UserId(uuid4()),
        email=Email("leo@example.com"),
        full_name=full_name,
    )

    assert user.full_name == full_name


def test_user_register_generates_exactly_one_user_registered_event() -> None:
    user = User.register(
        user_id=UserId(uuid4()),
        email=Email("leo@example.com"),
        full_name=FullName("Leandro André"),
    )

    assert len(user.domain_events) == 1
    assert isinstance(user.domain_events[0], UserRegistered)


def test_user_restore_creates_user_with_received_values() -> None:
    user_id = UserId(uuid4())
    email = Email("leo@example.com")
    full_name = FullName("Leandro André")

    user = User.restore(user_id=user_id, email=email, full_name=full_name)

    assert user.id == user_id
    assert user.email == email
    assert user.full_name == full_name


def test_user_restore_does_not_register_user_registered_event() -> None:
    user = User.restore(
        user_id=UserId(uuid4()),
        email=Email("leo@example.com"),
        full_name=FullName("Leandro André"),
    )

    assert user.domain_events == ()


def test_user_registered_event_has_user_id() -> None:
    user_id = UserId(uuid4())

    user = User.register(
        user_id=user_id,
        email=Email("leo@example.com"),
        full_name=FullName("Leandro André"),
    )

    event = user.domain_events[0]

    assert isinstance(event, UserRegistered)
    assert event.user_id == user_id


def test_user_registered_event_has_email() -> None:
    email = Email("leo@example.com")

    user = User.register(
        user_id=UserId(uuid4()),
        email=email,
        full_name=FullName("Leandro André"),
    )

    event = user.domain_events[0]

    assert isinstance(event, UserRegistered)
    assert event.email == email


def test_domain_events_allows_consulting_event_without_removing_it() -> None:
    user = User.register(
        user_id=UserId(uuid4()),
        email=Email("leo@example.com"),
        full_name=FullName("Leandro André"),
    )

    events = user.domain_events

    assert len(events) == 1
    assert len(user.domain_events) == 1


def test_pull_domain_events_returns_event_and_clears_collection() -> None:
    user = User.register(
        user_id=UserId(uuid4()),
        email=Email("leo@example.com"),
        full_name=FullName("Leandro André"),
    )

    events = user.pull_domain_events()

    assert len(events) == 1
    assert user.domain_events == ()


def test_clear_domain_events_clears_events() -> None:
    user = User.register(
        user_id=UserId(uuid4()),
        email=Email("leo@example.com"),
        full_name=FullName("Leandro André"),
    )

    user.clear_domain_events()

    assert user.domain_events == ()


def test_users_with_same_user_id_are_equal() -> None:
    user_id = UserId(uuid4())

    first_user = User(
        user_id=user_id,
        email=Email("first@example.com"),
        full_name=FullName("First"),
    )
    second_user = User(
        user_id=user_id,
        email=Email("second@example.com"),
        full_name=FullName("Second"),
    )

    assert first_user == second_user


def test_restored_user_preserves_aggregate_equality() -> None:
    user_id = UserId(uuid4())

    registered_user = User.register(
        user_id=user_id,
        email=Email("registered@example.com"),
        full_name=FullName("Registered"),
    )
    restored_user = User.restore(
        user_id=user_id,
        email=Email("restored@example.com"),
        full_name=FullName("Restored"),
    )

    assert restored_user == registered_user


def test_user_identity_has_no_public_setter() -> None:
    assert _property_descriptor(User, "id").fset is None


def test_user_email_has_no_public_setter() -> None:
    assert _property_descriptor(User, "email").fset is None


def test_user_full_name_has_no_public_setter() -> None:
    assert _property_descriptor(User, "full_name").fset is None


def _property_descriptor(owner: type[object], name: str) -> property:
    descriptor = getattr_static(owner, name)

    assert isinstance(descriptor, property)

    return descriptor
