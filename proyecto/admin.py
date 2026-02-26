from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0


class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "get_role",
        "get_phone",
        "get_address",
        "get_birth_date",
    )
    inlines = (UserProfileInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("userprofile")

    def _profile(self, obj):
        try:
            return obj.userprofile
        except UserProfile.DoesNotExist:
            return None

    def get_role(self, obj):
        profile = self._profile(obj)
        return profile.role if profile else "-"

    get_role.short_description = "Role"

    def get_phone(self, obj):
        profile = self._profile(obj)
        return profile.phone if profile else "-"

    get_phone.short_description = "Telefono"

    def get_address(self, obj):
        profile = self._profile(obj)
        return profile.address if profile else "-"

    get_address.short_description = "Direccion"

    def get_birth_date(self, obj):
        profile = self._profile(obj)
        return profile.birth_date if profile else "-"

    get_birth_date.short_description = "Fecha nacimiento"


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "birth_date", "address", "role", "phone")