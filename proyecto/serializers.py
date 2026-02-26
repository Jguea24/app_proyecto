from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import UserProfile


class RegisterSerializer(serializers.Serializer):
    nombre = serializers.CharField(label="Nombre", max_length=150)
    apellidos = serializers.CharField(label="Apellidos", max_length=150)
    correo = serializers.EmailField(label="Correo")
    fecha_nacimiento = serializers.DateField(
        label="Fecha nacimiento",
        input_formats=["%d/%m/%Y", "%Y-%m-%d"],
        format="%d/%m/%Y",
        style={"input_type": "date"},
    )
    direccion = serializers.CharField(label="Direccion", max_length=255)
    rol = serializers.ChoiceField(label="Rol", choices=UserProfile.ROLE_CHOICES)
    telefono = serializers.CharField(label="Telefono", max_length=20)
    contrasena = serializers.CharField(label="Contrasena", write_only=True, style={"input_type": "password"})
    confirmar_contrasena = serializers.CharField(
        label="Confirmar contrasena",
        write_only=True,
        style={"input_type": "password"},
    )

    def validate_correo(self, value):
        correo = value.strip().lower()
        if User.objects.filter(username=correo).exists() or User.objects.filter(email=correo).exists():
            raise serializers.ValidationError("El correo ya esta registrado.")
        return correo

    def validate(self, attrs):
        contrasena = attrs.get("contrasena")
        confirmar = attrs.get("confirmar_contrasena")
        if contrasena and confirmar and contrasena != confirmar:
            raise serializers.ValidationError({"confirmar_contrasena": "Las contrasenas no coinciden."})
        try:
            validate_password(contrasena)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"contrasena": exc.messages}) from exc
        return attrs

    def create(self, validated_data):
        email = validated_data["correo"]
        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data["contrasena"],
            first_name=validated_data["nombre"].strip(),
            last_name=validated_data["apellidos"].strip(),
        )
        UserProfile.objects.create(
            user=user,
            birth_date=validated_data["fecha_nacimiento"],
            address=validated_data["direccion"].strip(),
            role=validated_data["rol"].strip(),
            phone=validated_data["telefono"].strip(),
        )
        return user


class LoginSerializer(serializers.Serializer):
    correo = serializers.EmailField()
    contrasena = serializers.CharField()