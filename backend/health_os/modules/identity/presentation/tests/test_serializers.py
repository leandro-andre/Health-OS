from uuid import uuid4

from health_os.modules.identity.application import RegisterUserInput, RegisterUserOutput
from health_os.modules.identity.domain import User
from health_os.modules.identity.domain.user_id import UserId
from health_os.modules.identity.infrastructure.models import UserModel
from health_os.modules.identity.presentation import (
    RegisterUserRequestSerializer,
    RegisterUserResponseSerializer,
)


def test_register_user_request_serializer_accepts_valid_payload() -> None:
    serializer = RegisterUserRequestSerializer(
        data={
            "email": "leo@example.com",
            "full_name": "Leandro Andre",
        },
    )

    assert serializer.is_valid()


def test_register_user_request_serializer_rejects_missing_email() -> None:
    serializer = RegisterUserRequestSerializer(
        data={
            "full_name": "Leandro Andre",
        },
    )

    assert not serializer.is_valid()
    assert "email" in serializer.errors


def test_register_user_request_serializer_rejects_missing_full_name() -> None:
    serializer = RegisterUserRequestSerializer(
        data={
            "email": "leo@example.com",
        },
    )

    assert not serializer.is_valid()
    assert "full_name" in serializer.errors


def test_register_user_request_serializer_produces_register_user_input() -> None:
    serializer = RegisterUserRequestSerializer(
        data={
            "email": "LEO@example.com",
            "full_name": "Leandro  Andre",
        },
    )

    assert serializer.is_valid()

    input_data = serializer.to_register_user_input()

    assert input_data == RegisterUserInput(
        email="LEO@example.com",
        full_name="Leandro  Andre",
    )


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
