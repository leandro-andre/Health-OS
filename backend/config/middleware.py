from collections.abc import Callable
from typing import Any, cast
from uuid import uuid4

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from config.correlation import correlation_id


class CorrelationIdMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self._get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        header_name = settings.CORRELATION_ID_HEADER
        request_id = self._request_correlation_id(request, header_name)
        token = correlation_id.set(request_id)
        cast(Any, request).correlation_id = request_id

        try:
            response = self._get_response(request)
            response[header_name] = request_id
            return response
        finally:
            correlation_id.reset(token)

    def _request_correlation_id(self, request: HttpRequest, header_name: str) -> str:
        meta_header_name = f"HTTP_{header_name.upper().replace('-', '_')}"
        header_value = request.META.get(meta_header_name)

        if isinstance(header_value, str) and _is_safe_correlation_id(header_value):
            return header_value

        return str(uuid4())


def _is_safe_correlation_id(value: str) -> bool:
    return 0 < len(value) <= 128 and all(_is_safe_character(char) for char in value)


def _is_safe_character(char: str) -> bool:
    return char.isalnum() or char in {"-", "_", "."}
