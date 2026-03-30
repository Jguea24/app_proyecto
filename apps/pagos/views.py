from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from apps.usuarios.permissions import IsAdmin

from .models import Payment
from .serializers import BankTransferSerializer, CashPaymentSerializer, PaymentSerializer


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """Listado y detalle de pagos."""

    queryset = Payment.objects.select_related("order")
    serializer_class = PaymentSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        # Filtra por empresa del usuario.
        if not user.is_superuser:
            queryset = queryset.filter(order__empresa_id=user.empresa_id)

        metodo = self.request.query_params.get("payment_method")
        estado = self.request.query_params.get("status")

        if metodo:
            queryset = queryset.filter(payment_method=metodo)
        if estado:
            queryset = queryset.filter(status=estado)

        return queryset

    @action(detail=True, methods=["patch"], url_path="confirm")
    def confirm(self, request, pk=None):
        # Confirma un pago pendiente.
        pago = self.get_object()
        if pago.status != Payment.Estado.PENDIENTE:
            raise ValidationError({"status": "Solo se pueden confirmar pagos pendientes."})
        pago.status = Payment.Estado.COMPLETADO
        pago.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(pago).data, status=status.HTTP_200_OK)


class BankTransferCreateAPIView(CreateAPIView):
    """Registrar pago por transferencia bancaria."""

    serializer_class = BankTransferSerializer
    permission_classes = [IsAdmin]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pago = serializer.save()
        return Response(PaymentSerializer(pago).data, status=status.HTTP_201_CREATED)


class CashPaymentCreateAPIView(CreateAPIView):
    """Registrar pago en efectivo."""

    serializer_class = CashPaymentSerializer
    permission_classes = [IsAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pago = serializer.save()
        return Response(PaymentSerializer(pago).data, status=status.HTTP_201_CREATED)
