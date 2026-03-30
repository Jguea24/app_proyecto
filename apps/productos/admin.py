from django.contrib import admin
from django.utils.html import format_html

from .models import Carrito, CarritoItem, Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "empresa", "precio", "stock", "activo", "foto_preview")
    list_filter = ("empresa", "activo")
    search_fields = ("nombre",)
    readonly_fields = ("foto_preview",)

    @admin.display(description="Foto")
    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="height:60px;width:60px;object-fit:cover;border-radius:6px;" />',
                obj.foto.url,
            )
        return "-"


class CarritoItemInline(admin.TabularInline):
    model = CarritoItem
    extra = 0


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "empresa", "updated_at")
    list_filter = ("empresa",)
    inlines = [CarritoItemInline]


@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ("carrito", "producto", "cantidad", "precio_unitario")
