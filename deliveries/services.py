from django.contrib.auth.models import AbstractBaseUser

from .models import DeliveryProof


def is_admin(user: AbstractBaseUser) -> bool:
    return bool(user and (user.is_superuser or getattr(user, "role", None) == "ADMIN"))


def find_proof_by_offline_id_for_user(user, offline_id: str):
    if not offline_id:
        return None

    queryset = DeliveryProof.objects.select_related("delivery_point", "delivery_point__route", "delivery_point__route__driver")
    if not is_admin(user):
        queryset = queryset.filter(delivery_point__route__driver=user)

    return queryset.filter(offline_id=offline_id).first()
