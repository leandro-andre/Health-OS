import health_os.shared.domain as domain


def test_domain_exports_public_primitives() -> None:
    assert domain.__all__ == [
        "AggregateRoot",
        "DomainError",
        "DomainEvent",
        "Entity",
        "ValueObject",
    ]
