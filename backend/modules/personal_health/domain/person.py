from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class BiologicalSex(StrEnum):
    FEMALE = "female"
    MALE = "male"
    INTERSEX = "intersex"
    UNKNOWN = "unknown"


class UnitSystem(StrEnum):
    METRIC = "metric"
    IMPERIAL = "imperial"


@dataclass(frozen=True, slots=True)
class Person:
    id: UUID
    name: str
    birth_date: date
    biological_sex: BiologicalSex
    default_height: Decimal
    unit_system: UnitSystem
    language: str
    timezone: str
