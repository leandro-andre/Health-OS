from django.contrib.auth.hashers import check_password, make_password

from health_os.modules.identity.application import PasswordHasher


class DjangoPasswordHasher(PasswordHasher):
    def hash(self, plain_password: str) -> str:
        return make_password(plain_password)

    def verify(self, plain_password: str, password_hash: str) -> bool:
        return check_password(plain_password, password_hash)
