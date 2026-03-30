from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnlySameEmpresa(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        same_empresa = getattr(obj, "empresa_id", None) == getattr(user, "empresa_id", None)
        if request.method in SAFE_METHODS:
            return same_empresa
        return same_empresa and (user.is_superuser or user.rol == "ADMIN")


class IsAdminOrRepartidorDeRuta(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        same_empresa = obj.ruta.empresa_id == user.empresa_id
        if not same_empresa:
            return False

        if user.is_superuser or user.rol == "ADMIN":
            return True

        return obj.ruta.repartidor_id == user.id


class IsAdminOrRepartidorRutaReadonly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        same_empresa = obj.empresa_id == user.empresa_id
        if not same_empresa:
            return False

        if request.method in SAFE_METHODS:
            return user.is_superuser or user.rol == "ADMIN" or obj.repartidor_id == user.id

        return user.is_superuser or user.rol == "ADMIN"
