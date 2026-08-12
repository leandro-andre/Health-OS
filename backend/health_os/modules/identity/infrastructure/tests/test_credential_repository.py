from uuid import uuid4

import pytest
from django.db import IntegrityError, transaction

from health_os.modules.identity.domain import Email, FullName, User, UserId
from health_os.modules.identity.infrastructure import DjangoCredentialRepository
from health_os.modules.identity.infrastructure.models import CredentialModel
from health_os.modules.identity.infrastructure.user_repository import (
    DjangoUserRepository,
)

pytestmark = pytest.mark.django_db


def test_add_persists_credential_for_existing_user() -> None:
    user = _persisted_user()
    repository = DjangoCredentialRepository()

    repository.add(user.id, "hashed-password")

    credential = CredentialModel.objects.get(user_id=user.id.value)
    assert credential.password_hash == "hashed-password"


def test_get_password_hash_returns_persisted_hash() -> None:
    user = _persisted_user()
    repository = DjangoCredentialRepository()
    repository.add(user.id, "hashed-password")

    password_hash = repository.get_password_hash(user.id)

    assert password_hash == "hashed-password"
    assert isinstance(password_hash, str)
    assert not isinstance(password_hash, CredentialModel)


def test_get_password_hash_returns_none_when_user_has_no_credential() -> None:
    user = _persisted_user()
    repository = DjangoCredentialRepository()

    assert repository.get_password_hash(user.id) is None


def test_second_add_for_same_user_is_rejected() -> None:
    user = _persisted_user()
    repository = DjangoCredentialRepository()
    repository.add(user.id, "first-hash")

    with pytest.raises(IntegrityError), transaction.atomic():
        repository.add(user.id, "second-hash")

    credential = CredentialModel.objects.get(user_id=user.id.value)
    assert credential.password_hash == "first-hash"


@pytest.mark.django_db(transaction=True)
def test_add_for_missing_user_is_rejected_by_database_integrity() -> None:
    repository = DjangoCredentialRepository()

    with pytest.raises(IntegrityError), transaction.atomic():
        repository.add(UserId(uuid4()), "hashed-password")


def test_plain_password_is_not_persisted_when_repository_receives_hash() -> None:
    user = _persisted_user()
    repository = DjangoCredentialRepository()

    repository.add(user.id, "hashed-password")

    credential = CredentialModel.objects.get(user_id=user.id.value)
    assert credential.password_hash == "hashed-password"
    assert credential.password_hash != "plain-password"


def _persisted_user() -> User:
    user = User.restore(
        user_id=UserId(uuid4()),
        email=Email(f"{uuid4()}@example.com"),
        full_name=FullName("Leandro Andre"),
    )
    DjangoUserRepository().add(user)

    return user
