from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "payment_method", "status", "amount", "created_at")
    list_filter = ("payment_method", "status")
    search_fields = ("transaction_reference", "order__id")
    ordering = ("-created_at",)
