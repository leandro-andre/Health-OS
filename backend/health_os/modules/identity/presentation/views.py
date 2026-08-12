from collections.abc import Sequence

from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from health_os.modules.identity.application import UserAlreadyExistsError
from health_os.modules.identity.presentation.composition import build_register_user
from health_os.modules.identity.presentation.serializers import (
    RegisterUserRequestSerializer,
    RegisterUserResponseSerializer,
)
from health_os.shared.domain import DomainError


class RegisterUserAPIView(APIView):
    authentication_classes: Sequence[type[BaseAuthentication]] = ()
    permission_classes: Sequence[type[BasePermission]] = ()

    @extend_schema(
        operation_id="identity_register_user",
        summary="Register User",
        description="Registers a user identity.",
        request=RegisterUserRequestSerializer,
        responses={
            201: RegisterUserResponseSerializer,
            400: OpenApiResponse(
                response=inline_serializer(
                    name="RegisterUserBadRequestResponse",
                    fields={
                        "error": serializers.DictField(
                            child=serializers.CharField(),
                        ),
                    },
                ),
                description="The request payload or domain values are invalid.",
            ),
            409: OpenApiResponse(
                response=inline_serializer(
                    name="RegisterUserConflictResponse",
                    fields={
                        "error": serializers.DictField(
                            child=serializers.CharField(),
                        ),
                    },
                ),
                description="A user with the same e-mail already exists.",
            ),
        },
        tags=["Identity"],
    )
    def post(self, request: Request) -> Response:
        serializer = RegisterUserRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            output = build_register_user().execute(serializer.to_register_user_input())
        except UserAlreadyExistsError as error:
            return Response(
                {
                    "error": {
                        "code": "user_already_exists",
                        "message": str(error),
                    },
                },
                status=status.HTTP_409_CONFLICT,
            )
        except DomainError as error:
            return Response(
                {
                    "error": {
                        "code": "invalid_user",
                        "message": str(error),
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = RegisterUserResponseSerializer.from_register_user_output(
            output,
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
