from django.db import models
from django.utils import timezone

from apps.pedidos.models import Pedido


class Payment(models.Model):
    """Registro de pago asociado a un pedido."""

    class Metodo(models.TextChoices):
        TRANSFERENCIA = "transferencia", "Transferencia"
        EFECTIVO = "efectivo", "Efectivo"

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        COMPLETADO = "completado", "Completado"
        CANCELADO = "cancelado", "Cancelado"

    order = models.ForeignKey(Pedido, related_name="pagos", on_delete=models.PROTECT)
    payment_method = models.CharField(max_length=20, choices=Metodo.choices)
    status = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        db_index=True,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    # Transferencia bancaria
    bank_name = models.CharField(max_length=120, blank=True, default="")
    account_number = models.CharField(max_length=50, blank=True, default="")
    transaction_reference = models.CharField(max_length=120, blank=True, default="")
    transfer_receipt = models.FileField(upload_to="pagos/transferencias/", blank=True, null=True)
    transfer_date = models.DateField(blank=True, null=True)

    # Efectivo
    cash_received = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    change_given = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    confirmed_by = models.CharField(max_length=120, blank=True, default="")

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["payment_method", "status"]),
            models.Index(fields=["order", "status"]),
        ]
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self) -> str:
        return f"{self.order_id} - {self.payment_method} - {self.status}"
