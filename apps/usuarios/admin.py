from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(DjangoUserAdmin):
    model = Usuario
    list_display = ("email", "nombre", "rol", "empresa", "foto_preview", "is_active", "is_staff")
    list_filter = ("rol", "is_active")
    ordering = ("email",)
    search_fields = ("email", "nombre")
    readonly_fields = ("created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informacion personal", {"fields": ("nombre", "telefono", "foto", "empresa", "rol")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "nombre", "rol", "empresa", "password1", "password2"),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj=obj)

    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="height:36px;width:36px;object-fit:cover;border-radius:4px;" />',
                obj.foto.url,
            )
        return "-"

    foto_preview.short_description = "Foto"
