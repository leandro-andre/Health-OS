from typing import Protocol

from health_os.modules.identity.domain import Email, User, UserId


class UserRepository(Protocol):
    def add(self, user: User) -> None: ...

    def get_by_id(self, user_id: UserId) -> User | None: ...

    def get_by_email(self, email: Email) -> User | None: ...
