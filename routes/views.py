from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from users.permissions import IsAdminRole

from .models import DeliveryPoint, Route
from .permissions import IsAdminOrAssignedDriverPoint, IsAdminOrAssignedDriverReadOnly
from .serializers import DeliveryPointSerializer, RouteSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("driver").prefetch_related("delivery_points")
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAssignedDriverReadOnly]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "assign_driver"}:
            return [permissions.IsAuthenticated(), IsAdminRole()]
        if self.action in {"start", "complete"}:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAdminOrAssignedDriverReadOnly()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not (user.is_superuser or user.role == "ADMIN"):
            queryset = queryset.filter(driver=user)

        status_param = self.request.query_params.get("status")
        date_param = self.request.query_params.get("date")
        driver_param = self.request.query_params.get("driver")

        if status_param:
            queryset = queryset.filter(status=status_param)
        if date_param:
            queryset = queryset.filter(date=date_param)
        if driver_param and (user.is_superuser or user.role == "ADMIN"):
            queryset = queryset.filter(driver_id=driver_param)

        return queryset

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsAdminRole])
    def assign_driver(self, request, pk=None):
        route = self.get_object()
        driver_id = request.data.get("driver_id")

        if not driver_id:
            return Response({"ok": False, "error": "driver_id es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            driver = User.objects.get(id=driver_id, role=User.Role.DRIVER, is_active=True)
        except User.DoesNotExist:
            return Response(
                {"ok": False, "error": "El driver no existe o no esta activo."},
                status=status.HTTP_404_NOT_FOUND,
            )

        route.driver = driver
        route.save(update_fields=["driver"])

        return Response(RouteSerializer(route, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["get"])
    def delivery_points(self, request, pk=None):
        route = self.get_object()
        points = route.delivery_points.all().order_by("order")
        serializer = DeliveryPointSerializer(points, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        route = self.get_object()

        if not self._can_manage_route(request.user, route):
            return Response({"ok": False, "error": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        if not route.driver:
            return Response(
                {"ok": False, "error": "Debe asignar un DRIVER antes de iniciar la ruta."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if route.status == Route.Status.COMPLETED:
            return Response(
                {"ok": False, "error": "No se puede iniciar una ruta completada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        route.status = Route.Status.IN_PROGRESS
        route.save(update_fields=["status"])

        return Response(RouteSerializer(route, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        route = self.get_object()

        if not self._can_manage_route(request.user, route):
            return Response({"ok": False, "error": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        route.status = Route.Status.COMPLETED
        route.save(update_fields=["status"])

        return Response(RouteSerializer(route, context=self.get_serializer_context()).data)

    def _can_manage_route(self, user, route):
        return bool(user.is_superuser or user.role == "ADMIN" or route.driver_id == user.id)


class DeliveryPointViewSet(viewsets.ModelViewSet):
    queryset = DeliveryPoint.objects.select_related("route", "route__driver")
    serializer_class = DeliveryPointSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAssignedDriverPoint]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        route_id = self.request.query_params.get("route")
        if route_id:
            queryset = queryset.filter(route_id=route_id)

        if user.is_superuser or user.role == "ADMIN":
            return queryset

        return queryset.filter(route__driver=user)

    def get_permissions(self):
        if self.action in {"create", "destroy"}:
            return [permissions.IsAuthenticated(), IsAdminRole()]
        return [permissions.IsAuthenticated(), IsAdminOrAssignedDriverPoint()]

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user

        if not (user.is_superuser or user.role == "ADMIN"):
            allowed_fields = {"status"}
            incoming_fields = set(request.data.keys())
            if not incoming_fields.issubset(allowed_fields):
                raise PermissionDenied("Driver solo puede actualizar el estado del punto.")

            if obj.route.driver_id != user.id:
                raise PermissionDenied("No puede modificar puntos de rutas no asignadas.")

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def by_route(self, request):
        route_id = request.query_params.get("route")
        if not route_id:
            raise ValidationError({"route": "Debe enviar el query param route."})

        queryset = self.get_queryset().filter(route_id=route_id).order_by("order")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        point = self.get_object()
        status_value = request.data.get("status")

        if not status_value:
            raise ValidationError({"status": "Este campo es obligatorio."})

        serializer = self.get_serializer(point, data={"status": status_value}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
