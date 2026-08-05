from django.conf import settings


def test_backend_uses_sqlite_database() -> None:
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"


def test_api_foundation_dependencies_are_registered() -> None:
    assert "rest_framework" in settings.INSTALLED_APPS
    assert "drf_spectacular" in settings.INSTALLED_APPS
