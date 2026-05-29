"""
Borra los partidos de hoy creados con hora incorrecta y los vuelve a crear.
Uso: python manage.py resetear_partidos_hoy
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone

from eventos.models import Evento

NOMBRES_PARTIDOS = [
    "Alianza Lima vs Universitario",
    "Universitario de Deportes vs Alianza Lima",
    "Sporting Cristal vs Cienciano",
    "Melgar vs César Vallejo",
    "Boca Juniors vs River Plate",
    "América vs Chivas",
    "Flamengo vs Palmeiras",
    "Barcelona SC vs Emelec",
    "Colo Colo vs Universidad de Chile",
    "Nacional vs Peñarol",
    "Independiente vs San Lorenzo",
]


class Command(BaseCommand):
    help = 'Borra y recrea los partidos de hoy con la hora correcta (Lima)'

    def handle(self, *args, **options):
        eliminados = Evento.objects.filter(nombre__in=NOMBRES_PARTIDOS).delete()
        self.stdout.write(f'Partidos eliminados: {eliminados[0]}')

        call_command('crear_partidos_hoy')
