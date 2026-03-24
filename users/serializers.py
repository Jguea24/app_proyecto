from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "photo",
            "is_staff",
            "role",
            "address",
            "birth_date",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class AuthRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    photo = serializers.FileField(required=False, allow_null=True)
    address = serializers.CharField(max_length=255, allow_blank=True, required=False, default="")
    birth_date = serializers.DateField(required=False, allow_null=True)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        normalized = value.strip().lower()
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("El correo ya esta registrado.")
        return normalized

    def validate_birth_date(self, value):
        if value and value > timezone.localdate():
            raise serializers.ValidationError("La fecha de nacimiento no puede ser futura.")
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.pop("confirm_password", None)

        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Las contrasenas no coinciden."})

        validate_password(password)
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            photo=validated_data.get("photo"),
            address=validated_data.get("address", ""),
            birth_date=validated_data.get("birth_date"),
            password=validated_data["password"],
            role=User.Role.DRIVER,
            is_active=True,
        )


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "photo",
            "is_staff",
            "role",
            "address",
            "birth_date",
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

    def validate_birth_date(self, value):
        if value and value > timezone.localdate():
            raise serializers.ValidationError("La fecha de nacimiento no puede ser futura.")
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.pop("confirm_password", None)

        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Las contrasenas no coinciden."})

        validate_password(password)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class MeSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    photo = serializers.FileField(required=False, allow_null=True)
    address = serializers.CharField(required=False, max_length=255, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    new_password = serializers.CharField(write_only=True, required=False, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "photo",
            "role",
            "address",
            "birth_date",
            "is_active",
            "new_password",
            "confirm_new_password",
        )
        read_only_fields = ("id", "email", "role", "is_active")

    def validate_birth_date(self, value):
        if value and value > timezone.localdate():
            raise serializers.ValidationError("La fecha de nacimiento no puede ser futura.")
        return value

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

        for field in ("first_name", "last_name", "photo", "address", "birth_date"):
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
        token["role"] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
