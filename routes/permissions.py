from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrAssignedDriverReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_admin = getattr(user, "role", None) == "ADMIN" or user.is_superuser

        if request.method in SAFE_METHODS:
            return is_admin or obj.driver_id == user.id

        return is_admin


class IsAdminOrAssignedDriverPoint(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_admin = getattr(user, "role", None) == "ADMIN" or user.is_superuser
        is_assigned_driver = obj.route.driver_id == user.id

        if request.method in SAFE_METHODS:
            return is_admin or is_assigned_driver

        return is_admin or is_assigned_driver
