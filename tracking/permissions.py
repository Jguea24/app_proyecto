from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrOwnerTracking(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_admin = user.is_superuser or getattr(user, "role", None) == "ADMIN"

        if request.method in SAFE_METHODS:
            return is_admin or obj.driver_id == user.id

        return is_admin or obj.driver_id == user.id
