from uuid import uuid4

from health_os.modules.identity.application import (
    LoginUserInput,
    LoginUserOutput,
    RegisterUserInput,
    RegisterUserOutput,
)
from health_os.modules.identity.domain import User
from health_os.modules.identity.domain.user_id import UserId
from health_os.modules.identity.infrastructure.models import UserModel
from health_os.modules.identity.presentation import (
    LoginUserRequestSerializer,
    LoginUserResponseSerializer,
    RefreshTokenRequestSerializer,
    RefreshTokenResponseSerializer,
    RegisterUserRequestSerializer,
    RegisterUserResponseSerializer,
)


def test_login_user_request_serializer_accepts_valid_payload() -> None:
    serializer = LoginUserRequestSerializer(
        data={
            "email": "leo@example.com",
            "password": "fake-secret",
        },
    )

    assert serializer.is_valid()


def test_login_user_request_serializer_rejects_missing_email() -> None:
    serializer = LoginUserRequestSerializer(
        data={
            "password": "fake-secret",
        },
    )

    assert not serializer.is_valid()
    assert "email" in serializer.errors


def test_login_user_request_serializer_rejects_missing_password() -> None:
    serializer = LoginUserRequestSerializer(
        data={
            "email": "leo@example.com",
        },
    )

    assert not serializer.is_valid()
    assert "password" in serializer.errors


def test_login_user_request_serializer_produces_login_user_input() -> None:
    serializer = LoginUserRequestSerializer(
        data={
            "email": "LEO@example.com",
            "password": "fake-secret",
        },
    )

    assert serializer.is_valid()
    assert serializer.to_login_user_input() == LoginUserInput(
        email="LEO@example.com",
        password="fake-secret",
    )


def test_login_user_response_serializer_accepts_login_user_output() -> None:
    serializer = LoginUserResponseSerializer.from_login_user_output(
        LoginUserOutput(
            access_token="access-token",
            refresh_token="refresh-token",
        ),
    )

    assert serializer.data == {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
    }


def test_refresh_token_request_serializer_accepts_valid_payload() -> None:
    serializer = RefreshTokenRequestSerializer(
        data={
            "refresh_token": "refresh-token",
        },
    )

    assert serializer.is_valid()


def test_refresh_token_request_serializer_rejects_missing_refresh_token() -> None:
    serializer = RefreshTokenRequestSerializer(data={})

    assert not serializer.is_valid()
    assert "refresh_token" in serializer.errors


def test_refresh_token_response_serializer_contains_only_access_token() -> None:
    serializer = RefreshTokenResponseSerializer({"access_token": "access-token"})

    assert serializer.data == {"access_token": "access-token"}


def test_register_user_request_serializer_accepts_valid_payload() -> None:
    serializer = RegisterUserRequestSerializer(
        data={
            "email": "leo@example.com",
            "full_name": "Leandro Andre",
            "password": "fake-secret",
        },
    )

    assert serializer.is_valid()


def test_register_user_request_serializer_rejects_missing_email() -> None:
    serializer = RegisterUserRequestSerializer(
        data={
            "full_name": "Leandro Andre",
            "password": "fake-secret",
        },
    )

    assert not serializer.is_valid()
    assert "email" in serializer.errors


def test_register_user_request_serializer_rejects_missing_full_name() -> None:
    serializer = RegisterUserRequestSerializer(
        data={
            "email": "leo@example.com",
            "password": "fake-secret",
        },
    )

    assert not serializer.is_valid()
    assert "full_name" in serializer.errors


def test_register_user_request_serializer_produces_register_user_input() -> None:
    serializer = RegisterUserRequestSerializer(
        data={
            "email": "LEO@example.com",
            "full_name": "Leandro  Andre",
            "password": "fake-secret",
        },
    )

    assert serializer.is_valid()

    input_data = serializer.to_register_user_input()

    assert input_data == RegisterUserInput(
        email="LEO@example.com",
        full_name="Leandro  Andre",
        password="fake-secret",
    )


def test_register_user_request_serializer_rejects_missing_password() -> None:
    serializer = RegisterUserRequestSerializer(
        data={
            "email": "leo@example.com",
            "full_name": "Leandro Andre",
        },
    )

    assert not serializer.is_valid()
    assert "password" in serializer.errors


def test_response_serializer_does_not_leak_domain_or_infrastructure() -> None:
    serializer = RegisterUserResponseSerializer(
        {
            "user_id": uuid4(),
            "email": "leo@example.com",
            "full_name": "Leandro Andre",
        },
    )

    response_data = serializer.data

    assert set(response_data) == {"user_id", "email", "full_name"}
    assert not isinstance(response_data, User)
    assert not isinstance(response_data, UserModel)


def test_response_serializer_accepts_register_user_output() -> None:
    user_id = uuid4()
    serializer = RegisterUserResponseSerializer.from_register_user_output(
        RegisterUserOutput(
            user_id=UserId(user_id),
            email="leo@example.com",
            full_name="Leandro Andre",
        ),
    )

    assert serializer.data == {
        "user_id": str(user_id),
        "email": "leo@example.com",
        "full_name": "Leandro Andre",
    }
