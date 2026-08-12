from typing import Self

from health_os.modules.identity.domain.email import Email
from health_os.modules.identity.domain.events import UserRegistered
from health_os.modules.identity.domain.full_name import FullName
from health_os.modules.identity.domain.user_id import UserId
from health_os.shared.domain import AggregateRoot


class User(AggregateRoot[UserId]):
    def __init__(self, user_id: UserId, email: Email, full_name: FullName) -> None:
        super().__init__(user_id)
        self._email = email
        self._full_name = full_name

    @classmethod
    def register(cls, user_id: UserId, email: Email, full_name: FullName) -> Self:
        user = cls(user_id=user_id, email=email, full_name=full_name)
        user.register_domain_event(UserRegistered(user_id=user_id, email=email))

        return user

    @classmethod
    def restore(cls, user_id: UserId, email: Email, full_name: FullName) -> Self:
        return cls(user_id=user_id, email=email, full_name=full_name)

    @property
    def email(self) -> Email:
        return self._email

    @property
    def full_name(self) -> FullName:
        return self._full_name
