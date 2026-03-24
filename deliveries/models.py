import uuid

from django.db import models

from routes.models import DeliveryPoint


class DeliveryProof(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivery_point = models.ForeignKey(DeliveryPoint, related_name="delivery_proofs", on_delete=models.CASCADE)
    image = models.FileField(upload_to="delivery_proofs/images/", blank=True, null=True)
    signature = models.FileField(upload_to="delivery_proofs/signatures/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    offline_id = models.CharField(max_length=64, null=True, blank=True, unique=True)
    synced_from_offline = models.BooleanField(default=False)
    device_recorded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["delivery_point", "created_at"]),
            models.Index(fields=["offline_id"]),
        ]

    def __str__(self):
        return f"Proof {self.id} - {self.status}"
