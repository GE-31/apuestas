from django.contrib import admin
from .models import PerfilUsuario, VerificacionKYC
# Register your models here.

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'dni',
        'apellidos',
        'nombres',
        'estado_cuenta',
        'fecha_registro',
    )
    list_filter = (
        'estado_cuenta',
        'fecha_registro',
    )
    search_fields = (
        'dni',
        'nombres',
        'apellidos',
        'usuario__username',
        'usuario__email',
    )
    readonly_fields = (
        'fecha_registro',
        'fecha_actualizacion',
    )
    ordering = (
        'apellidos',
        'nombres',
    )


@admin.register(VerificacionKYC)
class VerificacionKYCAdmin(admin.ModelAdmin):
    list_display = (
        'perfil',
        'dni_verificado',
        'mayor_edad_verificado',
        'verificado_por',
        'fecha_verificacion',
    )
    list_filter = (
        'dni_verificado',
        'mayor_edad_verificado',
        'fecha_verificacion',
    )
    search_fields = (
        'perfil__dni',
        'perfil__nombres',
        'perfil__apellidos',
    )
    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
    )
    ordering = (
        '-fecha_creacion',
    )