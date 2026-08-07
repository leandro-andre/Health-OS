from typing import Any


class ValueObject:
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        original_init = cls.__init__

        def __init__(self: ValueObject, *args: object, **kwargs: object) -> None:
            object.__setattr__(self, "_is_frozen", False)
            original_init(self, *args, **kwargs)
            object.__setattr__(self, "_is_frozen", True)

        cls.__init__ = __init__  # type: ignore[assignment, method-assign]

    def __setattr__(self, name: str, value: object) -> None:
        if getattr(self, "_is_frozen", False):
            raise AttributeError(f"{type(self).__name__} is immutable")

        object.__setattr__(self, name, value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValueObject):
            return False

        if type(self) is not type(other):
            return False

        return self._values() == other._values()

    def __hash__(self) -> int:
        return hash((type(self), self._values()))

    def _values(self) -> tuple[tuple[str, Any], ...]:
        return tuple(
            sorted(
                (name, value)
                for name, value in vars(self).items()
                if name != "_is_frozen"
            )
        )
