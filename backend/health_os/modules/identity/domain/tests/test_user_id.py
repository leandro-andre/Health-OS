from uuid import UUID, uuid4

import pytest

from health_os.modules.identity.domain import UserId


def test_user_id_with_same_uuid_is_equal() -> None:
    value = UUID("3f9fcb0c-64cb-463d-84c4-9f5549f815aa")

    assert UserId(value) == UserId(value)


def test_user_id_with_different_uuid_is_not_equal() -> None:
    assert UserId(uuid4()) != UserId(uuid4())


def test_user_id_is_immutable() -> None:
    user_id = UserId(uuid4())

    with pytest.raises(AttributeError, match="UserId is immutable"):
        user_id._value = uuid4()


def test_user_id_exposes_value() -> None:
    value = uuid4()

    assert UserId(value).value == value
