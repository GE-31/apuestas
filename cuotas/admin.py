from django.contrib import admin
from .models import Odd, OddHistory

# Register your models here.




class OddHistoryInline(admin.TabularInline):
    model = OddHistory
    extra = 0
    readonly_fields = (
        'valor_anterior',
        'valor_nuevo',
        'margen_operador',
        'motivo',
        'cambiado_por',
        'fecha_cambio',
    )
    can_delete = False


@admin.register(Odd)
class OddAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'seleccion',
        'valor',
        'margen_operador',
        'activa',
        'suspendida',
        'fecha_actualizacion',
    )
    list_filter = (
        'activa',
        'suspendida',
        'fecha_creacion',
        'fecha_actualizacion',
    )
    search_fields = (
        'seleccion__nombre',
        'seleccion__mercado__nombre',
        'seleccion__mercado__evento__nombre',
    )
    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
    )
    ordering = (
        'seleccion',
    )
    autocomplete_fields = (
        'seleccion',
        'actualizada_por',
    )
    inlines = [
        OddHistoryInline,
    ]


@admin.register(OddHistory)
class OddHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'odd',
        'valor_anterior',
        'valor_nuevo',
        'margen_operador',
        'cambiado_por',
        'fecha_cambio',
    )
    list_filter = (
        'fecha_cambio',
    )
    search_fields = (
        'odd__seleccion__nombre',
        'odd__seleccion__mercado__nombre',
        'odd__seleccion__mercado__evento__nombre',
        'motivo',
    )
    readonly_fields = (
        'fecha_cambio',
    )
    ordering = (
        '-fecha_cambio',
    )
    autocomplete_fields = (
        'odd',
        'cambiado_por',
    )