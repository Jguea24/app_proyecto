from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Tracking

User = get_user_model()


class TrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tracking
        fields = (
            "id",
            "driver",
            "latitude",
            "longitude",
            "offline_id",
            "synced_from_offline",
            "device_recorded_at",
            "timestamp",
        )
        read_only_fields = ("id",)
        extra_kwargs = {"driver": {"required": False}}

    def validate_offline_id(self, value):
        if value is None:
            return value
        normalized = str(value).strip()
        if normalized == "":
            return None
        if len(normalized) < 6:
            raise serializers.ValidationError("offline_id debe tener al menos 6 caracteres.")
        return normalized

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        driver = attrs.get("driver")
        if not driver and user and user.is_authenticated and user.role == User.Role.DRIVER:
            attrs["driver"] = user

        driver = attrs.get("driver")
        if not driver:
            raise serializers.ValidationError({"driver": "Debe especificar un driver."})
        if driver.role != User.Role.DRIVER:
            raise serializers.ValidationError({"driver": "Solo usuarios DRIVER pueden registrar tracking."})

        lat = attrs.get("latitude")
        lng = attrs.get("longitude")
        if lat is not None and not (-90 <= lat <= 90):
            raise serializers.ValidationError({"latitude": "La latitud debe estar entre -90 y 90."})
        if lng is not None and not (-180 <= lng <= 180):
            raise serializers.ValidationError({"longitude": "La longitud debe estar entre -180 y 180."})

        synced_from_offline = attrs.get("synced_from_offline", False)
        offline_id = attrs.get("offline_id")
        if synced_from_offline and not offline_id:
            raise serializers.ValidationError({"offline_id": "offline_id es obligatorio para sincronizacion offline."})

        timestamp = attrs.get("timestamp") or timezone.now()
        if timestamp > timezone.now() + timezone.timedelta(minutes=5):
            raise serializers.ValidationError({"timestamp": "No se permiten timestamps muy en el futuro."})

        device_recorded_at = attrs.get("device_recorded_at")
        if device_recorded_at and device_recorded_at > timezone.now() + timezone.timedelta(minutes=5):
            raise serializers.ValidationError({"device_recorded_at": "No se permiten fechas muy en el futuro."})

        attrs["timestamp"] = timestamp
        return attrs
