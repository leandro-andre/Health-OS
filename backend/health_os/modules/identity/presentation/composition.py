from health_os.modules.identity.application import LoginUser, RegisterUser
from health_os.modules.identity.infrastructure import (
    DjangoCredentialRepository,
    DjangoPasswordHasher,
    DjangoUserRepository,
    JWTTokenIssuer,
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


def build_login_user() -> LoginUser:
    return LoginUser(
        user_repository=DjangoUserRepository(),
        credential_repository=DjangoCredentialRepository(),
        password_hasher=DjangoPasswordHasher(),
        token_issuer=JWTTokenIssuer(),
    )


def build_jwt_token_issuer() -> JWTTokenIssuer:
    return JWTTokenIssuer()
