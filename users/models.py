import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        DRIVER = "DRIVER", "Driver"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.DRIVER, db_index=True)
    photo = models.FileField(upload_to="users/photos/", blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, default="")
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        super().clean()
        if self.birth_date and self.birth_date > timezone.localdate():
            raise ValidationError({"birth_date": "La fecha de nacimiento no puede ser futura."})

    def __str__(self):
        return f"{self.email} ({self.role})"
