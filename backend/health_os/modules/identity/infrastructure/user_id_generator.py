from uuid import uuid4

from health_os.modules.identity.application import UserIdGenerator
from health_os.modules.identity.domain import UserId


class UUIDUserIdGenerator(UserIdGenerator):
    def generate(self) -> UserId:
        return UserId(uuid4())
