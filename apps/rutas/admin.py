from django.contrib import admin

from .models import ParadaRuta, Ruta


class ParadaRutaInline(admin.TabularInline):
    model = ParadaRuta
    extra = 0


@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ("id", "empresa", "repartidor", "fecha", "estado")
    list_filter = ("estado", "empresa")
    search_fields = ("id",)
    inlines = [ParadaRutaInline]


@admin.register(ParadaRuta)
class ParadaRutaAdmin(admin.ModelAdmin):
    list_display = ("ruta", "pedido", "orden", "estado")
    list_filter = ("estado",)
