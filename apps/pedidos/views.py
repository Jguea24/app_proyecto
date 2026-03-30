from math import asin, cos, radians, sin, sqrt

import requests
from django.conf import settings
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Pedido
from .permissions import IsAdminOrReadOnlySameEmpresa
from .serializers import PedidoSerializer


def _haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return r * c


class PedidoViewSet(viewsets.ModelViewSet):
    """CRUD de pedidos por empresa."""

    queryset = Pedido.objects.select_related("empresa")
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnlySameEmpresa]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return queryset
        return queryset.filter(empresa_id=user.empresa_id)

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa)

    @action(detail=False, methods=["post"], url_path="quote")
    def quote(self, request):
        """Cotiza distancia/tiempo entre origen y destino."""

        try:
            origen_lat = float(request.data.get("origen_latitud"))
            origen_lng = float(request.data.get("origen_longitud"))
            destino_lat = float(request.data.get("destino_latitud"))
            destino_lng = float(request.data.get("destino_longitud"))
        except (TypeError, ValueError):
            raise ValidationError(
                {
                    "origen": "Debe enviar origen_latitud/origen_longitud",
                    "destino": "Debe enviar destino_latitud/destino_longitud",
                }
            )

        distance_km = None
        duration_min = None

        if settings.ORS_API_KEY:
            try:
                resp = requests.post(
                    "https://api.openrouteservice.org/v2/directions/driving-car",
                    json={"coordinates": [[origen_lng, origen_lat], [destino_lng, destino_lat]]},
                    headers={"Authorization": settings.ORS_API_KEY},
                    timeout=15,
                )
                resp.raise_for_status()
                data = resp.json()
                segment = data["features"][0]["properties"]["segments"][0]
                distance_km = round(segment["distance"] / 1000, 2)
                duration_min = round(segment["duration"] / 60, 1)
            except Exception:
                distance_km = round(_haversine_km(origen_lat, origen_lng, destino_lat, destino_lng), 2)
        else:
            distance_km = round(_haversine_km(origen_lat, origen_lng, destino_lat, destino_lng), 2)

        return Response(
            {
                "distance_km": distance_km,
                "duration_min": duration_min,
            }
        )
