import pytest

from health_os.modules.identity.domain import FullName
from health_os.shared.domain import DomainError


def test_full_name_removes_external_whitespace() -> None:
    assert FullName("  Leandro André  ").value == "Leandro André"


def test_full_name_normalizes_multiple_internal_spaces() -> None:
    assert FullName("Leandro   André").value == "Leandro André"


def test_full_name_is_equal_after_normalization() -> None:
    assert FullName("  Leandro   André  ") == FullName("Leandro André")


def test_full_name_rejects_empty_value() -> None:
    with pytest.raises(DomainError, match="Full name cannot be empty"):
        FullName("   ")


def test_full_name_accepts_single_word() -> None:
    assert FullName("Leandro").value == "Leandro"


def test_full_name_is_immutable() -> None:
    full_name = FullName("Leandro André")

    with pytest.raises(AttributeError, match="FullName is immutable"):
        full_name._value = "Other Name"
