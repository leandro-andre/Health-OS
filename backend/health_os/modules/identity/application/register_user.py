from dataclasses import dataclass
from typing import Protocol

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


@dataclass(frozen=True, slots=True)
class RegisterUserOutput:
    user_id: UserId


class RegisterUser:
    def __init__(
        self,
        user_repository: UserRepository,
        user_id_generator: UserIdGenerator,
        event_bus: EventBus,
    ) -> None:
        self._user_repository = user_repository
        self._user_id_generator = user_id_generator
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

        self._user_repository.add(user)

        for event in user.pull_domain_events():
            self._event_bus.publish(event)

        return RegisterUserOutput(user_id=user.id)
