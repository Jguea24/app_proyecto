from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.empresas.models import Empresa

User = get_user_model()


class EmpresaRegistroSerializer(serializers.Serializer):
    empresa_nombre = serializers.CharField(max_length=150)
    plan = serializers.ChoiceField(choices=Empresa.Plan.choices, default=Empresa.Plan.BASICO)
    email = serializers.EmailField()
    nombre = serializers.CharField(max_length=150)
    telefono = serializers.CharField(max_length=30, allow_blank=True, required=False)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        normalized = value.strip().lower()
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("El correo ya esta registrado.")
        return normalized

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.pop("confirm_password", None)

        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Las contrasenas no coinciden."})

        validate_password(password)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        empresa = Empresa.objects.create(
            nombre=validated_data["empresa_nombre"],
            plan=validated_data.get("plan", Empresa.Plan.BASICO),
        )
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            nombre=validated_data["nombre"],
            telefono=validated_data.get("telefono", ""),
            empresa=empresa,
            rol=User.Rol.ADMIN,
            is_staff=True,
            is_active=True,
        )
        return {"empresa": empresa, "user": user}


class UsuarioSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source="empresa.nombre", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "nombre",
            "telefono",
            "foto",
            "rol",
            "empresa",
            "empresa_nombre",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "nombre",
            "telefono",
            "foto",
            "rol",
            "is_active",
            "password",
            "confirm_password",
        )
        read_only_fields = ("id",)

    def validate_email(self, value):
        normalized = value.strip().lower()
        query = User.objects.filter(email__iexact=normalized)
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError("El correo ya esta registrado.")
        return normalized

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.pop("confirm_password", None)

        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Las contrasenas no coinciden."})

        validate_password(password)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        empresa = self.context["request"].user.empresa
        return User.objects.create_user(password=password, empresa=empresa, **validated_data)


class MeSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=False, max_length=150)
    telefono = serializers.CharField(required=False, max_length=30, allow_blank=True)
    foto = serializers.FileField(required=False, allow_null=True)
    new_password = serializers.CharField(write_only=True, required=False, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "nombre",
            "telefono",
            "foto",
            "rol",
            "empresa",
            "is_active",
            "new_password",
            "confirm_new_password",
        )
        read_only_fields = ("id", "email", "rol", "empresa", "is_active")

    def validate(self, attrs):
        new_password = attrs.pop("new_password", None)
        confirm_new_password = attrs.pop("confirm_new_password", None)

        if new_password or confirm_new_password:
            if new_password != confirm_new_password:
                raise serializers.ValidationError({"confirm_new_password": "Las contrasenas no coinciden."})
            validate_password(new_password)
            attrs["_new_password"] = new_password

        return attrs

    def update(self, instance, validated_data):
        new_password = validated_data.pop("_new_password", None)

        for field in ("nombre", "telefono", "foto"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        if new_password:
            instance.set_password(new_password)

        instance.save()
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["rol"] = user.rol
        token["empresa_id"] = str(user.empresa_id) if user.empresa_id else None
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UsuarioSerializer(self.user).data
        return data
