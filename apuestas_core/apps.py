"""
Configuracion de la aplicacion apuestas_core.
"""
from django.apps import AppConfig


class ApuestasCoreConfig(AppConfig):
    """
    Configuracion principal para la app apuestas_core.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apuestas_core'
