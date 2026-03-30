from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Empresa
from .permissions import IsSuperuser
from .serializers import EmpresaSerializer


class EmpresaViewSet(viewsets.ModelViewSet):
    """Gestion de empresas (tenants)."""

    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer

    def get_permissions(self):
        if self.action in {"list", "create", "destroy"}:
            return [permissions.IsAuthenticated(), IsSuperuser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return queryset
        if getattr(user, "empresa_id", None):
            return queryset.filter(id=user.empresa_id)
        return queryset.none()

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        """Devuelve la empresa del usuario autenticado."""

        empresa = getattr(request.user, "empresa", None)
        if not empresa:
            return Response(None)
        serializer = self.get_serializer(empresa)
        return Response(serializer.data)
