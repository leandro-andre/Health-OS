from uuid import uuid4

from health_os.modules.identity.application import UserRepository
from health_os.modules.identity.domain import Email, FullName, User, UserId


class StubUserRepository:
    def __init__(self) -> None:
        self._users_by_id: dict[UserId, User] = {}
        self._users_by_email: dict[Email, User] = {}

    def add(self, user: User) -> None:
        self._users_by_id[user.id] = user
        self._users_by_email[user.email] = user

    def get_by_id(self, user_id: UserId) -> User | None:
        return self._users_by_id.get(user_id)

    def get_by_email(self, email: Email) -> User | None:
        return self._users_by_email.get(email)


def test_user_repository_accepts_expected_signature() -> None:
    repository: UserRepository = StubUserRepository()
    user_id = UserId(uuid4())
    email = Email("leo@example.com")
    user = User.restore(
        user_id=user_id,
        email=email,
        full_name=FullName("Leandro André"),
    )

    repository.add(user)

    assert repository.get_by_id(user_id) == user
    assert repository.get_by_email(email) == user
