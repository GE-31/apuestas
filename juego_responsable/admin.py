from django.contrib import admin
from .models import Autoexclusion, LimiteDeposito, MensajeJuegoResponsable
# Register your models here.

@admin.register(LimiteDeposito)
class LimiteDepositoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'usuario',
        'limite_diario',
        'limite_semanal',
        'limite_mensual',
        'aplicar_cambio_en',
        'fecha_actualizacion',
    )
    list_filter = (
        'aplicar_cambio_en',
        'fecha_creacion',
        'fecha_actualizacion',
    )
    search_fields = (
        'usuario__username',
        'usuario__email',
    )
    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
    )
    ordering = (
        'usuario',
    )
    autocomplete_fields = (
        'usuario',
    )


@admin.register(Autoexclusion)
class AutoexclusionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'usuario',
        'estado',
        'duracion',
        'fecha_inicio',
        'fecha_fin',
        'creada_por',
    )
    list_filter = (
        'estado',
        'duracion',
        'fecha_inicio',
        'fecha_fin',
    )
    search_fields = (
        'usuario__username',
        'usuario__email',
        'motivo',
    )
    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
    )
    ordering = (
        '-fecha_inicio',
    )
    autocomplete_fields = (
        'usuario',
        'creada_por',
    )


@admin.register(MensajeJuegoResponsable)
class MensajeJuegoResponsableAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'titulo',
        'ubicacion',
        'activo',
        'fecha_actualizacion',
    )
    list_filter = (
        'activo',
        'ubicacion',
        'fecha_creacion',
    )
    search_fields = (
        'titulo',
        'mensaje',
        'ubicacion',
    )
    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
    )
    ordering = (
        'ubicacion',
        'titulo',
    )