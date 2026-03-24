from django.contrib.auth.models import AbstractBaseUser

from .models import Tracking


def is_admin(user: AbstractBaseUser) -> bool:
    return bool(user and (user.is_superuser or getattr(user, "role", None) == "ADMIN"))


def find_tracking_by_offline_id_for_user(user, offline_id: str):
    if not offline_id:
        return None

    queryset = Tracking.objects.select_related("driver")
    if not is_admin(user):
        queryset = queryset.filter(driver=user)

    return queryset.filter(offline_id=offline_id).first()
