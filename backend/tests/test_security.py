import logging
import re

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.test import Client, RequestFactory, override_settings

from config.correlation import correlation_id
from config.logging import CorrelationIdFilter
from config.middleware import CorrelationIdMiddleware


def test_correlation_id_middleware_generates_response_header() -> None:
    client = Client()

    response = client.get("/api/v1/health/")

    header_value = response[settings.CORRELATION_ID_HEADER]
    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        header_value,
    )


def test_correlation_id_middleware_reuses_safe_incoming_header() -> None:
    client = Client()

    response = client.get(
        "/api/v1/health/",
        headers={
            settings.CORRELATION_ID_HEADER: "request-123",
        },
    )

    assert response[settings.CORRELATION_ID_HEADER] == "request-123"


def test_correlation_id_middleware_replaces_unsafe_incoming_header() -> None:
    client = Client()

    response = client.get(
        "/api/v1/health/",
        headers={
            settings.CORRELATION_ID_HEADER: "unsafe value",
        },
    )

    assert response[settings.CORRELATION_ID_HEADER] != "unsafe value"


def test_correlation_id_is_available_during_request_and_reset_afterwards() -> None:
    captured_correlation_ids: list[str] = []

    def get_response(request: HttpRequest) -> HttpResponse:
        captured_correlation_ids.append(correlation_id.get())
        return HttpResponse()

    middleware = CorrelationIdMiddleware(get_response)
    request = RequestFactory().get(
        "/",
        HTTP_X_CORRELATION_ID="request-456",
    )

    middleware(request)

    assert captured_correlation_ids == ["request-456"]
    assert correlation_id.get() == "-"


def test_correlation_id_logging_filter_adds_current_id() -> None:
    token = correlation_id.set("request-789")
    record = logging.LogRecord(
        name="health_os",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="message",
        args=(),
        exc_info=None,
    )

    try:
        CorrelationIdFilter().filter(record)
    finally:
        correlation_id.reset(token)

    assert vars(record)["correlation_id"] == "request-789"


def test_cors_allows_configured_origin() -> None:
    client = Client()

    with override_settings(CORS_ALLOWED_ORIGINS=["https://app.health-os.example"]):
        response = client.get(
            "/api/v1/health/",
            HTTP_ORIGIN="https://app.health-os.example",
        )

    assert response["access-control-allow-origin"] == "https://app.health-os.example"


def test_security_settings_are_configured() -> None:
    assert settings.SESSION_COOKIE_HTTPONLY is True
    assert settings.CSRF_COOKIE_HTTPONLY is True
    assert settings.X_FRAME_OPTIONS == "DENY"
    assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert settings.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
