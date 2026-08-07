from health_os.shared.domain import DomainError, ValueObject


class FullName(ValueObject):
    def __init__(self, value: str) -> None:
        normalized_value = " ".join(value.strip().split())

        if not normalized_value:
            raise DomainError("Full name cannot be empty")

        self._value = normalized_value

    @property
    def value(self) -> str:
        return self._value
