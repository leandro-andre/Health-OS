from .base import *  # noqa: F403

SECRET_KEY = "django-insecure-health-os-test-key"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
