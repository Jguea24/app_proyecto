from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Carrito, CarritoItem, Producto
from .permissions import IsAdminOrReadOnly
from .serializers import CarritoAddSerializer, CarritoSerializer, ProductoSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    """CRUD de productos por empresa."""

    queryset = Producto.objects.select_related("empresa")
    serializer_class = ProductoSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return queryset
        return queryset.filter(empresa_id=user.empresa_id)

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa)


class CarritoViewSet(viewsets.ViewSet):
    """Carrito del usuario autenticado."""

    permission_classes = [permissions.IsAuthenticated]

    def _get_cart(self, user):
        if not user.empresa_id:
            raise ValidationError({"empresa": "El usuario no tiene empresa asignada."})
        carrito, _ = Carrito.objects.get_or_create(empresa_id=user.empresa_id, usuario=user)
        return carrito

    def list(self, request):
        carrito = self._get_cart(request.user)
        serializer = CarritoSerializer(carrito)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="agregar")
    def agregar(self, request):
        serializer = CarritoAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        producto_id = serializer.validated_data["producto_id"]
        cantidad = serializer.validated_data["cantidad"]

        carrito = self._get_cart(request.user)

        try:
            producto = Producto.objects.get(id=producto_id, empresa_id=carrito.empresa_id, activo=True)
        except Producto.DoesNotExist:
            raise ValidationError({"producto_id": "Producto no encontrado."})

        if cantidad > producto.stock:
            raise ValidationError({"cantidad": "Stock insuficiente."})

        with transaction.atomic():
            item, created = CarritoItem.objects.select_for_update().get_or_create(
                carrito=carrito,
                producto=producto,
                defaults={"cantidad": 0, "precio_unitario": producto.precio},
            )
            nueva_cantidad = item.cantidad + cantidad
            if nueva_cantidad > producto.stock:
                raise ValidationError({"cantidad": "Stock insuficiente."})

            item.cantidad = nueva_cantidad
            item.precio_unitario = producto.precio
            item.save(update_fields=["cantidad", "precio_unitario"])

        return Response(CarritoSerializer(carrito).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="quitar")
    def quitar(self, request):
        serializer = CarritoAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        producto_id = serializer.validated_data["producto_id"]
        cantidad = serializer.validated_data["cantidad"]

        carrito = self._get_cart(request.user)
        try:
            item = CarritoItem.objects.get(carrito=carrito, producto_id=producto_id)
        except CarritoItem.DoesNotExist:
            raise ValidationError({"producto_id": "Producto no esta en el carrito."})

        if cantidad >= item.cantidad:
            item.delete()
        else:
            item.cantidad = item.cantidad - cantidad
            item.save(update_fields=["cantidad"])

        return Response(CarritoSerializer(carrito).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="vaciar")
    def vaciar(self, request):
        carrito = self._get_cart(request.user)
        carrito.items.all().delete()
        return Response(CarritoSerializer(carrito).data, status=status.HTTP_200_OK)
