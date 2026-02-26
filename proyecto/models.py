from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    ROLE_ADMIN = "admin"
    ROLE_CLIENTE = "cliente"
    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_CLIENTE, "Cliente"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birth_date = models.DateField()
    address = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"{self.user.email} - {self.role}"