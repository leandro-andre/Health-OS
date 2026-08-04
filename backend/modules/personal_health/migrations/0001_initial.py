# Generated manually for Health OS 0.1.0.

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Person",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("birth_date", models.DateField()),
                (
                    "biological_sex",
                    models.CharField(
                        choices=[
                            ("female", "Female"),
                            ("male", "Male"),
                            ("intersex", "Intersex"),
                            ("unknown", "Unknown"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "default_height",
                    models.DecimalField(decimal_places=2, max_digits=5),
                ),
                (
                    "unit_system",
                    models.CharField(
                        choices=[("metric", "Metric"), ("imperial", "Imperial")],
                        default="metric",
                        max_length=20,
                    ),
                ),
                ("language", models.CharField(default="pt-BR", max_length=10)),
                (
                    "timezone",
                    models.CharField(default="America/Sao_Paulo", max_length=64),
                ),
            ],
            options={
                "verbose_name": "Person",
                "verbose_name_plural": "People",
                "ordering": ["name"],
            },
        ),
    ]
