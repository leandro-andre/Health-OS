from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal, TypedDict
from uuid import UUID

import jwt
from django.conf import settings

from health_os.modules.identity.application import TokenIssuer, TokenPair
from health_os.modules.identity.domain import UserId

TokenType = Literal["access", "refresh"]


class TokenValidationError(Exception):
    pass


class TokenExpiredError(TokenValidationError):
    pass


class InvalidTokenError(TokenValidationError):
    pass


class WrongTokenTypeError(TokenValidationError):
    pass


class TokenPayload(TypedDict):
    user_id: UserId
    token_type: TokenType
    issued_at: datetime
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class JWTTokenSettings:
    signing_key: str
    algorithm: str
    access_token_lifetime: timedelta
    refresh_token_lifetime: timedelta

    @classmethod
    def from_django_settings(cls) -> "JWTTokenSettings":
        return cls(
            signing_key=str(settings.JWT_SIGNING_KEY),
            algorithm=str(settings.JWT_ALGORITHM),
            access_token_lifetime=timedelta(
                seconds=int(settings.JWT_ACCESS_TOKEN_SECONDS),
            ),
            refresh_token_lifetime=timedelta(
                seconds=int(settings.JWT_REFRESH_TOKEN_SECONDS),
            ),
        )


class JWTTokenIssuer(TokenIssuer):
    def __init__(self, token_settings: JWTTokenSettings | None = None) -> None:
        self._token_settings = token_settings or JWTTokenSettings.from_django_settings()

    def issue(self, user_id: UserId) -> TokenPair:
        return TokenPair(
            access_token=self._encode(user_id, "access"),
            refresh_token=self._encode(user_id, "refresh"),
        )

    def validate_access_token(self, token: str) -> TokenPayload:
        return self._decode(token, expected_token_type="access")

    def validate_refresh_token(self, token: str) -> TokenPayload:
        return self._decode(token, expected_token_type="refresh")

    def refresh_access_token(self, refresh_token: str) -> str:
        payload = self.validate_refresh_token(refresh_token)

        return self._encode(payload["user_id"], "access")

    def _encode(self, user_id: UserId, token_type: TokenType) -> str:
        issued_at = datetime.now(tz=UTC)
        lifetime = (
            self._token_settings.access_token_lifetime
            if token_type == "access"
            else self._token_settings.refresh_token_lifetime
        )
        expires_at = issued_at + lifetime
        payload = {
            "sub": str(user_id.value),
            "iat": issued_at,
            "exp": expires_at,
            "typ": token_type,
        }

        return str(
            jwt.encode(
                payload,
                self._token_settings.signing_key,
                algorithm=self._token_settings.algorithm,
            ),
        )

    def _decode(
        self,
        token: str,
        *,
        expected_token_type: TokenType,
    ) -> TokenPayload:
        try:
            payload = jwt.decode(
                token,
                self._token_settings.signing_key,
                algorithms=[self._token_settings.algorithm],
            )
        except jwt.ExpiredSignatureError as error:
            raise TokenExpiredError("Token has expired") from error
        except jwt.InvalidTokenError as error:
            raise InvalidTokenError("Token is invalid") from error

        token_type = payload.get("typ")
        if token_type != expected_token_type:
            raise WrongTokenTypeError("Token type is invalid")

        try:
            user_id = UserId(UUID(str(payload["sub"])))
            issued_at = datetime.fromtimestamp(int(payload["iat"]), tz=UTC)
            expires_at = datetime.fromtimestamp(int(payload["exp"]), tz=UTC)
        except (KeyError, TypeError, ValueError) as error:
            raise InvalidTokenError("Token is invalid") from error

        return {
            "user_id": user_id,
            "token_type": expected_token_type,
            "issued_at": issued_at,
            "expires_at": expires_at,
        }
