from django.contrib import admin

from modules.personal_health.infrastructure.models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "birth_date",
        "biological_sex",
        "default_height",
        "unit_system",
        "language",
        "timezone",
    )
    list_filter = ("biological_sex", "unit_system", "language", "timezone")
    search_fields = ("id", "name")
    ordering = ("name",)
    readonly_fields = ("id",)
