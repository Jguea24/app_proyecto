from django.contrib import admin

from .models import Pedido


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("cliente_nombre", "empresa", "estado", "created_at")
    list_filter = ("estado", "empresa")
    search_fields = ("cliente_nombre", "direccion")
