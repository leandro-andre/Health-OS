from health_os.modules.identity.domain import Email, FullName, User, UserId
from health_os.modules.identity.infrastructure.models import UserModel


class UserMapper:
    @staticmethod
    def to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id.value,
            email=user.email.value,
            full_name=user.full_name.value,
        )

    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User.restore(
            user_id=UserId(model.id),
            email=Email(model.email),
            full_name=FullName(model.full_name),
        )
