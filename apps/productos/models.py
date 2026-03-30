import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.empresas.models import Empresa


class Producto(models.Model):
    """Producto disponible para una empresa."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, related_name="productos", on_delete=models.PROTECT)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, default="")
    foto = models.FileField(upload_to="productos/fotos/", blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["-created_at", "nombre"]
        indexes = [models.Index(fields=["empresa", "activo"])]
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self) -> str:
        return self.nombre


class Carrito(models.Model):
    """Carrito por usuario dentro de una empresa."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, related_name="carritos", on_delete=models.PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="carritos", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["empresa", "usuario"], name="unique_carrito_empresa_usuario")
        ]
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"

    def __str__(self) -> str:
        return f"Carrito {self.usuario_id}"


class CarritoItem(models.Model):
    """Items de un carrito."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    carrito = models.ForeignKey(Carrito, related_name="items", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, related_name="carrito_items", on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["carrito", "producto"], name="unique_carrito_producto")
        ]
        verbose_name = "Item de carrito"
        verbose_name_plural = "Items de carrito"

    def __str__(self) -> str:
        return f"{self.producto_id} x {self.cantidad}"
