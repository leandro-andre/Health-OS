from django.apps import AppConfig


class SystemConfig(AppConfig):  # type: ignore[misc]
    default_auto_field = "django.db.models.BigAutoField"
    name = "health_os.modules.system"
    label = "system"
    verbose_name = "System"
