import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_schema_endpoint_exposes_openapi_metadata() -> None:
    client = APIClient()

    response = client.get("/api/v1/schema/", HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    assert response.json()["info"] == {
        "title": "Health OS API",
        "version": "0.1.0",
        "description": "Backend API for Health OS.",
    }


@pytest.mark.django_db
def test_schema_documents_health_check_endpoint() -> None:
    client = APIClient()

    response = client.get("/api/v1/schema/", HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    health_get = response.json()["paths"]["/api/v1/health/"]["get"]
    assert health_get["operationId"] == "system_health_check"
    assert health_get["tags"] == ["System"]
    assert "200" in health_get["responses"]
    assert "503" in health_get["responses"]


def test_docs_endpoint_is_available() -> None:
    client = APIClient()

    response = client.get("/api/v1/docs/")

    assert response.status_code == 200
