from uuid import uuid4

import pytest

from health_os.modules.identity.application import (
    CredentialRepository,
    InvalidCredentialsError,
    LoginUser,
    LoginUserInput,
    PasswordHasher,
    TokenIssuer,
    TokenPair,
    UserRepository,
)
from health_os.modules.identity.domain import Email, FullName, User, UserId


class FakeUserRepository:
    def __init__(self) -> None:
        self._users_by_email: dict[Email, User] = {}

    def add(self, user: User) -> None:
        self._users_by_email[user.email] = user

    def get_by_id(self, user_id: UserId) -> User | None:
        return next(
            (user for user in self._users_by_email.values() if user.id == user_id),
            None,
        )

    def get_by_email(self, email: Email) -> User | None:
        return self._users_by_email.get(email)


class FakeCredentialRepository:
    def __init__(self) -> None:
        self._password_hashes_by_user_id: dict[UserId, str] = {}

    def add(self, user_id: UserId, password_hash: str) -> None:
        self._password_hashes_by_user_id[user_id] = password_hash

    def get_password_hash(self, user_id: UserId) -> str | None:
        return self._password_hashes_by_user_id.get(user_id)


class SpyPasswordHasher:
    def __init__(self) -> None:
        self.verify_calls: list[tuple[str, str]] = []
        self.should_verify = True

    def hash(self, plain_password: str) -> str:
        return f"hashed::{plain_password}"

    def verify(self, plain_password: str, password_hash: str) -> bool:
        self.verify_calls.append((plain_password, password_hash))
        return self.should_verify


class SpyTokenIssuer:
    def __init__(self) -> None:
        self.issued_user_ids: list[UserId] = []

    def issue(self, user_id: UserId) -> TokenPair:
        self.issued_user_ids.append(user_id)
        return TokenPair(
            access_token=f"access::{user_id.value}",
            refresh_token=f"refresh::{user_id.value}",
        )


def test_login_user_valid_credentials_verify_password_and_issue_tokens() -> None:
    user = _user()
    user_repository = FakeUserRepository()
    user_repository.add(user)
    credential_repository = FakeCredentialRepository()
    credential_repository.add(user.id, "stored-hash")
    password_hasher = SpyPasswordHasher()
    token_issuer = SpyTokenIssuer()
    use_case = LoginUser(
        user_repository=user_repository,
        credential_repository=credential_repository,
        password_hasher=password_hasher,
        token_issuer=token_issuer,
    )

    output = use_case.execute(
        LoginUserInput(email="LEO@example.com", password="fake-secret"),
    )

    assert password_hasher.verify_calls == [("fake-secret", "stored-hash")]
    assert token_issuer.issued_user_ids == [user.id]
    assert output.access_token == f"access::{user.id.value}"
    assert output.refresh_token == f"refresh::{user.id.value}"


def test_login_user_output_does_not_expose_hash_or_domain_objects() -> None:
    use_case = _use_case_with_valid_user(password_hash="stored-hash")

    output = use_case.execute(
        LoginUserInput(email="leo@example.com", password="fake-secret"),
    )

    assert not hasattr(output, "password")
    assert not hasattr(output, "password_hash")
    assert not isinstance(output, User)


def test_login_user_missing_user_raises_invalid_credentials() -> None:
    token_issuer = SpyTokenIssuer()
    use_case = _use_case(token_issuer=token_issuer)

    with pytest.raises(InvalidCredentialsError, match="Invalid credentials"):
        use_case.execute(
            LoginUserInput(email="missing@example.com", password="fake-secret"),
        )

    assert token_issuer.issued_user_ids == []


def test_login_user_missing_credential_raises_invalid_credentials() -> None:
    user = _user()
    user_repository = FakeUserRepository()
    user_repository.add(user)
    password_hasher = SpyPasswordHasher()
    token_issuer = SpyTokenIssuer()
    use_case = _use_case(
        user_repository=user_repository,
        password_hasher=password_hasher,
        token_issuer=token_issuer,
    )

    with pytest.raises(InvalidCredentialsError, match="Invalid credentials"):
        use_case.execute(
            LoginUserInput(email="leo@example.com", password="fake-secret"),
        )

    assert password_hasher.verify_calls == []
    assert token_issuer.issued_user_ids == []


def test_login_user_wrong_password_raises_invalid_credentials() -> None:
    password_hasher = SpyPasswordHasher()
    password_hasher.should_verify = False
    token_issuer = SpyTokenIssuer()
    use_case = _use_case_with_valid_user(
        password_hash="stored-hash",
        password_hasher=password_hasher,
        token_issuer=token_issuer,
    )

    with pytest.raises(InvalidCredentialsError, match="Invalid credentials"):
        use_case.execute(
            LoginUserInput(email="leo@example.com", password="wrong-secret"),
        )

    assert password_hasher.verify_calls == [("wrong-secret", "stored-hash")]
    assert token_issuer.issued_user_ids == []


def test_login_user_uses_password_hasher_contract() -> None:
    password_hasher: PasswordHasher = SpyPasswordHasher()

    use_case = _use_case(password_hasher=password_hasher)

    assert isinstance(use_case, LoginUser)


def test_login_user_uses_token_issuer_contract() -> None:
    token_issuer: TokenIssuer = SpyTokenIssuer()

    use_case = _use_case(token_issuer=token_issuer)

    assert isinstance(use_case, LoginUser)


def test_login_user_uses_repository_contracts() -> None:
    user_repository: UserRepository = FakeUserRepository()
    credential_repository: CredentialRepository = FakeCredentialRepository()

    use_case = _use_case(
        user_repository=user_repository,
        credential_repository=credential_repository,
    )

    assert isinstance(use_case, LoginUser)


def _use_case_with_valid_user(
    *,
    password_hash: str,
    password_hasher: PasswordHasher | None = None,
    token_issuer: TokenIssuer | None = None,
) -> LoginUser:
    user = _user()
    user_repository = FakeUserRepository()
    user_repository.add(user)
    credential_repository = FakeCredentialRepository()
    credential_repository.add(user.id, password_hash)

    return _use_case(
        user_repository=user_repository,
        credential_repository=credential_repository,
        password_hasher=password_hasher,
        token_issuer=token_issuer,
    )


def _use_case(
    *,
    user_repository: UserRepository | None = None,
    credential_repository: CredentialRepository | None = None,
    password_hasher: PasswordHasher | None = None,
    token_issuer: TokenIssuer | None = None,
) -> LoginUser:
    return LoginUser(
        user_repository=user_repository or FakeUserRepository(),
        credential_repository=credential_repository or FakeCredentialRepository(),
        password_hasher=password_hasher or SpyPasswordHasher(),
        token_issuer=token_issuer or SpyTokenIssuer(),
    )


def _user() -> User:
    return User.restore(
        user_id=UserId(uuid4()),
        email=Email("leo@example.com"),
        full_name=FullName("Leandro Andre"),
    )
