from django.urls import path

from health_os.modules.identity.presentation.views import RegisterUserAPIView

urlpatterns = [
    path("users/", RegisterUserAPIView.as_view(), name="identity-register-user"),
]
