from uuid import UUID

import pytest
from rest_framework.test import APIClient

from health_os.modules.identity.infrastructure import DjangoPasswordHasher
from health_os.modules.identity.infrastructure.models import CredentialModel, UserModel
from health_os.shared.domain import DomainError

pytestmark = pytest.mark.django_db


def test_post_register_user_returns_201_with_user_data() -> None:
    client = APIClient()

    response = client.post(
        "/api/v1/users/",
        data={
            "email": "LEO@example.com",
            "full_name": " Leandro  Andre ",
            "password": "fake-secret",
        },
        format="json",
    )

    response_data = response.json()

    assert response.status_code == 201
    assert UUID(response_data["user_id"])
    assert response_data["email"] == "leo@example.com"
    assert response_data["full_name"] == "Leandro Andre"
    assert "password" not in response_data
    assert "password_hash" not in response_data


def test_post_register_user_persists_user() -> None:
    client = APIClient()

    response = client.post(
        "/api/v1/users/",
        data={
            "email": "leo@example.com",
            "full_name": "Leandro Andre",
            "password": "fake-secret",
        },
        format="json",
    )

    assert response.status_code == 201
    assert UserModel.objects.filter(id=response.json()["user_id"]).exists()


def test_post_register_user_persists_normalized_user_data() -> None:
    client = APIClient()

    response = client.post(
        "/api/v1/users/",
        data={
            "email": "LEO@example.com",
            "full_name": " Leandro  Andre ",
            "password": "fake-secret",
        },
        format="json",
    )

    model = UserModel.objects.get(id=response.json()["user_id"])

    assert model.email == "leo@example.com"
    assert model.full_name == "Leandro Andre"


def test_post_register_user_persists_credential_hash() -> None:
    client = APIClient()
    plain_password = "fake-secret"

    response = client.post(
        "/api/v1/users/",
        data={
            "email": "leo@example.com",
            "full_name": "Leandro Andre",
            "password": plain_password,
        },
        format="json",
    )

    credential = CredentialModel.objects.get(user_id=response.json()["user_id"])

    assert response.status_code == 201
    assert credential.password_hash != plain_password
    assert DjangoPasswordHasher().verify(plain_password, credential.password_hash)
    assert not DjangoPasswordHasher().verify("wrong-secret", credential.password_hash)


def test_post_register_user_without_email_returns_400() -> None:
    client = APIClient()

    response = client.post(
        "/api/v1/users/",
        data={
            "full_name": "Leandro Andre",
            "password": "fake-secret",
        },
        format="json",
    )

    assert response.status_code == 400


def test_post_register_user_without_full_name_returns_400() -> None:
    client = APIClient()

    response = client.post(
        "/api/v1/users/",
        data={
            "email": "leo@example.com",
            "password": "fake-secret",
        },
        format="json",
    )

    assert response.status_code == 400


def test_post_register_user_with_invalid_email_returns_400() -> None:
    client = APIClient()

    response = client.post(
        "/api/v1/users/",
        data={
            "email": "not-an-email",
            "full_name": "Leandro Andre",
            "password": "fake-secret",
        },
        format="json",
    )

    assert response.status_code == 400


def test_post_register_user_with_invalid_full_name_returns_400() -> None:
    client = APIClient()

    response = client.post(
        "/api/v1/users/",
        data={
            "email": "leo@example.com",
            "full_name": "",
            "password": "fake-secret",
        },
        format="json",
    )

    assert response.status_code == 400


def test_post_register_user_without_password_returns_400() -> None:
    client = APIClient()

    response = client.post(
        "/api/v1/users/",
        data={
            "email": "leo@example.com",
            "full_name": "Leandro Andre",
        },
        format="json",
    )

    assert response.status_code == 400


def test_post_register_user_with_domain_error_returns_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingRegisterUser:
        def execute(self, input_data: object) -> object:
            raise DomainError("Email is invalid")

    monkeypatch.setattr(
        "health_os.modules.identity.presentation.views.build_register_user",
        lambda: FailingRegisterUser(),
    )
    client = APIClient()

    response = client.post(
        "/api/v1/users/",
        data={
            "email": "leo@example.com",
            "full_name": "Leandro Andre",
            "password": "fake-secret",
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "invalid_user",
            "message": "Email is invalid",
        },
    }


def test_post_register_user_with_existing_email_returns_409() -> None:
    client = APIClient()
    payload = {
        "email": "leo@example.com",
        "full_name": "Leandro Andre",
        "password": "fake-secret",
    }

    first_response = client.post("/api/v1/users/", data=payload, format="json")
    second_response = client.post("/api/v1/users/", data=payload, format="json")

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "error": {
            "code": "user_already_exists",
            "message": "User email already exists",
        },
    }


def test_post_register_user_with_existing_email_does_not_create_another_user() -> None:
    client = APIClient()
    payload = {
        "email": "leo@example.com",
        "full_name": "Leandro Andre",
        "password": "fake-secret",
    }

    client.post("/api/v1/users/", data=payload, format="json")
    client.post("/api/v1/users/", data=payload, format="json")

    assert UserModel.objects.count() == 1
    assert CredentialModel.objects.count() == 1


def test_register_user_route_exists_at_expected_url() -> None:
    client = APIClient()

    response = client.options("/api/v1/users/")

    assert response.status_code == 200


def test_register_user_get_returns_method_not_allowed() -> None:
    client = APIClient()

    response = client.get("/api/v1/users/")

    assert response.status_code == 405


def test_openapi_schema_documents_register_user_operation() -> None:
    client = APIClient()

    response = client.get("/api/v1/schema/", HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    post_operation = response.json()["paths"]["/api/v1/users/"]["post"]
    assert post_operation["operationId"] == "identity_register_user"
    assert post_operation["tags"] == ["Identity"]
    assert "201" in post_operation["responses"]
    assert "400" in post_operation["responses"]
    assert "409" in post_operation["responses"]
