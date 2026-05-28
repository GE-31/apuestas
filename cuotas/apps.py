"""
Configuracion de la aplicacion cuotas.
"""
from django.apps import AppConfig


class CuotasConfig(AppConfig):
    """
    Configuracion principal para la app cuotas.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cuotas'
