import pytest

from health_os.shared.domain import DomainError


def test_domain_error_is_base_domain_exception() -> None:
    with pytest.raises(DomainError, match="invalid domain state"):
        raise DomainError("invalid domain state")
