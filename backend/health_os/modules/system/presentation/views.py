from typing import ClassVar

from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from health_os.modules.system.application.health_check import HealthCheckService
from health_os.modules.system.infrastructure.database import DjangoDatabaseHealthChecker


class HealthCheckAPIView(APIView):  # type: ignore[misc]
    authentication_classes: ClassVar[list[type[object]]] = []
    permission_classes: ClassVar[list[type[object]]] = []

    @extend_schema(
        operation_id="system_health_check",
        summary="Health Check",
        description="Returns the operational health status of the API.",
        responses={
            200: inline_serializer(
                name="HealthCheckHealthyResponse",
                fields={
                    "status": serializers.CharField(),
                    "service": serializers.CharField(),
                    "version": serializers.CharField(),
                    "checks": serializers.DictField(
                        child=serializers.CharField(),
                    ),
                },
            ),
            503: OpenApiResponse(
                response=inline_serializer(
                    name="HealthCheckUnavailableResponse",
                    fields={
                        "status": serializers.CharField(),
                        "service": serializers.CharField(),
                        "version": serializers.CharField(),
                        "checks": serializers.DictField(
                            child=serializers.CharField(),
                        ),
                    },
                ),
                description="A required dependency is unavailable.",
            ),
        },
        tags=["System"],
    )
    def get(self, request: Request) -> Response:
        result = HealthCheckService(DjangoDatabaseHealthChecker()).execute()
        response_status = (
            status.HTTP_200_OK
            if result.is_healthy
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return Response(result.to_response_data(), status=response_status)
