from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnlySameEmpresa(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        same_empresa = getattr(obj, "empresa_id", None) == getattr(user, "empresa_id", None)

        if request.method in SAFE_METHODS:
            return same_empresa

        return same_empresa and (user.is_superuser or user.rol in {"ADMIN", "CLIENTE"})
