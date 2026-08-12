from health_os.modules.identity.application import PasswordHasher
from health_os.modules.identity.infrastructure import DjangoPasswordHasher


def test_django_password_hasher_generates_hash_different_from_plain_password() -> None:
    password_hasher = DjangoPasswordHasher()

    password_hash = password_hasher.hash("correct-password")

    assert password_hash != "correct-password"


def test_django_password_hasher_verifies_correct_password() -> None:
    password_hasher = DjangoPasswordHasher()

    password_hash = password_hasher.hash("correct-password")

    assert password_hasher.verify("correct-password", password_hash)


def test_django_password_hasher_rejects_wrong_password() -> None:
    password_hasher = DjangoPasswordHasher()

    password_hash = password_hasher.hash("correct-password")

    assert not password_hasher.verify("wrong-password", password_hash)


def test_django_password_hasher_implements_password_hasher_contract() -> None:
    password_hasher: PasswordHasher = DjangoPasswordHasher()

    password_hash = password_hasher.hash("correct-password")

    assert password_hasher.verify("correct-password", password_hash)
