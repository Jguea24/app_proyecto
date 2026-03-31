import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.empresas.models import Empresa

from .managers import UsuarioManager


class Usuario(AbstractUser):
    """Usuario del sistema En Ruta."""

    class Rol(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        REPARTIDOR = "REPARTIDOR", "Repartidor"
        CLIENTE = "CLIENTE", "Cliente"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)
    empresa = models.ForeignKey(Empresa, related_name="usuarios", on_delete=models.PROTECT, null=True, blank=True)
    rol = models.CharField(max_length=15, choices=Rol.choices, default=Rol.REPARTIDOR, db_index=True)
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=30, blank=True, default="")
    foto = models.FileField(upload_to="usuarios/fotos/", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def clean(self):
        super().clean()
        if not self.is_superuser and not self.empresa:
            raise ValidationError({"empresa": "Debe asignar una empresa al usuario."})

    def __str__(self) -> str:
        return f"{self.email} ({self.rol})"
