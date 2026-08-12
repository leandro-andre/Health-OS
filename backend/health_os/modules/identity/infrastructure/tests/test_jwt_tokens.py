from datetime import timedelta
from uuid import uuid4

import jwt
import pytest

from health_os.modules.identity.application import TokenIssuer
from health_os.modules.identity.domain import UserId
from health_os.modules.identity.infrastructure import (
    InvalidTokenError,
    JWTTokenIssuer,
    JWTTokenSettings,
    TokenExpiredError,
    WrongTokenTypeError,
)


def test_jwt_token_issuer_satisfies_token_issuer_contract() -> None:
    token_issuer: TokenIssuer = _issuer()

    assert isinstance(token_issuer, JWTTokenIssuer)


def test_issue_returns_access_and_refresh_tokens() -> None:
    token_pair = _issuer().issue(UserId(uuid4()))

    assert token_pair.access_token
    assert token_pair.refresh_token
    assert token_pair.access_token != token_pair.refresh_token


def test_access_token_contains_user_id_and_token_type() -> None:
    user_id = UserId(uuid4())
    issuer = _issuer()

    token_pair = issuer.issue(user_id)
    payload = issuer.validate_access_token(token_pair.access_token)

    assert payload["user_id"] == user_id
    assert payload["token_type"] == "access"


def test_refresh_token_contains_user_id_and_token_type() -> None:
    user_id = UserId(uuid4())
    issuer = _issuer()

    token_pair = issuer.issue(user_id)
    payload = issuer.validate_refresh_token(token_pair.refresh_token)

    assert payload["user_id"] == user_id
    assert payload["token_type"] == "refresh"


def test_tokens_expire_using_configured_lifetimes() -> None:
    issuer = _issuer(access_seconds=60, refresh_seconds=3600)
    user_id = UserId(uuid4())

    token_pair = issuer.issue(user_id)
    access_payload = issuer.validate_access_token(token_pair.access_token)
    refresh_payload = issuer.validate_refresh_token(token_pair.refresh_token)

    assert access_payload["expires_at"] - access_payload["issued_at"] == timedelta(
        seconds=60,
    )
    assert refresh_payload["expires_at"] - refresh_payload["issued_at"] == timedelta(
        seconds=3600,
    )


def test_token_with_invalid_signature_is_rejected() -> None:
    issuer = _issuer(signing_key="correct-key-correct-key-correct-key")
    token = (
        _issuer(signing_key="wrong-key-wrong-key-wrong-key-wrong")
        .issue(
            UserId(uuid4()),
        )
        .access_token
    )

    with pytest.raises(InvalidTokenError, match="Token is invalid"):
        issuer.validate_access_token(token)


def test_expired_token_is_rejected() -> None:
    issuer = _issuer(access_seconds=-1)

    token = issuer.issue(UserId(uuid4())).access_token

    with pytest.raises(TokenExpiredError, match="Token has expired"):
        issuer.validate_access_token(token)


def test_refresh_token_can_generate_new_access_token() -> None:
    user_id = UserId(uuid4())
    issuer = _issuer()

    token_pair = issuer.issue(user_id)
    access_token = issuer.refresh_access_token(token_pair.refresh_token)
    access_payload = issuer.validate_access_token(access_token)

    assert access_token != token_pair.refresh_token
    assert access_payload["user_id"] == user_id
    assert access_payload["token_type"] == "access"


def test_access_token_cannot_be_used_as_refresh_token() -> None:
    issuer = _issuer()
    access_token = issuer.issue(UserId(uuid4())).access_token

    with pytest.raises(WrongTokenTypeError, match="Token type is invalid"):
        issuer.refresh_access_token(access_token)


def test_refresh_token_cannot_be_used_as_access_token() -> None:
    issuer = _issuer()
    refresh_token = issuer.issue(UserId(uuid4())).refresh_token

    with pytest.raises(WrongTokenTypeError, match="Token type is invalid"):
        issuer.validate_access_token(refresh_token)


def test_malformed_token_is_rejected() -> None:
    with pytest.raises(InvalidTokenError, match="Token is invalid"):
        _issuer().validate_access_token("not-a-jwt")


def test_token_without_required_claims_is_rejected() -> None:
    token = jwt.encode(
        {"typ": "access"},
        "test-signing-key-test-signing-key",
        algorithm="HS256",
    )

    with pytest.raises(InvalidTokenError, match="Token is invalid"):
        _issuer().validate_access_token(token)


def _issuer(
    *,
    signing_key: str = "test-signing-key-test-signing-key",
    algorithm: str = "HS256",
    access_seconds: int = 900,
    refresh_seconds: int = 604800,
) -> JWTTokenIssuer:
    return JWTTokenIssuer(
        JWTTokenSettings(
            signing_key=signing_key,
            algorithm=algorithm,
            access_token_lifetime=timedelta(seconds=access_seconds),
            refresh_token_lifetime=timedelta(seconds=refresh_seconds),
        ),
    )
