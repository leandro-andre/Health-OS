from dataclasses import dataclass

from health_os.modules.identity.domain.email import Email
from health_os.modules.identity.domain.user_id import UserId
from health_os.shared.domain import DomainEvent


@dataclass(frozen=True, slots=True, kw_only=True)
class UserRegistered(DomainEvent):
    user_id: UserId
    email: Email
