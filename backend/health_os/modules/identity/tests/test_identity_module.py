from django.apps import apps
from django.conf import settings


def test_identity_app_config_is_registered() -> None:
    assert "health_os.modules.identity.apps.IdentityConfig" in settings.INSTALLED_APPS


def test_identity_module_can_be_loaded_by_django() -> None:
    app_config = apps.get_app_config("identity")

    assert app_config.name == "health_os.modules.identity"
    assert app_config.label == "identity"
