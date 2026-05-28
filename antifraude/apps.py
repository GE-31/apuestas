"""
Configuracion de la aplicacion antifraude.
"""
from django.apps import AppConfig


class AntifraudeConfig(AppConfig):
    """
    Configuracion principal para la app antifraude.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'antifraude'
