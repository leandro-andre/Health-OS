import health_os.modules.identity.domain as domain


def test_identity_domain_exports_public_value_objects() -> None:
    assert domain.__all__ == [
        "Email",
        "FullName",
        "UserId",
    ]
