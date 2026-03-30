from rest_framework import permissions, viewsets
from rest_framework.response import Response

from apps.usuarios.permissions import IsAdmin

from .services import get_location, list_locations


class TrackingViewSet(viewsets.ViewSet):
    """Endpoints REST para lectura de ubicaciones en Redis."""

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Lista ubicaciones activas de la empresa (solo ADMIN)."""

        if not (request.user.is_superuser or request.user.rol == "ADMIN"):
            return Response([], status=200)

        data = list_locations(str(request.user.empresa_id))
        return Response(data)

    def retrieve(self, request, pk=None):
        """Obtiene la ubicacion de un repartidor."""

        if not (request.user.is_superuser or request.user.rol == "ADMIN" or str(request.user.id) == str(pk)):
            return Response(None, status=403)

        data = get_location(str(request.user.empresa_id), str(pk))
        return Response(data)
