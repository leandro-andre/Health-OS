from dataclasses import dataclass

from health_os.modules.identity.application.credential_repository import (
    CredentialRepository,
)
from health_os.modules.identity.application.password_hasher import PasswordHasher
from health_os.modules.identity.application.token_issuer import TokenIssuer
from health_os.modules.identity.application.user_repository import UserRepository
from health_os.modules.identity.domain import Email


class InvalidCredentialsError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class LoginUserInput:
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class LoginUserOutput:
    access_token: str
    refresh_token: str


class LoginUser:
    def __init__(
        self,
        user_repository: UserRepository,
        credential_repository: CredentialRepository,
        password_hasher: PasswordHasher,
        token_issuer: TokenIssuer,
    ) -> None:
        self._user_repository = user_repository
        self._credential_repository = credential_repository
        self._password_hasher = password_hasher
        self._token_issuer = token_issuer

    def execute(self, input_data: LoginUserInput) -> LoginUserOutput:
        email = Email(input_data.email)
        user = self._user_repository.get_by_email(email)

        if user is None:
            raise InvalidCredentialsError("Invalid credentials")

        password_hash = self._credential_repository.get_password_hash(user.id)

        if password_hash is None:
            raise InvalidCredentialsError("Invalid credentials")

        if not self._password_hasher.verify(input_data.password, password_hash):
            raise InvalidCredentialsError("Invalid credentials")

        token_pair = self._token_issuer.issue(user.id)

        return LoginUserOutput(
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
        )
