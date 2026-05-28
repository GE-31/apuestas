"""
Configuracion de la aplicacion billetera.
"""
from django.apps import AppConfig


class BilleteraConfig(AppConfig):
    """
    Configuracion principal para la app billetera.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'billetera'
