from rest_framework import serializers

from .models import Empresa


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ("id", "nombre", "plan", "activa", "fecha_creacion")
        read_only_fields = ("id", "fecha_creacion")
