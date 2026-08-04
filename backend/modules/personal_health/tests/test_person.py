from datetime import date
from decimal import Decimal
from uuid import UUID

from django.test import TestCase

from modules.personal_health.infrastructure.models import Person


class PersonModelTests(TestCase):
    def test_creates_person_with_required_fields(self):
        person = Person.objects.create(
            name="Ana Silva",
            birth_date=date(1990, 5, 20),
            biological_sex=Person.BiologicalSex.FEMALE,
            default_height=Decimal("165.50"),
            unit_system=Person.UnitSystem.METRIC,
            language="pt-BR",
            timezone="America/Sao_Paulo",
        )

        self.assertIsInstance(person.id, UUID)
        self.assertEqual(person.name, "Ana Silva")
        self.assertEqual(person.birth_date, date(1990, 5, 20))
        self.assertEqual(person.biological_sex, Person.BiologicalSex.FEMALE)
        self.assertEqual(person.default_height, Decimal("165.50"))
        self.assertEqual(person.unit_system, Person.UnitSystem.METRIC)
        self.assertEqual(person.language, "pt-BR")
        self.assertEqual(person.timezone, "America/Sao_Paulo")

    def test_string_representation_is_name(self):
        person = Person.objects.create(
            name="Bruno Costa",
            birth_date=date(1988, 1, 15),
            biological_sex=Person.BiologicalSex.MALE,
            default_height=Decimal("180.00"),
        )

        self.assertEqual(str(person), "Bruno Costa")

    def test_default_preferences_are_applied(self):
        person = Person.objects.create(
            name="Carla Souza",
            birth_date=date(1995, 9, 10),
            biological_sex=Person.BiologicalSex.UNKNOWN,
            default_height=Decimal("170.00"),
        )

        self.assertEqual(person.unit_system, Person.UnitSystem.METRIC)
        self.assertEqual(person.language, "pt-BR")
        self.assertEqual(person.timezone, "America/Sao_Paulo")
