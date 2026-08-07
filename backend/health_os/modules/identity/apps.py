from django.apps import AppConfig


class IdentityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "health_os.modules.identity"
    label = "identity"
    verbose_name = "Identity"
