from health_os.modules.identity.application import LoginUser, RegisterUser
from health_os.modules.identity.infrastructure import JWTTokenIssuer
from health_os.modules.identity.presentation import (
    build_jwt_token_issuer,
    build_login_user,
    build_register_user,
)


def test_build_register_user_creates_register_user_use_case() -> None:
    use_case = build_register_user()

    assert isinstance(use_case, RegisterUser)


def test_build_login_user_creates_login_user_use_case() -> None:
    use_case = build_login_user()

    assert isinstance(use_case, LoginUser)


def test_build_jwt_token_issuer_creates_jwt_token_issuer() -> None:
    token_issuer = build_jwt_token_issuer()

    assert isinstance(token_issuer, JWTTokenIssuer)
