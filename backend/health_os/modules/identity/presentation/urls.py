from django.urls import path

from health_os.modules.identity.presentation.views import (
    LoginUserAPIView,
    RefreshTokenAPIView,
    RegisterUserAPIView,
)

urlpatterns = [
    path("auth/login/", LoginUserAPIView.as_view(), name="identity-login-user"),
    path(
        "auth/refresh/",
        RefreshTokenAPIView.as_view(),
        name="identity-refresh-token",
    ),
    path("users/", RegisterUserAPIView.as_view(), name="identity-register-user"),
]
