from uuid import uuid4

from health_os.modules.identity.domain import Email, FullName, User, UserId
from health_os.modules.identity.infrastructure.models import UserModel
from health_os.modules.identity.infrastructure.user_mapper import UserMapper


def test_user_mapper_converts_domain_user_to_model() -> None:
    user_id = UserId(uuid4())
    user = User.restore(
        user_id=user_id,
        email=Email("LEO@example.com"),
        full_name=FullName("Leandro  Andre"),
    )

    model = UserMapper.to_model(user)

    assert isinstance(model, UserModel)
    assert model.id == user_id.value
    assert model.email == "leo@example.com"
    assert model.full_name == "Leandro Andre"


def test_user_mapper_rehydrates_model_as_domain_user_without_events() -> None:
    user_id = uuid4()
    model = UserModel(
        id=user_id,
        email="leo@example.com",
        full_name="Leandro Andre",
    )

    user = UserMapper.to_domain(model)

    assert isinstance(user, User)
    assert user.id == UserId(user_id)
    assert user.email == Email("leo@example.com")
    assert user.full_name == FullName("Leandro Andre")
    assert user.domain_events == ()
