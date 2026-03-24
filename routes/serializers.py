from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import DeliveryPoint, Route

User = get_user_model()


class DeliveryPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPoint
        fields = ("id", "route", "address", "latitude", "longitude", "order", "status")
        read_only_fields = ("id",)

    def validate(self, attrs):
        lat = attrs.get("latitude", getattr(self.instance, "latitude", None))
        lng = attrs.get("longitude", getattr(self.instance, "longitude", None))

        if lat is not None and not (-90 <= lat <= 90):
            raise serializers.ValidationError({"latitude": "La latitud debe estar entre -90 y 90."})
        if lng is not None and not (-180 <= lng <= 180):
            raise serializers.ValidationError({"longitude": "La longitud debe estar entre -180 y 180."})

        return attrs


class NestedDeliveryPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPoint
        fields = ("address", "latitude", "longitude", "order", "status")

    def validate(self, attrs):
        lat = attrs.get("latitude")
        lng = attrs.get("longitude")

        if lat is not None and not (-90 <= lat <= 90):
            raise serializers.ValidationError({"latitude": "La latitud debe estar entre -90 y 90."})
        if lng is not None and not (-180 <= lng <= 180):
            raise serializers.ValidationError({"longitude": "La longitud debe estar entre -180 y 180."})

        return attrs


class RouteSerializer(serializers.ModelSerializer):
    delivery_points = NestedDeliveryPointSerializer(many=True, required=False)

    class Meta:
        model = Route
        fields = ("id", "name", "date", "status", "driver", "delivery_points")
        read_only_fields = ("id",)

    def validate_driver(self, value):
        if value and value.role != User.Role.DRIVER:
            raise serializers.ValidationError("El usuario asignado debe tener rol DRIVER.")
        return value

    def validate(self, attrs):
        status_value = attrs.get("status", getattr(self.instance, "status", Route.Status.PENDING))
        driver = attrs.get("driver", getattr(self.instance, "driver", None))
        points_data = attrs.get("delivery_points")

        if status_value == Route.Status.IN_PROGRESS and not driver:
            raise serializers.ValidationError({"driver": "Debe asignar un DRIVER antes de iniciar la ruta."})

        if self.instance is None and not points_data:
            raise serializers.ValidationError(
                {"delivery_points": "Debe enviar al menos un punto de entrega al crear la ruta."}
            )

        if points_data is not None and len(points_data) < 2:
            raise serializers.ValidationError(
                {"delivery_points": "La ruta debe tener multiples puntos (minimo 2)."}
            )

        if points_data:
            orders = [item["order"] for item in points_data]
            if len(orders) != len(set(orders)):
                raise serializers.ValidationError({"delivery_points": "El campo order no puede repetirse."})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        points_data = validated_data.pop("delivery_points", [])
        route = Route.objects.create(**validated_data)

        for point_data in points_data:
            DeliveryPoint.objects.create(route=route, **point_data)

        return route

    @transaction.atomic
    def update(self, instance, validated_data):
        points_data = validated_data.pop("delivery_points", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if points_data is not None:
            instance.delivery_points.all().delete()
            for point_data in points_data:
                DeliveryPoint.objects.create(route=instance, **point_data)

        return instance
