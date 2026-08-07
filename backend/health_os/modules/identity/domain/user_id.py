from uuid import UUID

from health_os.shared.domain import ValueObject


class UserId(ValueObject):
    def __init__(self, value: UUID) -> None:
        self._value = value

    @property
    def value(self) -> UUID:
        return self._value
