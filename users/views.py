from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsAdminRole
from .serializers import (
    AuthRegisterSerializer,
    CustomTokenObtainPairSerializer,
    MeSerializer,
    UserCreateSerializer,
    UserSerializer,
)

User = get_user_model()


class AuthRegisterAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = AuthRegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"ok": True, "user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class AuthLoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-created_at")
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "me":
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAdminRole()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "me" and self.request.method == "PATCH":
            return MeSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get("role")
        is_active = self.request.query_params.get("is_active")

        if role:
            queryset = queryset.filter(role=role)

        if is_active is not None:
            normalized = is_active.strip().lower()
            if normalized in {"true", "1", "yes"}:
                queryset = queryset.filter(is_active=True)
            elif normalized in {"false", "0", "no"}:
                queryset = queryset.filter(is_active=False)

        return queryset

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        if request.method == "GET":
            return Response(UserSerializer(request.user).data)

        serializer = MeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
