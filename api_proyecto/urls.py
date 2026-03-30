from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from apps.empresas.views import EmpresaViewSet
from apps.pagos.views import BankTransferCreateAPIView, CashPaymentCreateAPIView, PaymentViewSet
from apps.pedidos.views import PedidoViewSet
from apps.productos.views import CarritoViewSet, ProductoViewSet
from apps.rutas.views import ParadaRutaViewSet, RutaViewSet
from apps.tracking.views import TrackingViewSet
from apps.usuarios.views import AuthLoginAPIView, AuthRegisterAPIView, UsuarioViewSet

router = DefaultRouter()
router.register("empresas", EmpresaViewSet, basename="empresas")
router.register("usuarios", UsuarioViewSet, basename="usuarios")
router.register("pedidos", PedidoViewSet, basename="pedidos")
router.register("productos", ProductoViewSet, basename="productos")
router.register("payments", PaymentViewSet, basename="payments")
router.register("rutas", RutaViewSet, basename="rutas")
router.register("paradas", ParadaRutaViewSet, basename="paradas")
router.register("tracking", TrackingViewSet, basename="tracking")
router.register("carrito", CarritoViewSet, basename="carrito")

urlpatterns = [
    path("", RedirectView.as_view(url="/api/", permanent=False), name="root_redirect"),
    path("admin/", admin.site.urls),
    path("api/auth/register/", AuthRegisterAPIView.as_view(), name="auth_register"),
    path("api/auth/login/", AuthLoginAPIView.as_view(), name="auth_login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="auth_refresh"),
    path("api/auth/verify/", TokenVerifyView.as_view(), name="auth_verify"),
    path("api/payments/transfer/", BankTransferCreateAPIView.as_view(), name="payments_transfer"),
    path("api/payments/cash/", CashPaymentCreateAPIView.as_view(), name="payments_cash"),
    path("api/", include(router.urls)),
]

if settings.DEBUG or getattr(settings, "IS_RUNSERVER", False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
