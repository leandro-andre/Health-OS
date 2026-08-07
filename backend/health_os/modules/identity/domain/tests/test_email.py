import pytest

from health_os.modules.identity.domain import Email
from health_os.shared.domain import DomainError


def test_email_normalizes_case() -> None:
    assert Email("Leo@Example.COM").value == "leo@example.com"


def test_email_removes_external_whitespace() -> None:
    assert Email("  leo@example.com  ").value == "leo@example.com"


def test_email_is_equal_after_normalization() -> None:
    assert Email("  Leo@Example.COM  ") == Email("leo@example.com")


def test_email_rejects_empty_value() -> None:
    with pytest.raises(DomainError, match="Email cannot be empty"):
        Email("   ")


@pytest.mark.parametrize(
    "value",
    [
        "leo",
        "leo@",
        "@example.com",
        "leo@example",
        "leo@@example.com",
    ],
)
def test_email_rejects_obviously_invalid_formats(value: str) -> None:
    with pytest.raises(DomainError, match="Email is invalid"):
        Email(value)


def test_email_is_immutable() -> None:
    email = Email("leo@example.com")

    with pytest.raises(AttributeError, match="Email is immutable"):
        email._value = "other@example.com"
