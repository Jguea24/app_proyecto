from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    ordering = ("email",)
    list_display = (
        "photo_preview",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "role",
        "address",
        "birth_date",
        "is_active",
        "created_at",
    )
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "first_name", "last_name", "address")
    readonly_fields = ("photo_preview", "created_at", "last_login", "date_joined")

    fieldsets = (
        (None, {"fields": ("email", "password")} ),
        ("Informacion personal", {"fields": ("first_name", "last_name", "photo", "photo_preview", "address", "birth_date")}),
        ("Permisos", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("created_at", "last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "photo",
                    "address",
                    "birth_date",
                    "role",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    @admin.display(description="FOTO")
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;" />', obj.photo.url)
        return "-"
