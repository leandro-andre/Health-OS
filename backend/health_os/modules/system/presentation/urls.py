from django.urls import path

from health_os.modules.system.presentation.views import HealthCheckAPIView

urlpatterns = [
    path("health/", HealthCheckAPIView.as_view(), name="system-health-check"),
]
