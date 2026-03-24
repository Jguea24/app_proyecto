from django.utils import timezone
from rest_framework import serializers

from .models import DeliveryProof

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024


class DeliveryProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryProof
        fields = (
            "id",
            "delivery_point",
            "image",
            "signature",
            "status",
            "offline_id",
            "synced_from_offline",
            "device_recorded_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def _validate_file(self, file_obj, field_name):
        if not file_obj:
            return

        content_type = getattr(file_obj, "content_type", None)
        size = getattr(file_obj, "size", None)

        if content_type and content_type.lower() not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError({field_name: "Formato no permitido. Use JPG, PNG o WEBP."})

        if size and size > MAX_UPLOAD_SIZE:
            raise serializers.ValidationError({field_name: "El archivo excede 10MB."})

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
        instance = getattr(self, "instance", None)
        image = attrs.get("image", getattr(instance, "image", None))
        signature = attrs.get("signature", getattr(instance, "signature", None))
        status_value = attrs.get("status", getattr(instance, "status", DeliveryProof.Status.PENDING))

        self._validate_file(attrs.get("image"), "image")
        self._validate_file(attrs.get("signature"), "signature")

        if status_value == DeliveryProof.Status.DELIVERED and not (image or signature):
            raise serializers.ValidationError(
                {"non_field_errors": "Debe adjuntar imagen o firma para un estado delivered."}
            )

        if instance and instance.status in {DeliveryProof.Status.DELIVERED, DeliveryProof.Status.FAILED}:
            if status_value != instance.status:
                raise serializers.ValidationError(
                    {"status": f"No se permite cambiar estado desde {instance.status}."}
                )

        synced_from_offline = attrs.get(
            "synced_from_offline",
            getattr(instance, "synced_from_offline", False),
        )
        offline_id = attrs.get("offline_id", getattr(instance, "offline_id", None))
        if synced_from_offline and not offline_id:
            raise serializers.ValidationError({"offline_id": "offline_id es obligatorio para sincronizacion offline."})

        device_recorded_at = attrs.get("device_recorded_at", getattr(instance, "device_recorded_at", None))
        if device_recorded_at and device_recorded_at > timezone.now() + timezone.timedelta(minutes=5):
            raise serializers.ValidationError({"device_recorded_at": "No se permiten fechas muy en el futuro."})

        return attrs


class DeliveryProofStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=DeliveryProof.Status.choices)
