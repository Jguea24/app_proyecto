import uuid

from django.db import models
from django.utils import timezone


class Empresa(models.Model):
    """Tenant principal del sistema."""

    class Plan(models.TextChoices):
        BASICO = "BASICO", "Basico"
        PRO = "PRO", "Pro"
        ENTERPRISE = "ENTERPRISE", "Enterprise"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150, unique=True)
    plan = models.CharField(max_length=20, choices=Plan.choices, default=Plan.BASICO)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-fecha_creacion", "nombre"]
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self) -> str:
        return self.nombre
