from django.apps import AppConfig


class PersonalHealthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.personal_health"
    label = "personal_health"
    verbose_name = "Personal Health"
