from django.contrib.gis.geos import Point
from rest_framework import serializers

from .models import Pedido


class PedidoSerializer(serializers.ModelSerializer):
    # Compatibilidad anterior (destino)
    latitud = serializers.FloatField(write_only=True, required=False)
    longitud = serializers.FloatField(write_only=True, required=False)

    # Origen
    origen_latitud = serializers.FloatField(write_only=True, required=False)
    origen_longitud = serializers.FloatField(write_only=True, required=False)

    # Destino
    destino_latitud = serializers.FloatField(write_only=True, required=False)
    destino_longitud = serializers.FloatField(write_only=True, required=False)
    destino_direccion = serializers.CharField(source="direccion", required=False)

    ubicacion = serializers.SerializerMethodField(read_only=True)
    origen_ubicacion = serializers.SerializerMethodField(read_only=True)
    destino_ubicacion = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Pedido
        fields = (
            "id",
            "empresa",
            "cliente_nombre",
            "cliente_telefono",
            "direccion",
            "destino_direccion",
            "ubicacion",
            "destino_ubicacion",
            "latitud",
            "longitud",
            "destino_latitud",
            "destino_longitud",
            "origen_direccion",
            "origen_ubicacion",
            "origen_latitud",
            "origen_longitud",
            "estado",
            "ventana_inicio",
            "ventana_fin",
            "notas",
            "created_at",
        )
        read_only_fields = ("id", "empresa", "created_at")

    def get_ubicacion(self, obj):
        if not obj.ubicacion:
            return None
        return {"latitud": obj.ubicacion.y, "longitud": obj.ubicacion.x}

    def get_destino_ubicacion(self, obj):
        return self.get_ubicacion(obj)

    def get_origen_ubicacion(self, obj):
        if not obj.origen_ubicacion:
            return None
        return {"latitud": obj.origen_ubicacion.y, "longitud": obj.origen_ubicacion.x}

    def _validate_lat_lng(self, lat, lng, campo):
        if lat is None or lng is None:
            raise serializers.ValidationError({campo: "Debe enviar latitud y longitud."})
        if not (-90 <= lat <= 90):
            raise serializers.ValidationError({f"{campo}_latitud": "Latitud fuera de rango."})
        if not (-180 <= lng <= 180):
            raise serializers.ValidationError({f"{campo}_longitud": "Longitud fuera de rango."})

    def validate(self, attrs):
        # Origen
        origen_lat = attrs.pop("origen_latitud", None)
        origen_lng = attrs.pop("origen_longitud", None)

        # Destino (nuevo)
        destino_lat = attrs.pop("destino_latitud", None)
        destino_lng = attrs.pop("destino_longitud", None)

        # Destino (compatibilidad anterior)
        legacy_lat = attrs.pop("latitud", None)
        legacy_lng = attrs.pop("longitud", None)
        if destino_lat is None and destino_lng is None and (legacy_lat is not None or legacy_lng is not None):
            destino_lat, destino_lng = legacy_lat, legacy_lng

        if destino_lat is not None or destino_lng is not None:
            self._validate_lat_lng(destino_lat, destino_lng, "destino")
            attrs["ubicacion"] = Point(destino_lng, destino_lat, srid=4326)

        if origen_lat is not None or origen_lng is not None:
            self._validate_lat_lng(origen_lat, origen_lng, "origen")
            attrs["origen_ubicacion"] = Point(origen_lng, origen_lat, srid=4326)

        ventana_inicio = attrs.get("ventana_inicio")
        ventana_fin = attrs.get("ventana_fin")
        if ventana_inicio and ventana_fin and ventana_fin < ventana_inicio:
            raise serializers.ValidationError({"ventana_fin": "La ventana fin debe ser mayor que inicio."})

        return attrs
