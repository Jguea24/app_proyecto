import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.empresas.models import Empresa
from apps.pedidos.models import Pedido


class Ruta(models.Model):
    """Ruta optimizada para un repartidor."""

    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        ASIGNADA = "ASIGNADA", "Asignada"
        EN_PROGRESO = "EN_PROGRESO", "En progreso"
        COMPLETADA = "COMPLETADA", "Completada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, related_name="rutas", on_delete=models.PROTECT)
    repartidor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="rutas",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        limit_choices_to={"rol": "REPARTIDOR"},
    )
    fecha = models.DateField(default=timezone.localdate, db_index=True)
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.BORRADOR, db_index=True)
    secuencia_optimizada = models.JSONField(default=list, blank=True)
    distancia_total_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    tiempo_estimado_min = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["-fecha", "-created_at"]
        indexes = [models.Index(fields=["empresa", "fecha", "estado"])]
        verbose_name = "Ruta"
        verbose_name_plural = "Rutas"

    def clean(self):
        if self.repartidor and getattr(self.repartidor, "rol", None) != "REPARTIDOR":
            raise ValidationError({"repartidor": "El usuario debe tener rol REPARTIDOR."})
        if self.repartidor and self.empresa_id and self.repartidor.empresa_id != self.empresa_id:
            raise ValidationError({"repartidor": "El repartidor debe pertenecer a la misma empresa."})

    def __str__(self) -> str:
        return f"Ruta {self.id} - {self.fecha}"


class ParadaRuta(models.Model):
    """Parada asociada a un pedido dentro de una ruta."""

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        EN_RUTA = "EN_RUTA", "En ruta"
        ENTREGADO = "ENTREGADO", "Entregado"
        FALLIDO = "FALLIDO", "Fallido"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ruta = models.ForeignKey(Ruta, related_name="paradas", on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, related_name="paradas", on_delete=models.PROTECT)
    orden = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.PENDIENTE, db_index=True)
    hora_llegada = models.DateTimeField(null=True, blank=True)
    foto_entrega = models.FileField(upload_to="rutas/fotos_entrega/", blank=True, null=True)
    firma = models.FileField(upload_to="rutas/firmas/", blank=True, null=True)
    notas_fallo = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(fields=["ruta", "orden"], name="unique_ruta_orden"),
            models.UniqueConstraint(fields=["ruta", "pedido"], name="unique_ruta_pedido"),
        ]
        indexes = [models.Index(fields=["ruta", "estado"])]
        verbose_name = "Parada de ruta"
        verbose_name_plural = "Paradas de ruta"

    def clean(self):
        if self.ruta and self.pedido:
            if self.ruta.empresa_id != self.pedido.empresa_id:
                raise ValidationError({"pedido": "El pedido debe pertenecer a la misma empresa de la ruta."})

    def __str__(self) -> str:
        return f"Parada {self.orden} - {self.pedido_id}"
