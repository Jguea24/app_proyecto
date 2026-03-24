import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Route(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    date = models.DateField(db_index=True, default=timezone.localdate)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="routes",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "DRIVER"},
    )

    class Meta:
        ordering = ["-date", "name"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["date"]),
            models.Index(fields=["driver", "date"]),
        ]

    def clean(self):
        if self.driver and self.driver.role != "DRIVER":
            raise ValidationError({"driver": "El usuario asignado debe tener rol DRIVER."})

    def __str__(self):
        return f"{self.name} - {self.date}"


class DeliveryPoint(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(Route, related_name="delivery_points", on_delete=models.CASCADE)
    address = models.CharField(max_length=255, default="")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    order = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)

    class Meta:
        ordering = ["route", "order"]
        constraints = [models.UniqueConstraint(fields=["route", "order"], name="unique_route_order")]
        indexes = [models.Index(fields=["status"]), models.Index(fields=["route", "order"])]

    def clean(self):
        if not (-90 <= self.latitude <= 90):
            raise ValidationError({"latitude": "La latitud debe estar entre -90 y 90."})
        if not (-180 <= self.longitude <= 180):
            raise ValidationError({"longitude": "La longitud debe estar entre -180 y 180."})

    def __str__(self):
        return f"{self.route.name} - punto {self.order}"
