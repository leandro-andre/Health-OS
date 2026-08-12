from django.apps import AppConfig


class IdentityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "health_os.modules.identity"
    label = "identity"
    verbose_name = "Identity"

    def import_models(self) -> None:
        super().import_models()

        from health_os.modules.identity.infrastructure import models  # noqa: F401
