from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_superuser or user.rol == "ADMIN"))


class IsRepartidor(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.rol == "REPARTIDOR")


class IsAdminOrCliente(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.rol in {"ADMIN", "CLIENTE"})
        )


class IsSameEmpresa(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        empresa_id = getattr(user, "empresa_id", None)
        obj_empresa_id = getattr(obj, "empresa_id", None)
        return bool(user and user.is_authenticated and empresa_id and obj_empresa_id and empresa_id == obj_empresa_id)
