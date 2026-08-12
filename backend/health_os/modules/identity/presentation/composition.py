from health_os.modules.identity.application import RegisterUser
from health_os.modules.identity.infrastructure import (
    DjangoCredentialRepository,
    DjangoPasswordHasher,
    DjangoUserRepository,
)
from health_os.modules.identity.infrastructure.user_id_generator import (
    UUIDUserIdGenerator,
)
from health_os.shared.infrastructure import InMemoryEventBus


def build_register_user() -> RegisterUser:
    return RegisterUser(
        user_repository=DjangoUserRepository(),
        user_id_generator=UUIDUserIdGenerator(),
        event_bus=InMemoryEventBus(),
        password_hasher=DjangoPasswordHasher(),
        credential_repository=DjangoCredentialRepository(),
    )
