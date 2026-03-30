from rest_framework import serializers

from .models import Carrito, CarritoItem, Producto


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = (
            "id",
            "empresa",
            "nombre",
            "descripcion",
            "foto",
            "precio",
            "stock",
            "activo",
            "created_at",
        )
        read_only_fields = ("id", "empresa", "created_at")

    def to_internal_value(self, data):
        if "stock" not in data and "stok" in data:
            data = {**data, "stock": data.get("stok")}
        return super().to_internal_value(data)


class ProductoResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ("id", "nombre", "precio", "stock")


class CarritoItemSerializer(serializers.ModelSerializer):
    producto = ProductoResumenSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CarritoItem
        fields = ("id", "producto", "cantidad", "precio_unitario", "subtotal")

    def get_subtotal(self, obj):
        return float(obj.cantidad * obj.precio_unitario)


class CarritoSerializer(serializers.ModelSerializer):
    items = CarritoItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Carrito
        fields = ("id", "usuario", "empresa", "items", "total", "updated_at")
        read_only_fields = ("id", "usuario", "empresa", "updated_at")

    def get_total(self, obj):
        total = 0
        for item in obj.items.all():
            total += item.cantidad * item.precio_unitario
        return float(total)


class CarritoAddSerializer(serializers.Serializer):
    producto_id = serializers.UUIDField()
    cantidad = serializers.IntegerField(min_value=1, default=1)
