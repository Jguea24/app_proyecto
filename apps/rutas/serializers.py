from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.pedidos.models import Pedido

from .models import ParadaRuta, Ruta


class PedidoResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ("id", "cliente_nombre", "direccion", "estado")


class ParadaRutaSerializer(serializers.ModelSerializer):
    pedido = PedidoResumenSerializer(read_only=True)

    class Meta:
        model = ParadaRuta
        fields = (
            "id",
            "ruta",
            "pedido",
            "orden",
            "estado",
            "hora_llegada",
            "foto_entrega",
            "firma",
            "notas_fallo",
        )
        read_only_fields = ("id", "ruta", "pedido", "orden")


class ParadaRutaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParadaRuta
        fields = ("estado", "hora_llegada", "foto_entrega", "firma", "notas_fallo")

    def validate(self, attrs):
        estado = attrs.get("estado", getattr(self.instance, "estado", ParadaRuta.Estado.PENDIENTE))
        foto = attrs.get("foto_entrega", getattr(self.instance, "foto_entrega", None))
        firma = attrs.get("firma", getattr(self.instance, "firma", None))

        if estado == ParadaRuta.Estado.ENTREGADO and not (foto or firma):
            raise serializers.ValidationError(
                {"estado": "Debe adjuntar foto o firma para marcar como ENTREGADO."}
            )

        return attrs

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        if "estado" in validated_data:
            Pedido.objects.filter(id=instance.pedido_id).update(estado=validated_data["estado"])

        return instance


class RutaSerializer(serializers.ModelSerializer):
    paradas = ParadaRutaSerializer(many=True, read_only=True)

    class Meta:
        model = Ruta
        fields = (
            "id",
            "empresa",
            "repartidor",
            "fecha",
            "estado",
            "secuencia_optimizada",
            "distancia_total_km",
            "tiempo_estimado_min",
            "paradas",
            "created_at",
        )
        read_only_fields = ("id", "empresa", "created_at")


class RutaCreateSerializer(serializers.ModelSerializer):
    pedido_ids = serializers.ListField(child=serializers.UUIDField(), write_only=True)

    class Meta:
        model = Ruta
        fields = (
            "id",
            "repartidor",
            "fecha",
            "estado",
            "pedido_ids",
            "secuencia_optimizada",
            "distancia_total_km",
            "tiempo_estimado_min",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        request = self.context.get("request")
        empresa = getattr(request.user, "empresa", None) if request else None
        repartidor = attrs.get("repartidor")
        fecha = attrs.get("fecha", timezone.localdate())
        estado = attrs.get("estado", Ruta.Estado.BORRADOR)

        if repartidor:
            if repartidor.rol != "REPARTIDOR":
                raise serializers.ValidationError({"repartidor": "Debe tener rol REPARTIDOR."})
            if empresa and repartidor.empresa_id != empresa.id:
                raise serializers.ValidationError({"repartidor": "Repartidor fuera de la empresa."})

            if estado in {Ruta.Estado.ASIGNADA, Ruta.Estado.EN_PROGRESO}:
                exists = Ruta.objects.filter(
                    repartidor=repartidor,
                    fecha=fecha,
                    estado__in={Ruta.Estado.ASIGNADA, Ruta.Estado.EN_PROGRESO},
                )
                if self.instance:
                    exists = exists.exclude(pk=self.instance.pk)
                if exists.exists():
                    raise serializers.ValidationError(
                        {"repartidor": "El repartidor ya tiene una ruta activa en esa fecha."}
                    )

        pedido_ids = attrs.get("pedido_ids") or []
        if not pedido_ids:
            raise serializers.ValidationError({"pedido_ids": "Debe enviar al menos un pedido."})

        if len(pedido_ids) != len(set(pedido_ids)):
            raise serializers.ValidationError({"pedido_ids": "No puede repetir pedidos."})

        if empresa:
            pedidos_validos = Pedido.objects.filter(empresa=empresa, id__in=pedido_ids).count()
            if pedidos_validos != len(pedido_ids):
                raise serializers.ValidationError({"pedido_ids": "Todos los pedidos deben ser de la empresa."})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        pedido_ids = validated_data.pop("pedido_ids")
        request = self.context.get("request")
        empresa = request.user.empresa if request else None
        ruta = Ruta.objects.create(empresa=empresa, **validated_data)

        pedido_map = Pedido.objects.in_bulk(pedido_ids)
        paradas = []
        for idx, pedido_id in enumerate(pedido_ids, start=1):
            pedido = pedido_map.get(pedido_id)
            if pedido:
                paradas.append(ParadaRuta(ruta=ruta, pedido=pedido, orden=idx))

        ParadaRuta.objects.bulk_create(paradas)

        if ruta.estado in {Ruta.Estado.ASIGNADA, Ruta.Estado.EN_PROGRESO}:
            Pedido.objects.filter(id__in=pedido_ids).update(estado=Pedido.Estado.EN_RUTA)

        return ruta
