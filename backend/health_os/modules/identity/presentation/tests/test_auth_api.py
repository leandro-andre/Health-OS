from datetime import timedelta
from uuid import UUID

import pytest
from django.conf import settings
from rest_framework.test import APIClient

from health_os.modules.identity.domain import Email, FullName, User, UserId
from health_os.modules.identity.infrastructure import (
    DjangoCredentialRepository,
    DjangoPasswordHasher,
    DjangoUserRepository,
    JWTTokenIssuer,
    JWTTokenSettings,
)

pytestmark = pytest.mark.django_db


def test_post_login_returns_200_with_tokens() -> None:
    user = _persist_user_with_credential(password="fake-secret")
    client = APIClient()

    response = client.post(
        "/api/v1/auth/login/",
        data={
            "email": "LEO@example.com",
            "password": "fake-secret",
        },
        format="json",
    )

    response_data = response.json()

    assert response.status_code == 200
    assert response_data["access_token"]
    assert response_data["refresh_token"]
    assert response_data["access_token"] != response_data["refresh_token"]
    assert "password" not in response_data
    assert "password_hash" not in response_data
    assert (
        JWTTokenIssuer().validate_access_token(
            response_data["access_token"],
        )["user_id"]
        == user.id
    )
    assert (
        JWTTokenIssuer().validate_refresh_token(
            response_data["refresh_token"],
        )["user_id"]
        == user.id
    )


def test_post_login_with_wrong_password_returns_401() -> None:
    _persist_user_with_credential(password="fake-secret")

    response = APIClient().post(
        "/api/v1/auth/login/",
        data={
            "email": "leo@example.com",
            "password": "wrong-secret",
        },
        format="json",
    )

    assert response.status_code == 401
    assert response.json() == _invalid_credentials_error()


def test_post_login_with_missing_user_returns_same_401_contract() -> None:
    response = APIClient().post(
        "/api/v1/auth/login/",
        data={
            "email": "missing@example.com",
            "password": "fake-secret",
        },
        format="json",
    )

    assert response.status_code == 401
    assert response.json() == _invalid_credentials_error()


def test_post_login_with_missing_credential_returns_same_401_contract() -> None:
    DjangoUserRepository().add(_user())

    response = APIClient().post(
        "/api/v1/auth/login/",
        data={
            "email": "leo@example.com",
            "password": "fake-secret",
        },
        format="json",
    )

    assert response.status_code == 401
    assert response.json() == _invalid_credentials_error()


def test_post_login_without_email_returns_400() -> None:
    response = APIClient().post(
        "/api/v1/auth/login/",
        data={"password": "fake-secret"},
        format="json",
    )

    assert response.status_code == 400


def test_post_login_without_password_returns_400() -> None:
    response = APIClient().post(
        "/api/v1/auth/login/",
        data={"email": "leo@example.com"},
        format="json",
    )

    assert response.status_code == 400


def test_post_refresh_with_valid_refresh_token_returns_new_access_token() -> None:
    user = _user()
    token_pair = JWTTokenIssuer().issue(user.id)

    response = APIClient().post(
        "/api/v1/auth/refresh/",
        data={"refresh_token": token_pair.refresh_token},
        format="json",
    )

    response_data = response.json()

    assert response.status_code == 200
    assert set(response_data) == {"access_token"}
    assert response_data["access_token"] != token_pair.refresh_token
    assert (
        JWTTokenIssuer().validate_access_token(
            response_data["access_token"],
        )["user_id"]
        == user.id
    )


def test_post_refresh_with_access_token_returns_401() -> None:
    access_token = JWTTokenIssuer().issue(UserId(UUID(int=1))).access_token

    response = APIClient().post(
        "/api/v1/auth/refresh/",
        data={"refresh_token": access_token},
        format="json",
    )

    assert response.status_code == 401
    assert response.json() == _invalid_refresh_token_error()


def test_post_refresh_with_expired_refresh_token_returns_401() -> None:
    token_issuer = JWTTokenIssuer(
        JWTTokenSettings(
            signing_key=str(settings.JWT_SIGNING_KEY),
            algorithm=str(settings.JWT_ALGORITHM),
            access_token_lifetime=timedelta(seconds=900),
            refresh_token_lifetime=timedelta(seconds=-1),
        ),
    )
    refresh_token = token_issuer.issue(UserId(UUID(int=1))).refresh_token

    response = APIClient().post(
        "/api/v1/auth/refresh/",
        data={"refresh_token": refresh_token},
        format="json",
    )

    assert response.status_code == 401
    assert response.json() == _invalid_refresh_token_error()


def test_post_refresh_with_invalid_signature_returns_401() -> None:
    token_issuer = JWTTokenIssuer(
        JWTTokenSettings(
            signing_key="wrong-key-wrong-key-wrong-key-wrong",
            algorithm="HS256",
            access_token_lifetime=timedelta(seconds=900),
            refresh_token_lifetime=timedelta(seconds=604800),
        ),
    )
    refresh_token = token_issuer.issue(UserId(UUID(int=1))).refresh_token

    response = APIClient().post(
        "/api/v1/auth/refresh/",
        data={"refresh_token": refresh_token},
        format="json",
    )

    assert response.status_code == 401
    assert response.json() == _invalid_refresh_token_error()


def test_post_refresh_without_refresh_token_returns_400() -> None:
    response = APIClient().post(
        "/api/v1/auth/refresh/",
        data={},
        format="json",
    )

    assert response.status_code == 400


def test_openapi_schema_documents_auth_operations() -> None:
    response = APIClient().get("/api/v1/schema/", HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    schema = response.json()
    login_operation = schema["paths"]["/api/v1/auth/login/"]["post"]
    refresh_operation = schema["paths"]["/api/v1/auth/refresh/"]["post"]

    assert login_operation["operationId"] == "identity_login_user"
    assert "200" in login_operation["responses"]
    assert "400" in login_operation["responses"]
    assert "401" in login_operation["responses"]
    assert refresh_operation["operationId"] == "identity_refresh_token"
    assert "200" in refresh_operation["responses"]
    assert "400" in refresh_operation["responses"]
    assert "401" in refresh_operation["responses"]


def test_register_login_refresh_end_to_end() -> None:
    client = APIClient()
    register_response = client.post(
        "/api/v1/users/",
        data={
            "email": "leo@example.com",
            "full_name": "Leandro Andre",
            "password": "fake-secret",
        },
        format="json",
    )

    login_response = client.post(
        "/api/v1/auth/login/",
        data={
            "email": "leo@example.com",
            "password": "fake-secret",
        },
        format="json",
    )
    refresh_response = client.post(
        "/api/v1/auth/refresh/",
        data={"refresh_token": login_response.json()["refresh_token"]},
        format="json",
    )

    user_id = UserId(UUID(register_response.json()["user_id"]))

    assert register_response.status_code == 201
    assert login_response.status_code == 200
    assert refresh_response.status_code == 200
    assert (
        JWTTokenIssuer().validate_access_token(
            login_response.json()["access_token"],
        )["user_id"]
        == user_id
    )
    assert (
        JWTTokenIssuer().validate_refresh_token(
            login_response.json()["refresh_token"],
        )["user_id"]
        == user_id
    )
    assert (
        JWTTokenIssuer().validate_access_token(
            refresh_response.json()["access_token"],
        )["user_id"]
        == user_id
    )


def _persist_user_with_credential(*, password: str) -> User:
    user = _user()
    DjangoUserRepository().add(user)
    DjangoCredentialRepository().add(
        user.id,
        DjangoPasswordHasher().hash(password),
    )

    return user


def _user() -> User:
    return User.restore(
        user_id=UserId(UUID(int=1)),
        email=Email("leo@example.com"),
        full_name=FullName("Leandro Andre"),
    )


def _invalid_credentials_error() -> dict[str, dict[str, str]]:
    return {
        "error": {
            "code": "invalid_credentials",
            "message": "Invalid credentials",
        },
    }


def _invalid_refresh_token_error() -> dict[str, dict[str, str]]:
    return {
        "error": {
            "code": "invalid_refresh_token",
            "message": "Invalid refresh token",
        },
    }
