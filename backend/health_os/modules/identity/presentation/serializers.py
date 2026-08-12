from typing import Any

from rest_framework import serializers

from health_os.modules.identity.application import (
    LoginUserInput,
    LoginUserOutput,
    RegisterUserInput,
    RegisterUserOutput,
)


class LoginUserRequestSerializer(serializers.Serializer[Any]):
    email: serializers.EmailField = serializers.EmailField()
    password: serializers.CharField = serializers.CharField(
        trim_whitespace=False,
        write_only=True,
    )

    def to_login_user_input(self) -> LoginUserInput:
        return LoginUserInput(
            email=str(self.validated_data["email"]),
            password=str(self.validated_data["password"]),
        )


class LoginUserResponseSerializer(serializers.Serializer[Any]):
    access_token: serializers.CharField = serializers.CharField()
    refresh_token: serializers.CharField = serializers.CharField()

    @classmethod
    def from_login_user_output(
        cls,
        output: LoginUserOutput,
    ) -> "LoginUserResponseSerializer":
        return cls(
            {
                "access_token": output.access_token,
                "refresh_token": output.refresh_token,
            },
        )


class RefreshTokenRequestSerializer(serializers.Serializer[Any]):
    refresh_token: serializers.CharField = serializers.CharField(
        trim_whitespace=False,
        write_only=True,
    )


class RefreshTokenResponseSerializer(serializers.Serializer[Any]):
    access_token: serializers.CharField = serializers.CharField()


class RegisterUserRequestSerializer(serializers.Serializer[Any]):
    email: serializers.EmailField = serializers.EmailField()
    full_name: serializers.CharField = serializers.CharField()
    password: serializers.CharField = serializers.CharField(
        trim_whitespace=False,
        write_only=True,
    )

    def to_register_user_input(self) -> RegisterUserInput:
        return RegisterUserInput(
            email=str(self.validated_data["email"]),
            full_name=str(self.validated_data["full_name"]),
            password=str(self.validated_data["password"]),
        )


class RegisterUserResponseSerializer(serializers.Serializer[Any]):
    user_id: serializers.UUIDField = serializers.UUIDField()
    email: serializers.EmailField = serializers.EmailField()
    full_name: serializers.CharField = serializers.CharField()

    @classmethod
    def from_register_user_output(
        cls,
        output: RegisterUserOutput,
    ) -> "RegisterUserResponseSerializer":
        return cls(
            {
                "user_id": output.user_id.value,
                "email": output.email,
                "full_name": output.full_name,
            },
        )
