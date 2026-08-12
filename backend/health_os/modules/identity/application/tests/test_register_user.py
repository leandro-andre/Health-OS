from uuid import uuid4

import pytest

from health_os.modules.identity.application import (
    RegisterUser,
    RegisterUserInput,
    UserAlreadyExistsError,
    CredentialRepository,
    PasswordHasher,
    UserIdGenerator,
    UserRepository,
)
from health_os.modules.identity.domain import (
    Email,
    FullName,
    User,
    UserId,
    UserRegistered,
)
from health_os.shared.application import EventBus, EventHandler
from health_os.shared.domain import DomainEvent


class StubUserIdGenerator:
    def __init__(self, user_id: UserId) -> None:
        self._user_id = user_id
        self.generate_calls = 0

    def generate(self) -> UserId:
        self.generate_calls += 1
        return self._user_id


class SpyUserRepository:
    def __init__(self, operation_log: list[str] | None = None) -> None:
        self.added_users: list[User] = []
        self._users_by_email: dict[Email, User] = {}
        self._operation_log = operation_log
        self.should_fail_on_add = False

    def add(self, user: User) -> None:
        if self._operation_log is not None:
            self._operation_log.append("repository.add")

        if self.should_fail_on_add:
            raise RuntimeError("repository failed")

        self.added_users.append(user)
        self._users_by_email[user.email] = user

    def get_by_id(self, user_id: UserId) -> User | None:
        return next((user for user in self.added_users if user.id == user_id), None)

    def get_by_email(self, email: Email) -> User | None:
        return self._users_by_email.get(email)

    def add_existing(self, user: User) -> None:
        self._users_by_email[user.email] = user


class SpyCredentialRepository:
    def __init__(self, operation_log: list[str] | None = None) -> None:
        self.added_credentials: list[tuple[UserId, str]] = []
        self._operation_log = operation_log
        self.should_fail_on_add = False

    def add(self, user_id: UserId, password_hash: str) -> None:
        if self._operation_log is not None:
            self._operation_log.append("credential_repository.add")

        if self.should_fail_on_add:
            raise RuntimeError("credential repository failed")

        self.added_credentials.append((user_id, password_hash))

    def get_password_hash(self, user_id: UserId) -> str | None:
        return next(
            (
                password_hash
                for credential_user_id, password_hash in self.added_credentials
                if credential_user_id == user_id
            ),
            None,
        )


class SpyPasswordHasher:
    def __init__(self) -> None:
        self.hash_calls: list[str] = []
        self.should_fail = False

    def hash(self, plain_password: str) -> str:
        if self.should_fail:
            raise RuntimeError("password hashing failed")

        self.hash_calls.append(plain_password)
        return f"hashed:{plain_password}"

    def verify(self, plain_password: str, password_hash: str) -> bool:
        return password_hash == self.hash(plain_password)


class SpyEventBus:
    def __init__(self, operation_log: list[str] | None = None) -> None:
        self.published_events: list[DomainEvent] = []
        self._handlers: list[EventHandler] = []
        self._operation_log = operation_log

    def register(
        self,
        event_type: type[DomainEvent],
        handler: EventHandler,
    ) -> None:
        self._handlers.append(handler)

    def publish(self, event: DomainEvent) -> None:
        if self._operation_log is not None:
            self._operation_log.append("event_bus.publish")

        for handler in self._handlers:
            handler.handle(event)

        self.published_events.append(event)


class FailingHandler:
    def handle(self, event: DomainEvent) -> None:
        raise RuntimeError("handler failed")


def test_register_user_persists_valid_user() -> None:
    user_id = UserId(uuid4())
    repository = SpyUserRepository()
    use_case = _use_case(user_id=user_id, repository=repository)

    output = use_case.execute(
        RegisterUserInput(
            email="LEO@example.com",
            full_name="Leandro  Andre",
            password="plain-password",
        ),
    )

    assert output.user_id == user_id
    assert output.email == "leo@example.com"
    assert output.full_name == "Leandro Andre"
    assert len(repository.added_users) == 1
    assert repository.added_users[0].id == user_id
    assert repository.added_users[0].email == Email("leo@example.com")
    assert repository.added_users[0].full_name == FullName("Leandro Andre")


def test_register_user_generates_user_id() -> None:
    user_id_generator = StubUserIdGenerator(UserId(uuid4()))
    use_case = RegisterUser(
        user_repository=SpyUserRepository(),
        user_id_generator=user_id_generator,
        event_bus=SpyEventBus(),
        password_hasher=SpyPasswordHasher(),
        credential_repository=SpyCredentialRepository(),
    )

    use_case.execute(
        RegisterUserInput(
            email="leo@example.com",
            full_name="Leandro",
            password="plain-password",
        ),
    )

    assert user_id_generator.generate_calls == 1


def test_register_user_publishes_user_registered_after_persistence() -> None:
    user_id = UserId(uuid4())
    operation_log: list[str] = []
    repository = SpyUserRepository(operation_log)
    event_bus = SpyEventBus(operation_log)
    use_case = _use_case(user_id=user_id, repository=repository, event_bus=event_bus)

    use_case.execute(_input())

    assert operation_log == [
        "repository.add",
        "credential_repository.add",
        "event_bus.publish",
    ]
    assert len(event_bus.published_events) == 1
    event = event_bus.published_events[0]
    assert isinstance(event, UserRegistered)
    assert event.user_id == user_id
    assert event.email == Email("leo@example.com")


def test_register_user_does_not_publish_event_when_repository_add_fails() -> None:
    repository = SpyUserRepository()
    repository.should_fail_on_add = True
    credential_repository = SpyCredentialRepository()
    event_bus = SpyEventBus()
    use_case = _use_case(
        repository=repository,
        event_bus=event_bus,
        credential_repository=credential_repository,
    )

    with pytest.raises(RuntimeError, match="repository failed"):
        use_case.execute(_input())

    assert credential_repository.added_credentials == []
    assert event_bus.published_events == []


def test_register_user_does_not_persist_or_publish_when_email_already_exists() -> None:
    repository = SpyUserRepository()
    repository.add_existing(
        User.restore(
            user_id=UserId(uuid4()),
            email=Email("leo@example.com"),
            full_name=FullName("Existing User"),
        ),
    )
    event_bus = SpyEventBus()

    user_id_generator = StubUserIdGenerator(UserId(uuid4()))
    use_case = RegisterUser(
        user_repository=repository,
        user_id_generator=user_id_generator,
        event_bus=event_bus,
        password_hasher=SpyPasswordHasher(),
        credential_repository=SpyCredentialRepository(),
    )

    with pytest.raises(UserAlreadyExistsError, match="User email already exists"):
        use_case.execute(_input())

    assert repository.added_users == []
    assert event_bus.published_events == []
    assert user_id_generator.generate_calls == 0


def test_register_user_propagates_event_bus_handler_exception() -> None:
    event_bus = SpyEventBus()
    event_bus.register(UserRegistered, FailingHandler())
    use_case = _use_case(event_bus=event_bus)

    with pytest.raises(RuntimeError, match="handler failed"):
        use_case.execute(_input())


def test_register_user_clears_aggregate_events_after_successful_publication() -> None:
    repository = SpyUserRepository()
    event_bus = SpyEventBus()
    use_case = _use_case(repository=repository, event_bus=event_bus)

    use_case.execute(_input())

    assert repository.added_users[0].domain_events == ()


def test_register_user_depends_on_event_bus_contract() -> None:
    event_bus: EventBus = SpyEventBus()

    use_case = _use_case(event_bus=event_bus)

    assert isinstance(use_case, RegisterUser)


def test_register_user_hashes_password_and_persists_only_hash() -> None:
    user_id = UserId(uuid4())
    password_hasher = SpyPasswordHasher()
    credential_repository = SpyCredentialRepository()
    use_case = _use_case(
        user_id=user_id,
        password_hasher=password_hasher,
        credential_repository=credential_repository,
    )

    use_case.execute(_input(password="plain-password"))

    assert password_hasher.hash_calls == ["plain-password"]
    assert credential_repository.added_credentials == [
        (user_id, "hashed:plain-password"),
    ]
    assert credential_repository.added_credentials[0][1] != "plain-password"


def test_register_user_aggregate_does_not_contain_password() -> None:
    repository = SpyUserRepository()
    use_case = _use_case(repository=repository)

    use_case.execute(_input(password="plain-password"))

    user = repository.added_users[0]
    assert not hasattr(user, "password")
    assert not hasattr(user, "password_hash")


def test_register_user_does_not_hash_or_persist_when_email_already_exists() -> None:
    repository = SpyUserRepository()
    repository.add_existing(
        User.restore(
            user_id=UserId(uuid4()),
            email=Email("leo@example.com"),
            full_name=FullName("Existing User"),
        ),
    )
    password_hasher = SpyPasswordHasher()
    credential_repository = SpyCredentialRepository()
    event_bus = SpyEventBus()
    user_id_generator = StubUserIdGenerator(UserId(uuid4()))
    use_case = RegisterUser(
        user_repository=repository,
        user_id_generator=user_id_generator,
        event_bus=event_bus,
        password_hasher=password_hasher,
        credential_repository=credential_repository,
    )

    with pytest.raises(UserAlreadyExistsError, match="User email already exists"):
        use_case.execute(_input())

    assert user_id_generator.generate_calls == 0
    assert password_hasher.hash_calls == []
    assert repository.added_users == []
    assert credential_repository.added_credentials == []
    assert event_bus.published_events == []


def test_register_user_does_not_persist_or_publish_when_hashing_fails() -> None:
    repository = SpyUserRepository()
    password_hasher = SpyPasswordHasher()
    password_hasher.should_fail = True
    credential_repository = SpyCredentialRepository()
    event_bus = SpyEventBus()
    use_case = _use_case(
        repository=repository,
        password_hasher=password_hasher,
        credential_repository=credential_repository,
        event_bus=event_bus,
    )

    with pytest.raises(RuntimeError, match="password hashing failed"):
        use_case.execute(_input())

    assert repository.added_users == []
    assert credential_repository.added_credentials == []
    assert event_bus.published_events == []


def test_register_user_does_not_publish_when_credential_repository_fails() -> None:
    credential_repository = SpyCredentialRepository()
    credential_repository.should_fail_on_add = True
    event_bus = SpyEventBus()
    use_case = _use_case(
        credential_repository=credential_repository,
        event_bus=event_bus,
    )

    with pytest.raises(RuntimeError, match="credential repository failed"):
        use_case.execute(_input())

    assert event_bus.published_events == []


def _use_case(
    *,
    user_id: UserId | None = None,
    repository: UserRepository | None = None,
    event_bus: EventBus | None = None,
    password_hasher: PasswordHasher | None = None,
    credential_repository: CredentialRepository | None = None,
) -> RegisterUser:
    generated_user_id = user_id or UserId(uuid4())
    user_id_generator: UserIdGenerator = StubUserIdGenerator(generated_user_id)
    return RegisterUser(
        user_repository=repository or SpyUserRepository(),
        user_id_generator=user_id_generator,
        event_bus=event_bus or SpyEventBus(),
        password_hasher=password_hasher or SpyPasswordHasher(),
        credential_repository=credential_repository or SpyCredentialRepository(),
    )


def _input(*, password: str = "plain-password") -> RegisterUserInput:
    return RegisterUserInput(
        email="leo@example.com",
        full_name="Leandro",
        password=password,
    )
