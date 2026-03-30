from django.utils import timezone
from rest_framework import serializers


class TrackingPayloadSerializer(serializers.Serializer):
    latitud = serializers.FloatField()
    longitud = serializers.FloatField()
    timestamp = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        lat = attrs.get("latitud")
        lng = attrs.get("longitud")
        if not (-90 <= lat <= 90):
            raise serializers.ValidationError({"latitud": "Latitud fuera de rango."})
        if not (-180 <= lng <= 180):
            raise serializers.ValidationError({"longitud": "Longitud fuera de rango."})

        timestamp = attrs.get("timestamp") or timezone.now()
        attrs["timestamp"] = timestamp
        return attrs
