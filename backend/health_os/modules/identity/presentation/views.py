from collections.abc import Sequence

from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from health_os.modules.identity.application import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from health_os.modules.identity.infrastructure import TokenValidationError
from health_os.modules.identity.presentation.composition import (
    build_jwt_token_issuer,
    build_login_user,
    build_register_user,
)
from health_os.modules.identity.presentation.serializers import (
    LoginUserRequestSerializer,
    LoginUserResponseSerializer,
    RefreshTokenRequestSerializer,
    RefreshTokenResponseSerializer,
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


class LoginUserAPIView(APIView):
    authentication_classes: Sequence[type[BaseAuthentication]] = ()
    permission_classes: Sequence[type[BasePermission]] = ()

    @extend_schema(
        operation_id="identity_login_user",
        summary="Login User",
        description="Authenticates a user and returns access and refresh tokens.",
        request=LoginUserRequestSerializer,
        responses={
            200: LoginUserResponseSerializer,
            400: OpenApiResponse(
                response=inline_serializer(
                    name="LoginUserBadRequestResponse",
                    fields={
                        "error": serializers.DictField(
                            child=serializers.CharField(),
                        ),
                    },
                ),
                description="The request payload is invalid.",
            ),
            401: OpenApiResponse(
                response=inline_serializer(
                    name="LoginUserUnauthorizedResponse",
                    fields={
                        "error": serializers.DictField(
                            child=serializers.CharField(),
                        ),
                    },
                ),
                description="Credentials are invalid.",
            ),
        },
        tags=["Identity"],
    )
    def post(self, request: Request) -> Response:
        serializer = LoginUserRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            output = build_login_user().execute(serializer.to_login_user_input())
        except (InvalidCredentialsError, DomainError):
            return _invalid_credentials_response()

        response_serializer = LoginUserResponseSerializer.from_login_user_output(output)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class RefreshTokenAPIView(APIView):
    authentication_classes: Sequence[type[BaseAuthentication]] = ()
    permission_classes: Sequence[type[BasePermission]] = ()

    @extend_schema(
        operation_id="identity_refresh_token",
        summary="Refresh Access Token",
        description="Uses a refresh token to issue a new access token.",
        request=RefreshTokenRequestSerializer,
        responses={
            200: RefreshTokenResponseSerializer,
            400: OpenApiResponse(
                response=inline_serializer(
                    name="RefreshTokenBadRequestResponse",
                    fields={
                        "error": serializers.DictField(
                            child=serializers.CharField(),
                        ),
                    },
                ),
                description="The request payload is invalid.",
            ),
            401: OpenApiResponse(
                response=inline_serializer(
                    name="RefreshTokenUnauthorizedResponse",
                    fields={
                        "error": serializers.DictField(
                            child=serializers.CharField(),
                        ),
                    },
                ),
                description="The refresh token is invalid.",
            ),
        },
        tags=["Identity"],
    )
    def post(self, request: Request) -> Response:
        serializer = RefreshTokenRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            access_token = build_jwt_token_issuer().refresh_access_token(
                str(serializer.validated_data["refresh_token"]),
            )
        except TokenValidationError:
            return _invalid_refresh_token_response()

        response_serializer = RefreshTokenResponseSerializer(
            {"access_token": access_token},
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)


def _invalid_credentials_response() -> Response:
    return Response(
        {
            "error": {
                "code": "invalid_credentials",
                "message": "Invalid credentials",
            },
        },
        status=status.HTTP_401_UNAUTHORIZED,
    )


def _invalid_refresh_token_response() -> Response:
    return Response(
        {
            "error": {
                "code": "invalid_refresh_token",
                "message": "Invalid refresh token",
            },
        },
        status=status.HTTP_401_UNAUTHORIZED,
    )
