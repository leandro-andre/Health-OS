from health_os.modules.identity.application import CredentialRepository
from health_os.modules.identity.domain import UserId
from health_os.modules.identity.infrastructure.models import CredentialModel


class DjangoCredentialRepository(CredentialRepository):
    def add(self, user_id: UserId, password_hash: str) -> None:
        CredentialModel.objects.create(
            user_id=user_id.value,
            password_hash=password_hash,
        )

    def get_password_hash(self, user_id: UserId) -> str | None:
        try:
            credential = CredentialModel.objects.get(user_id=user_id.value)
        except CredentialModel.DoesNotExist:
            return None

        return str(credential.password_hash)
