from typing import Any

from rest_framework import serializers

from health_os.modules.identity.application import RegisterUserInput, RegisterUserOutput


class RegisterUserRequestSerializer(serializers.Serializer[Any]):
    email: serializers.EmailField = serializers.EmailField()
    full_name: serializers.CharField = serializers.CharField()

    def to_register_user_input(self) -> RegisterUserInput:
        return RegisterUserInput(
            email=str(self.validated_data["email"]),
            full_name=str(self.validated_data["full_name"]),
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
