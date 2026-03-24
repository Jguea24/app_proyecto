import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Tracking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="trackings", on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    offline_id = models.CharField(max_length=64, null=True, blank=True, unique=True)
    synced_from_offline = models.BooleanField(default=False)
    device_recorded_at = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["driver", "timestamp"]),
            models.Index(fields=["offline_id"]),
        ]

    def clean(self):
        if self.driver and self.driver.role != "DRIVER":
            raise ValidationError({"driver": "Solo usuarios DRIVER pueden registrar tracking."})
        if not (-90 <= self.latitude <= 90):
            raise ValidationError({"latitude": "La latitud debe estar entre -90 y 90."})
        if not (-180 <= self.longitude <= 180):
            raise ValidationError({"longitude": "La longitud debe estar entre -180 y 180."})

    def __str__(self):
        return f"{self.driver_id} @ {self.timestamp}"
