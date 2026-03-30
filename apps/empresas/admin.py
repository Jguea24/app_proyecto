from django.contrib import admin

from .models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "plan", "activa", "fecha_creacion")
    search_fields = ("nombre",)
    list_filter = ("plan", "activa")
