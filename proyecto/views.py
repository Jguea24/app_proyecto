from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import LoginSerializer, RegisterSerializer


class RegisterAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"ok": False, "error": "Datos invalidos.", "details": serializer.errors}, status=400)

        user = serializer.save()
        return Response(
            {
                "ok": True,
                "user_id": user.id,
                "correo": user.email,
                "nombre": user.first_name,
                "apellidos": user.last_name,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"ok": False, "error": "Datos invalidos.", "details": serializer.errors}, status=400)

        email = serializer.validated_data["correo"]
        password = serializer.validated_data["contrasena"]
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response({"ok": False, "error": "Credenciales invalidas."}, status=401)

        return Response(
            {
                "ok": True,
                "user_id": user.id,
                "correo": user.email,
                "nombre": user.first_name,
                "apellidos": user.last_name,
            }
        )