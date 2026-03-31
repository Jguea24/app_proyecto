from decimal import Decimal

from rest_framework import serializers

from apps.pedidos.models import Pedido

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer general de pagos."""

    cliente_nombre = serializers.CharField(source="order.cliente_nombre", read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = (
            "payment_method",
            "status",
            "change_given",
            "created_at",
            "updated_at",
        )


class BasePaymentCreateSerializer(serializers.ModelSerializer):
    """Base para validar reglas comunes en creacion de pagos."""

    order = serializers.PrimaryKeyRelatedField(queryset=Pedido.objects.all())

    def validate(self, attrs):
        order = attrs.get("order")
        # Evita registrar pagos nuevos si ya existe uno completado para el pedido.
        if order and Payment.objects.filter(order=order, status=Payment.Estado.COMPLETADO).exists():
            raise serializers.ValidationError(
                {"order": "El pedido ya tiene un pago completado."}
            )
        return attrs


class BankTransferSerializer(BasePaymentCreateSerializer):
    """Pago por transferencia bancaria."""

    class Meta:
        model = Payment
        fields = (
            "order",
            "amount",
            "bank_name",
            "account_number",
            "transaction_reference",
            "transfer_receipt",
            "transfer_date",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # La referencia de transferencia es obligatoria.
        if not attrs.get("transaction_reference"):
            raise serializers.ValidationError(
                {"transaction_reference": "La referencia de la transferencia es obligatoria."}
            )
        return attrs

    def create(self, validated_data):
        validated_data["payment_method"] = Payment.Metodo.TRANSFERENCIA
        validated_data.setdefault("status", Payment.Estado.PENDIENTE)
        return Payment.objects.create(**validated_data)


class CashPaymentSerializer(BasePaymentCreateSerializer):
    """Pago en efectivo."""

    class Meta:
        model = Payment
        fields = (
            "order",
            "amount",
            "cash_received",
            "confirmed_by",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        amount = attrs.get("amount")
        cash_received = attrs.get("cash_received")

        if cash_received is None:
            raise serializers.ValidationError({"cash_received": "El efectivo recibido es obligatorio."})

        if amount is None:
            raise serializers.ValidationError({"amount": "El monto es obligatorio."})

        # El efectivo debe cubrir el monto total.
        if Decimal(cash_received) < Decimal(amount):
            raise serializers.ValidationError(
                {"cash_received": "El efectivo recibido debe ser mayor o igual al monto."}
            )

        if not attrs.get("confirmed_by"):
            raise serializers.ValidationError({"confirmed_by": "Debe indicar quien confirma el pago."})

        return attrs

    def create(self, validated_data):
        validated_data["payment_method"] = Payment.Metodo.EFECTIVO
        validated_data.setdefault("status", Payment.Estado.PENDIENTE)
        # Calcula el vuelto de forma automatica.
        amount = Decimal(validated_data["amount"])
        cash_received = Decimal(validated_data["cash_received"])
        validated_data["change_given"] = cash_received - amount
        return Payment.objects.create(**validated_data)
