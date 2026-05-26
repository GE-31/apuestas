from django.contrib import admin
from .models import AuditIntegrityCheck, AuditLog
# Register your models here.

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tipo_evento',
        'entidad',
        'entidad_id',
        'accion',
        'creado_por',
        'fecha_creacion',
    )
    list_filter = (
        'tipo_evento',
        'entidad',
        'accion',
        'fecha_creacion',
    )
    search_fields = (
        'entidad',
        'entidad_id',
        'accion',
        'current_hash',
        'previous_hash',
    )
    readonly_fields = (
        'tipo_evento',
        'entidad',
        'entidad_id',
        'accion',
        'payload',
        'previous_hash',
        'current_hash',
        'creado_por',
        'ip_origen',
        'user_agent',
        'fecha_creacion',
    )
    ordering = (
        '-fecha_creacion',
    )

    def has_add_permission(self, request):
        """
        La auditoría debe ser append-only desde services/,
        no creada manualmente desde admin.
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        No permitir edición manual para mantener integridad.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        No permitir eliminación manual.
        """
        return False


@admin.register(AuditIntegrityCheck)
class AuditIntegrityCheckAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'es_valida',
        'total_registros',
        'ejecutado_por',
        'fecha_ejecucion',
    )
    list_filter = (
        'es_valida',
        'fecha_ejecucion',
    )
    search_fields = (
        'ejecutado_por__username',
        'ejecutado_por__email',
    )
    readonly_fields = (
        'ejecutado_por',
        'es_valida',
        'total_registros',
        'errores_detectados',
        'fecha_ejecucion',
    )
    ordering = (
        '-fecha_ejecucion',
    )

    def has_add_permission(self, request):
        """
        Las verificaciones deben generarse desde el servicio de auditoría.
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        No permitir edición manual del resultado.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        No permitir eliminación manual.
        """
        return False