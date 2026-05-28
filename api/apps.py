"""
Configuracion de la aplicacion api.
"""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    Configuracion principal para la app api.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
