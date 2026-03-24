from django.contrib import admin

from .models import DeliveryPoint, Route


class DeliveryPointInline(admin.TabularInline):
    model = DeliveryPoint
    extra = 0


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "status", "driver")
    list_filter = ("status", "date")
    search_fields = ("name",)
    inlines = [DeliveryPointInline]


@admin.register(DeliveryPoint)
class DeliveryPointAdmin(admin.ModelAdmin):
    list_display = ("route", "order", "address", "status")
    list_filter = ("status", "route")
    search_fields = ("address",)
