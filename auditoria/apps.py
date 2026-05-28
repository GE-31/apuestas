"""
Configuracion de la aplicacion auditoria.
"""
from django.apps import AppConfig


class AuditoriaConfig(AppConfig):
    """
    Configuracion principal para la app auditoria.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auditoria'
