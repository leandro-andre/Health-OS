from health_os.modules.identity.application import RegisterUser
from health_os.modules.identity.presentation import build_register_user


def test_build_register_user_creates_register_user_use_case() -> None:
    use_case = build_register_user()

    assert isinstance(use_case, RegisterUser)
