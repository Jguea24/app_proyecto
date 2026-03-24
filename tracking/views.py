from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response

from users.permissions import IsAdminRole

from .models import Tracking
from .permissions import IsAdminOrOwnerTracking
from .serializers import TrackingSerializer
from .services import find_tracking_by_offline_id_for_user


class TrackingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Tracking.objects.select_related("driver")
    serializer_class = TrackingSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwnerTracking]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not (user.is_superuser or user.role == "ADMIN"):
            queryset = queryset.filter(driver=user)

        driver_id = self.request.query_params.get("driver")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        offline_id = self.request.query_params.get("offline_id")

        if driver_id and (user.is_superuser or user.role == "ADMIN"):
            queryset = queryset.filter(driver_id=driver_id)
        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)
        if offline_id:
            queryset = queryset.filter(offline_id=offline_id)

        return queryset.order_by("-timestamp")

    def create(self, request, *args, **kwargs):
        offline_id = request.data.get("offline_id")
        existing = find_tracking_by_offline_id_for_user(request.user, offline_id)
        if existing:
            serializer = self.get_serializer(existing)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        offline_id = serializer.validated_data.get("offline_id")

        if user.role == "DRIVER" and not user.is_superuser:
            serializer.save(driver=user, synced_from_offline=bool(offline_id))
            return
        serializer.save(synced_from_offline=bool(offline_id))

    def get_permissions(self):
        if self.action == "destroy":
            return [permissions.IsAuthenticated(), IsAdminRole()]
        return super().get_permissions()
