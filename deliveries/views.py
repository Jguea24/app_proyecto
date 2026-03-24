from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from users.permissions import IsAdminRole

from .models import DeliveryProof
from .permissions import IsAdminOrAssignedDriverDeliveryProof
from .serializers import DeliveryProofSerializer, DeliveryProofStatusSerializer
from .services import find_proof_by_offline_id_for_user


class DeliveryProofViewSet(viewsets.ModelViewSet):
    queryset = DeliveryProof.objects.select_related("delivery_point", "delivery_point__route", "delivery_point__route__driver")
    serializer_class = DeliveryProofSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAssignedDriverDeliveryProof]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not (user.is_superuser or user.role == "ADMIN"):
            queryset = queryset.filter(delivery_point__route__driver=user)

        delivery_point_id = self.request.query_params.get("delivery_point")
        status_value = self.request.query_params.get("status")
        offline_id = self.request.query_params.get("offline_id")

        if delivery_point_id:
            queryset = queryset.filter(delivery_point_id=delivery_point_id)
        if status_value:
            queryset = queryset.filter(status=status_value)
        if offline_id:
            queryset = queryset.filter(offline_id=offline_id)

        return queryset

    def get_permissions(self):
        if self.action == "destroy":
            return [permissions.IsAuthenticated(), IsAdminRole()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        offline_id = request.data.get("offline_id")
        existing = find_proof_by_offline_id_for_user(request.user, offline_id)
        if existing:
            serializer = self.get_serializer(existing)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        delivery_point = serializer.validated_data["delivery_point"]

        if not (user.is_superuser or user.role == "ADMIN") and delivery_point.route.driver_id != user.id:
            raise PermissionDenied("No puede crear evidencias para rutas no asignadas.")

        offline_id = serializer.validated_data.get("offline_id")
        serializer.save(synced_from_offline=bool(offline_id))

    @action(detail=True, methods=["post"])
    def upload_evidence(self, request, pk=None):
        proof = self.get_object()
        payload = {
            "image": request.data.get("image", proof.image),
            "signature": request.data.get("signature", proof.signature),
        }

        serializer = self.get_serializer(proof, data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        proof = self.get_object()
        status_serializer = DeliveryProofStatusSerializer(data=request.data)
        status_serializer.is_valid(raise_exception=True)

        serializer = self.get_serializer(proof, data={"status": status_serializer.validated_data["status"]}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
