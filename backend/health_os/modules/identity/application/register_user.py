from dataclasses import dataclass
from typing import Protocol

from health_os.modules.identity.application.credential_repository import (
    CredentialRepository,
)
from health_os.modules.identity.application.password_hasher import PasswordHasher
from health_os.modules.identity.application.user_repository import UserRepository
from health_os.modules.identity.domain import Email, FullName, User, UserId
from health_os.shared.application import EventBus


class UserIdGenerator(Protocol):
    def generate(self) -> UserId: ...


class UserAlreadyExistsError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class RegisterUserInput:
    email: str
    full_name: str
    password: str


@dataclass(frozen=True, slots=True)
class RegisterUserOutput:
    user_id: UserId
    email: str
    full_name: str


class RegisterUser:
    def __init__(
        self,
        user_repository: UserRepository,
        credential_repository: CredentialRepository,
        user_id_generator: UserIdGenerator,
        password_hasher: PasswordHasher,
        event_bus: EventBus,
    ) -> None:
        self._user_repository = user_repository
        self._credential_repository = credential_repository
        self._user_id_generator = user_id_generator
        self._password_hasher = password_hasher
        self._event_bus = event_bus

    def execute(self, input_data: RegisterUserInput) -> RegisterUserOutput:
        email = Email(input_data.email)
        full_name = FullName(input_data.full_name)

        if self._user_repository.get_by_email(email) is not None:
            raise UserAlreadyExistsError("User email already exists")

        user = User.register(
            user_id=self._user_id_generator.generate(),
            email=email,
            full_name=full_name,
        )
        password_hash = self._password_hasher.hash(input_data.password)

        self._user_repository.add(user)
        self._credential_repository.add(user.id, password_hash)

        for event in user.pull_domain_events():
            self._event_bus.publish(event)

        return RegisterUserOutput(
            user_id=user.id,
            email=user.email.value,
            full_name=user.full_name.value,
        )
