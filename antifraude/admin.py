from django.contrib import admin
from .models import FraudAlert


@admin.register(FraudAlert)
class FraudAlertAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'usuario', 'tipo_alerta', 'severidad',
        'estado', 'bet_id', 'fecha_creacion',
    )
    list_filter  = ('tipo_alerta', 'severidad', 'estado', 'fecha_creacion')
    search_fields = ('usuario__username', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'metadata')
    ordering = ('-fecha_creacion',)

    fieldsets = (
        ('Identificación', {
            'fields': ('usuario', 'bet', 'tipo_alerta', 'severidad', 'estado'),
        }),
        ('Detalle', {
            'fields': ('descripcion', 'metadata'),
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario', 'bet')
