from health_os.shared.domain import DomainError, ValueObject


class Email(ValueObject):
    def __init__(self, value: str) -> None:
        normalized_value = value.strip().lower()

        if not normalized_value:
            raise DomainError("Email cannot be empty")

        if not self._is_valid(normalized_value):
            raise DomainError("Email is invalid")

        self._value = normalized_value

    @property
    def value(self) -> str:
        return self._value

    def _is_valid(self, value: str) -> bool:
        local_part, separator, domain_part = value.partition("@")

        if separator == "":
            return False

        if not local_part or not domain_part:
            return False

        if "@" in domain_part:
            return False

        return "." in domain_part
