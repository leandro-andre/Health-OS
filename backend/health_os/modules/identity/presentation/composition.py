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
        credential_repository=DjangoCredentialRepository(),
        user_id_generator=UUIDUserIdGenerator(),
        password_hasher=DjangoPasswordHasher(),
        event_bus=InMemoryEventBus(),
    )
