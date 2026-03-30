from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsAdmin
from .serializers import (
    CustomTokenObtainPairSerializer,
    EmpresaRegistroSerializer,
    MeSerializer,
    UsuarioCreateSerializer,
    UsuarioSerializer,
)

User = get_user_model()


class AuthRegisterAPIView(GenericAPIView):
    """Registra una empresa y su usuario ADMIN inicial."""

    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = EmpresaRegistroSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(
            {
                "empresa": {
                    "id": str(result["empresa"].id),
                    "nombre": result["empresa"].nombre,
                    "plan": result["empresa"].plan,
                },
                "user": UsuarioSerializer(result["user"]).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AuthLoginAPIView(TokenObtainPairView):
    """Login con JWT (access/refresh)."""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


class UsuarioViewSet(viewsets.ModelViewSet):
    """Gestion de usuarios por rol y empresa."""

    queryset = User.objects.all().order_by("-created_at")
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.action == "me":
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAdmin()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return queryset
        if not user.empresa_id:
            return queryset.none()
        return queryset.filter(empresa_id=user.empresa_id)

    def get_serializer_class(self):
        if self.action == "create":
            return UsuarioCreateSerializer
        if self.action == "me" and self.request.method == "PATCH":
            return MeSerializer
        return UsuarioSerializer

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        """Devuelve o actualiza el perfil del usuario autenticado."""

        if request.method == "GET":
            return Response(UsuarioSerializer(request.user).data)

        serializer = MeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UsuarioSerializer(request.user).data, status=status.HTTP_200_OK)
