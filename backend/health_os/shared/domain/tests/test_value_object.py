import pytest

from health_os.shared.domain import ValueObject


class SampleValueObject(ValueObject):
    def __init__(self, amount: int, currency: str) -> None:
        self.amount = amount
        self.currency = currency


class OtherSampleValueObject(ValueObject):
    def __init__(self, amount: int, currency: str) -> None:
        self.amount = amount
        self.currency = currency


def test_value_objects_with_same_values_are_equal() -> None:
    assert SampleValueObject(10, "BRL") == SampleValueObject(10, "BRL")


def test_value_objects_with_different_values_are_not_equal() -> None:
    assert SampleValueObject(10, "BRL") != SampleValueObject(20, "BRL")


def test_value_objects_of_different_concrete_types_are_not_equal() -> None:
    assert SampleValueObject(10, "BRL") != OtherSampleValueObject(10, "BRL")


def test_value_object_is_immutable() -> None:
    value_object = SampleValueObject(10, "BRL")

    with pytest.raises(AttributeError, match="SampleValueObject is immutable"):
        value_object.amount = 20


def test_value_object_can_be_used_in_set() -> None:
    value_objects = {
        SampleValueObject(10, "BRL"),
        SampleValueObject(10, "BRL"),
        SampleValueObject(20, "BRL"),
    }

    assert len(value_objects) == 2
