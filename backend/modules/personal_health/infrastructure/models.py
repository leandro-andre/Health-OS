import uuid

from django.db import models


class Person(models.Model):
    class BiologicalSex(models.TextChoices):
        FEMALE = "female", "Female"
        MALE = "male", "Male"
        INTERSEX = "intersex", "Intersex"
        UNKNOWN = "unknown", "Unknown"

    class UnitSystem(models.TextChoices):
        METRIC = "metric", "Metric"
        IMPERIAL = "imperial", "Imperial"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    birth_date = models.DateField()
    biological_sex = models.CharField(
        max_length=20,
        choices=BiologicalSex.choices,
    )
    default_height = models.DecimalField(max_digits=5, decimal_places=2)
    unit_system = models.CharField(
        max_length=20,
        choices=UnitSystem.choices,
        default=UnitSystem.METRIC,
    )
    language = models.CharField(max_length=10, default="pt-BR")
    timezone = models.CharField(max_length=64, default="America/Sao_Paulo")

    class Meta:
        ordering = ["name"]
        verbose_name = "Person"
        verbose_name_plural = "People"

    def __str__(self) -> str:
        return self.name
