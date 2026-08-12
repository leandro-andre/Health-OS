import health_os.modules.identity.application as application


def test_identity_application_exports_public_contracts() -> None:
    assert application.__all__ == [
        "RegisterUser",
        "RegisterUserInput",
        "RegisterUserOutput",
        "UserAlreadyExistsError",
        "UserRepository",
        "UserIdGenerator",
    ]
