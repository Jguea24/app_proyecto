from django.contrib import admin

from .models import DeliveryProof


@admin.register(DeliveryProof)
class DeliveryProofAdmin(admin.ModelAdmin):
    list_display = ("id", "delivery_point", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("delivery_point__address",)
    readonly_fields = ("created_at",)
