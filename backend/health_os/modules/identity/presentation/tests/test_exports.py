import health_os.modules.identity.presentation as presentation


def test_identity_presentation_exports_public_api_helpers() -> None:
    assert presentation.__all__ == [
        "RegisterUserAPIView",
        "RegisterUserRequestSerializer",
        "RegisterUserResponseSerializer",
        "build_register_user",
    ]
