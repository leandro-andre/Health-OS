import health_os.modules.identity.application as application


def test_identity_application_exports_public_contracts() -> None:
    assert application.__all__ == [
        "CredentialRepository",
        "InvalidCredentialsError",
        "LoginUser",
        "LoginUserInput",
        "LoginUserOutput",
        "PasswordHasher",
        "RegisterUser",
        "RegisterUserInput",
        "RegisterUserOutput",
        "TokenIssuer",
        "TokenPair",
        "UserAlreadyExistsError",
        "UserRepository",
        "UserIdGenerator",
    ]
