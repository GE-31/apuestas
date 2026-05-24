from django.contrib import admin
from .models import Deporte, Equipo, Evento, ResultadoEvento

# Register your models here.




@admin.register(Deporte)
class DeporteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'activo',
        'fecha_creacion',
    )
    list_filter = (
        'activo',
        'fecha_creacion',
    )
    search_fields = (
        'nombre',
        'descripcion',
    )
    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
    )
    ordering = (
        'nombre',
    )


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'abreviatura',
        'deporte',
        'pais',
        'activo',
    )
    list_filter = (
        'deporte',
        'pais',
        'activo',
    )
    search_fields = (
        'nombre',
        'abreviatura',
        'pais',
    )
    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
    )
    ordering = (
        'nombre',
    )


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'deporte',
        'equipo_local',
        'equipo_visitante',
        'estado',
        'fecha_inicio',
        'activo',
    )
    list_filter = (
        'estado',
        'deporte',
        'activo',
        'fecha_inicio',
    )
    search_fields = (
        'nombre',
        'equipo_local__nombre',
        'equipo_visitante__nombre',
        'deporte__nombre',
    )
    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
    )
    ordering = (
        'fecha_inicio',
    )
    autocomplete_fields = (
        'deporte',
        'equipo_local',
        'equipo_visitante',
    )


@admin.register(ResultadoEvento)
class ResultadoEventoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'evento',
        'marcador_local',
        'marcador_visitante',
        'resultado_1x2',
        'registrado_por',
        'fecha_registro',
    )
    list_filter = (
        'resultado_1x2',
        'fecha_registro',
    )
    search_fields = (
        'evento__nombre',
        'evento__equipo_local__nombre',
        'evento__equipo_visitante__nombre',
    )
    readonly_fields = (
        'fecha_registro',
    )
    ordering = (
        '-fecha_registro',
    )
    autocomplete_fields = (
        'evento',
        'registrado_por',
    )