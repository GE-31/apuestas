from django.contrib import admin
from .models import Mercado, SeleccionMercado

# Register your models here.





class SeleccionMercadoInline(admin.TabularInline):
    model = SeleccionMercado
    extra = 3
    fields = (
        'tipo',
        'nombre',
        'activo',
    )


@admin.register(Mercado)
class MercadoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'evento',
        'tipo',
        'nombre',
        'activo',
        'suspendido',
        'fecha_creacion',
    )
    list_filter = (
        'tipo',
        'activo',
        'suspendido',
        'fecha_creacion',
    )
    search_fields = (
        'nombre',
        'evento__nombre',
        'evento__equipo_local__nombre',
        'evento__equipo_visitante__nombre',
    )
    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
    )
    ordering = (
        'evento',
        'tipo',
    )
    autocomplete_fields = (
        'evento',
    )
    inlines = [
        SeleccionMercadoInline,
    ]


@admin.register(SeleccionMercado)
class SeleccionMercadoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'mercado',
        'tipo',
        'nombre',
        'activo',
        'fecha_creacion',
    )
    list_filter = (
        'tipo',
        'activo',
        'fecha_creacion',
    )
    search_fields = (
        'nombre',
        'mercado__nombre',
        'mercado__evento__nombre',
    )
    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
    )
    ordering = (
        'mercado',
        'tipo',
    )
    autocomplete_fields = (
        'mercado',
    )