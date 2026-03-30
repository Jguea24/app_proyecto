import uuid

from django.contrib.gis.db import models
from django.utils import timezone

from apps.empresas.models import Empresa


class Pedido(models.Model):
    """Pedido creado por una empresa."""

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        EN_RUTA = "EN_RUTA", "En ruta"
        ENTREGADO = "ENTREGADO", "Entregado"
        FALLIDO = "FALLIDO", "Fallido"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, related_name="pedidos", on_delete=models.PROTECT)
    cliente_nombre = models.CharField(max_length=150)
    cliente_telefono = models.CharField(max_length=30, blank=True, default="")
    # Destino (direccion y ubicacion de entrega)
    direccion = models.CharField(max_length=255)
    ubicacion = models.PointField(geography=True, srid=4326)
    # Origen (direccion y ubicacion de recogida)
    origen_direccion = models.CharField(max_length=255, blank=True, default="")
    origen_ubicacion = models.PointField(geography=True, srid=4326, null=True, blank=True)
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.PENDIENTE, db_index=True)
    ventana_inicio = models.DateTimeField(null=True, blank=True)
    ventana_fin = models.DateTimeField(null=True, blank=True)
    notas = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["empresa", "estado"])]
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self) -> str:
        return f"{self.cliente_nombre} - {self.direccion}"
