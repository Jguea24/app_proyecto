from django.urls import path

from .views import LoginAPIView, RegisterAPIView

urlpatterns = [
    path("api/registro/", RegisterAPIView.as_view(), name="api_registro"),
    path("api/login/", LoginAPIView.as_view(), name="api_login"),
]