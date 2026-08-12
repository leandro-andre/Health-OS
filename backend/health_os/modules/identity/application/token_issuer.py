from dataclasses import dataclass
from typing import Protocol

from health_os.modules.identity.domain import UserId


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    refresh_token: str


class TokenIssuer(Protocol):
    def issue(self, user_id: UserId) -> TokenPair: ...
