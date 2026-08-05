from dataclasses import dataclass
from typing import Protocol

SERVICE_NAME = "health-os-api"
SERVICE_VERSION = "0.1.0"


class DatabaseHealthChecker(Protocol):
    def is_healthy(self) -> bool: ...


@dataclass(frozen=True, slots=True)
class HealthCheckResult:
    status: str
    service: str
    version: str
    checks: dict[str, str]

    @property
    def is_healthy(self) -> bool:
        return self.status == "healthy"

    def to_response_data(self) -> dict[str, object]:
        return {
            "status": self.status,
            "service": self.service,
            "version": self.version,
            "checks": self.checks,
        }


class HealthCheckService:
    def __init__(self, database_checker: DatabaseHealthChecker) -> None:
        self._database_checker = database_checker

    def execute(self) -> HealthCheckResult:
        database_status = (
            "healthy" if self._database_checker.is_healthy() else "unhealthy"
        )
        status = "healthy" if database_status == "healthy" else "unhealthy"

        return HealthCheckResult(
            status=status,
            service=SERVICE_NAME,
            version=SERVICE_VERSION,
            checks={
                "database": database_status,
            },
        )
