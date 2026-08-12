from __future__ import annotations

from uuid import UUID

from django.db import models


class UserModel(models.Model):
    id: models.UUIDField[UUID, UUID] = models.UUIDField(
        primary_key=True,
        editable=False,
    )
    email: models.EmailField[str, str] = models.EmailField(max_length=254, unique=True)
    full_name: models.CharField[str, str] = models.CharField(max_length=255)

    class Meta:
        db_table = "identity_user"
