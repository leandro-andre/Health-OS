from health_os.modules.identity.application import UserRepository
from health_os.modules.identity.domain import Email, User, UserId
from health_os.modules.identity.infrastructure.models import UserModel
from health_os.modules.identity.infrastructure.user_mapper import UserMapper


class DjangoUserRepository(UserRepository):
    def add(self, user: User) -> None:
        UserModel.objects.update_or_create(
            id=user.id.value,
            defaults={
                "email": user.email.value,
                "full_name": user.full_name.value,
            },
        )

    def get_by_id(self, user_id: UserId) -> User | None:
        try:
            model = UserModel.objects.get(id=user_id.value)
        except UserModel.DoesNotExist:
            return None

        return UserMapper.to_domain(model)

    def get_by_email(self, email: Email) -> User | None:
        try:
            model = UserModel.objects.get(email=email.value)
        except UserModel.DoesNotExist:
            return None

        return UserMapper.to_domain(model)
