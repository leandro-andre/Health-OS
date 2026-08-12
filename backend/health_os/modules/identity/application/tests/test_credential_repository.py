from uuid import uuid4

from health_os.modules.identity.application import CredentialRepository
from health_os.modules.identity.domain import UserId


class StubCredentialRepository:
    def __init__(self) -> None:
        self._password_hashes_by_user_id: dict[UserId, str] = {}

    def add(self, user_id: UserId, password_hash: str) -> None:
        self._password_hashes_by_user_id[user_id] = password_hash

    def get_password_hash(self, user_id: UserId) -> str | None:
        return self._password_hashes_by_user_id.get(user_id)


def test_credential_repository_accepts_expected_signature() -> None:
    repository: CredentialRepository = StubCredentialRepository()
    user_id = UserId(uuid4())

    repository.add(user_id, "hashed-password")

    assert repository.get_password_hash(user_id) == "hashed-password"
    assert repository.get_password_hash(UserId(uuid4())) is None
