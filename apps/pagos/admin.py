from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "cliente_nombre", "payment_method", "status", "amount", "created_at")
    list_filter = ("payment_method", "status")
    search_fields = ("transaction_reference", "order__id", "order__cliente_nombre")
    ordering = ("-created_at",)
    readonly_fields = ("cliente_nombre", "created_at", "updated_at")

    fieldsets = (
        ("Pedido", {"fields": ("order", "cliente_nombre")}),
        ("Pago", {"fields": ("payment_method", "status", "amount")}),
        (
            "Transferencia",
            {
                "fields": (
                    "bank_name",
                    "account_number",
                    "transaction_reference",
                    "transfer_receipt",
                    "transfer_date",
                )
            },
        ),
        ("Efectivo", {"fields": ("cash_received", "change_given", "confirmed_by")}),
        ("Fechas", {"fields": ("created_at", "updated_at")}),
    )

    def cliente_nombre(self, obj):
        return obj.order.cliente_nombre if obj.order else "-"

    cliente_nombre.short_description = "Cliente"
