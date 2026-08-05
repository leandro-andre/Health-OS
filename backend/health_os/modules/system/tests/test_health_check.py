import pytest
from rest_framework.test import APIClient

from health_os.modules.system.infrastructure.database import DjangoDatabaseHealthChecker


@pytest.mark.django_db
def test_health_check_returns_healthy_response() -> None:
    client = APIClient()

    response = client.get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "health-os-api",
        "version": "0.1.0",
        "checks": {
            "database": "healthy",
        },
    }


def test_health_check_returns_503_when_database_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(DjangoDatabaseHealthChecker, "is_healthy", lambda self: False)
    client = APIClient()

    response = client.get("/api/v1/health/")

    assert response.status_code == 503
    assert response.json() == {
        "status": "unhealthy",
        "service": "health-os-api",
        "version": "0.1.0",
        "checks": {
            "database": "unhealthy",
        },
    }
