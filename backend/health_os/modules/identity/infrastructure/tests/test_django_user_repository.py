from uuid import uuid4

import pytest
from django.db import IntegrityError, transaction

from health_os.modules.identity.domain import Email, FullName, User, UserId
from health_os.modules.identity.infrastructure import DjangoUserRepository
from health_os.modules.identity.infrastructure.models import UserModel

pytestmark = pytest.mark.django_db


def test_add_persists_user() -> None:
    user = _user(email="leo@example.com", full_name="Leandro Andre")
    repository = DjangoUserRepository()

    repository.add(user)

    model = UserModel.objects.get(id=user.id.value)
    assert model.email == "leo@example.com"
    assert model.full_name == "Leandro Andre"


def test_get_by_id_returns_domain_user() -> None:
    user = _user(email="leo@example.com", full_name="Leandro Andre")
    repository = DjangoUserRepository()
    repository.add(user)

    restored = repository.get_by_id(user.id)

    assert isinstance(restored, User)
    assert restored == user
    assert restored.id == user.id
    assert restored.email == user.email
    assert restored.full_name == user.full_name


def test_get_by_email_returns_domain_user() -> None:
    user = _user(email="leo@example.com", full_name="Leandro Andre")
    repository = DjangoUserRepository()
    repository.add(user)

    restored = repository.get_by_email(user.email)

    assert isinstance(restored, User)
    assert restored == user
    assert restored.id == user.id
    assert restored.email == user.email
    assert restored.full_name == user.full_name


def test_get_by_id_returns_none_when_user_does_not_exist() -> None:
    repository = DjangoUserRepository()

    assert repository.get_by_id(UserId(uuid4())) is None


def test_get_by_email_returns_none_when_user_does_not_exist() -> None:
    repository = DjangoUserRepository()

    assert repository.get_by_email(Email("missing@example.com")) is None


def test_round_trip_preserves_user_state_and_does_not_add_events() -> None:
    user = User.register(
        user_id=UserId(uuid4()),
        email=Email("LEO@example.com"),
        full_name=FullName("Leandro  Andre"),
    )
    repository = DjangoUserRepository()

    repository.add(user)
    model = UserModel.objects.get(id=user.id.value)
    restored = repository.get_by_id(UserId(model.id))

    assert isinstance(restored, User)
    assert restored == user
    assert restored.id == user.id
    assert restored.email == Email("leo@example.com")
    assert restored.full_name == FullName("Leandro Andre")
    assert restored.domain_events == ()
    assert len(user.domain_events) == 1


def test_duplicate_email_is_rejected_by_database_constraint() -> None:
    repository = DjangoUserRepository()
    repository.add(_user(email="leo@example.com", full_name="Leandro Andre"))

    with pytest.raises(IntegrityError), transaction.atomic():
        repository.add(_user(email="leo@example.com", full_name="Another User"))


def test_add_with_existing_id_is_rejected_without_updating_user() -> None:
    user_id = UserId(uuid4())
    original_user = User.restore(
        user_id=user_id,
        email=Email("original@example.com"),
        full_name=FullName("Original User"),
    )
    duplicate_id_user = User.restore(
        user_id=user_id,
        email=Email("updated@example.com"),
        full_name=FullName("Updated User"),
    )
    repository = DjangoUserRepository()
    repository.add(original_user)

    with pytest.raises(IntegrityError), transaction.atomic():
        repository.add(duplicate_id_user)

    model = UserModel.objects.get(id=user_id.value)
    assert model.email == "original@example.com"
    assert model.full_name == "Original User"


def _user(*, email: str, full_name: str) -> User:
    return User.restore(
        user_id=UserId(uuid4()),
        email=Email(email),
        full_name=FullName(full_name),
    )
