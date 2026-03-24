from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrAssignedDriverDeliveryProof(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_admin = user.is_superuser or getattr(user, "role", None) == "ADMIN"
        is_assigned_driver = obj.delivery_point.route.driver_id == user.id

        if request.method in SAFE_METHODS:
            return is_admin or is_assigned_driver

        return is_admin or is_assigned_driver
