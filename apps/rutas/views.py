from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.pedidos.models import Pedido
from apps.usuarios.permissions import IsAdmin

from .models import ParadaRuta, Ruta
from .permissions import IsAdminOrReadOnlySameEmpresa, IsAdminOrRepartidorDeRuta, IsAdminOrRepartidorRutaReadonly
from .serializers import ParadaRutaSerializer, ParadaRutaUpdateSerializer, RutaCreateSerializer, RutaSerializer
from .services import optimize_route


class RutaViewSet(viewsets.ModelViewSet):
    """CRUD de rutas y acciones de negocio."""

    queryset = Ruta.objects.select_related("empresa", "repartidor").prefetch_related("paradas", "paradas__pedido")
    serializer_class = RutaSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnlySameEmpresa]

    def get_serializer_class(self):
        if self.action == "create":
            return RutaCreateSerializer
        return RutaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return queryset
        if user.rol == "ADMIN":
            return queryset.filter(empresa_id=user.empresa_id)
        return queryset.filter(empresa_id=user.empresa_id, repartidor_id=user.id)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def asignar_repartidor(self, request, pk=None):
        """Asigna un repartidor a la ruta."""

        ruta = self.get_object()
        driver_id = request.data.get("repartidor_id")
        if not driver_id:
            raise ValidationError({"repartidor_id": "Es obligatorio."})

        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            repartidor = User.objects.get(id=driver_id, rol=User.Rol.REPARTIDOR, empresa_id=ruta.empresa_id)
        except User.DoesNotExist:
            raise ValidationError({"repartidor_id": "Repartidor no valido para esta empresa."})

        active = Ruta.objects.filter(
            repartidor=repartidor,
            fecha=ruta.fecha,
            estado__in={Ruta.Estado.ASIGNADA, Ruta.Estado.EN_PROGRESO},
        ).exclude(pk=ruta.pk)
        if active.exists():
            raise ValidationError({"repartidor_id": "El repartidor ya tiene una ruta activa ese dia."})

        ruta.repartidor = repartidor
        if ruta.estado == Ruta.Estado.BORRADOR:
            ruta.estado = Ruta.Estado.ASIGNADA
        ruta.save(update_fields=["repartidor", "estado"])
        return Response(RutaSerializer(ruta).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def iniciar(self, request, pk=None):
        """Marca la ruta como EN_PROGRESO."""

        ruta = self.get_object()
        if not ruta.repartidor:
            raise ValidationError({"repartidor": "Debe asignar un repartidor antes de iniciar."})
        ruta.estado = Ruta.Estado.EN_PROGRESO
        ruta.save(update_fields=["estado"])
        Pedido.objects.filter(paradas__ruta=ruta).update(estado=Pedido.Estado.EN_RUTA)
        return Response(RutaSerializer(ruta).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def completar(self, request, pk=None):
        """Marca la ruta como COMPLETADA."""

        ruta = self.get_object()
        ruta.estado = Ruta.Estado.COMPLETADA
        ruta.save(update_fields=["estado"])
        return Response(RutaSerializer(ruta).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def optimizar(self, request, pk=None):
        """Calcula la secuencia optimizada usando OpenRouteService."""

        ruta = self.get_object()
        coordenadas = [
            (parada.pedido.ubicacion.y, parada.pedido.ubicacion.x)
            for parada in ruta.paradas.select_related("pedido")
            if parada.pedido and parada.pedido.ubicacion
        ]
        if not coordenadas:
            raise ValidationError({"paradas": "No hay coordenadas suficientes para optimizar."})

        data = optimize_route(coordenadas)
        ruta.secuencia_optimizada = data
        ruta.save(update_fields=["secuencia_optimizada"])
        return Response(RutaSerializer(ruta).data, status=status.HTTP_200_OK)


class ParadaRutaViewSet(viewsets.ModelViewSet):
    """Gestion de paradas de ruta (solo repartidor actualiza)."""

    queryset = ParadaRuta.objects.select_related("ruta", "ruta__empresa", "pedido")
    serializer_class = ParadaRutaSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrRepartidorDeRuta]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser or user.rol == "ADMIN":
            return queryset.filter(ruta__empresa_id=user.empresa_id)
        return queryset.filter(ruta__empresa_id=user.empresa_id, ruta__repartidor_id=user.id)

    def get_serializer_class(self):
        if self.action in {"update", "partial_update"}:
            return ParadaRutaUpdateSerializer
        return ParadaRutaSerializer

    def update(self, request, *args, **kwargs):
        if request.user.rol != "REPARTIDOR":
            raise PermissionDenied("Solo REPARTIDOR puede actualizar paradas.")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated, IsAdminOrRepartidorRutaReadonly])
    def por_ruta(self, request):
        """Lista paradas filtradas por ruta."""

        ruta_id = request.query_params.get("ruta")
        if not ruta_id:
            raise ValidationError({"ruta": "Debe enviar el query param ruta."})

        queryset = self.get_queryset().filter(ruta_id=ruta_id).order_by("orden")
        serializer = ParadaRutaSerializer(queryset, many=True)
        return Response(serializer.data)
