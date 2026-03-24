from deliveries.views import DeliveryProofViewSet
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from routes.views import DeliveryPointViewSet, RouteViewSet
from tracking.views import TrackingViewSet
from users.views import AuthLoginAPIView, AuthRegisterAPIView, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("routes", RouteViewSet, basename="routes")
router.register("delivery-points", DeliveryPointViewSet, basename="delivery-points")
router.register("delivery-proofs", DeliveryProofViewSet, basename="delivery-proofs")
router.register("tracking", TrackingViewSet, basename="tracking")

urlpatterns = [
    path("", RedirectView.as_view(url="/api/", permanent=False), name="root_redirect"),
    path("admin/", admin.site.urls),
    re_path(r"^api/auth/register/?$", AuthRegisterAPIView.as_view(), name="auth_register"),
    re_path(r"^api/auth/login/?$", AuthLoginAPIView.as_view(), name="auth_login"),
    re_path(r"^api/auth/refresh/?$", TokenRefreshView.as_view(), name="auth_refresh"),
    path("api/auth/token/", AuthLoginAPIView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/", include(router.urls)),
]

if settings.DEBUG or getattr(settings, "IS_RUNSERVER", False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
