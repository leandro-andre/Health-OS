from typing import Protocol

from health_os.modules.identity.domain import UserId


class CredentialRepository(Protocol):
    def add(self, user_id: UserId, password_hash: str) -> None: ...

    def get_password_hash(self, user_id: UserId) -> str | None: ...
