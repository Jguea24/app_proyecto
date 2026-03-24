from django.contrib import admin

from .models import Tracking


@admin.register(Tracking)
class TrackingAdmin(admin.ModelAdmin):
    list_display = ("driver", "latitude", "longitude", "timestamp")
    list_filter = ("driver",)
    search_fields = ("driver__email",)
