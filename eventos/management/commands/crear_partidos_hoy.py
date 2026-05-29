"""
Crea 10 partidos de fútbol para hoy 28/05/2026 a las horas indicadas.
Cada partido tendrá mercado 1X2 con cuotas base.

Uso: python manage.py crear_partidos_hoy
"""

from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.timezone import make_aware

from cuotas.models import Odd
from eventos.models import Deporte, Equipo, Evento, Liga
from mercados.models import Mercado, SeleccionMercado


PARTIDOS = [
    # (local, visitante, liga_nombre, hora, minuto)
    ("Universitario de Deportes", "Alianza Lima",     "Liga 1 Perú",           18, 25),
    ("Sporting Cristal",      "Melgar",              "Liga 1 Perú",           18, 30),
    ("Cusco FC",              "Sport Huancayo",      "Liga 1 Perú",           19, 10),
    ("Deportivo Municipal",   "Cienciano",           "Liga 1 Perú",           19, 20),
    ("Sporting Cristal",      "Cienciano",           "Liga 1 Perú",           19, 30),
    ("Melgar",                "César Vallejo",       "Liga 1 Perú",           19, 40),
    ("Boca Juniors",          "River Plate",         "Copa Libertadores",     20,  0),
    ("América",               "Chivas",              "Liga MX",               20, 20),
    ("Flamengo",              "Palmeiras",           "Brasileirao",           20, 40),
    ("Barcelona SC",          "Emelec",              "Liga Pro Ecuador",      21,  0),
    ("Colo Colo",             "Universidad de Chile","Primera División Chile",21, 20),
    ("Nacional",              "Peñarol",             "Primera División Uruguay", 21, 40),
    ("Independiente",         "San Lorenzo",         "Liga Profesional Argentina", 22, 0),
]


def _get_or_create_odd(seleccion, valor):
    Odd.objects.get_or_create(
        seleccion=seleccion,
        defaults={
            'valor': Decimal(valor),
            'margen_operador': Decimal('0.0000'),
            'activa': True,
            'suspendida': False,
            'actualizada_por': None,
        },
    )


def _crear_mercado_1x2(evento):
    local     = evento.equipo_local.nombre
    visitante = evento.equipo_visitante.nombre

    mercado, _ = Mercado.objects.get_or_create(
        evento=evento,
        tipo='1x2',
        defaults={'nombre': 'Resultado final 1X2', 'activo': True, 'suspendido': False},
    )
    for tipo_sel, nombre_sel, cuota in [
        ('local',     f'Gana {local}',    '1.9000'),
        ('empate',    'Empate',           '3.3000'),
        ('visitante', f'Gana {visitante}','2.0500'),
    ]:
        sel, _ = SeleccionMercado.objects.get_or_create(
            mercado=mercado,
            tipo=tipo_sel,
            defaults={'nombre': nombre_sel, 'activo': True},
        )
        _get_or_create_odd(sel, cuota)


class Command(BaseCommand):
    help = 'Crea 10 partidos de fútbol para hoy con horarios de tarde/noche'

    def handle(self, *args, **options):
        deporte, _ = Deporte.objects.get_or_create(
            nombre='Fútbol',
            defaults={'descripcion': 'Fútbol profesional', 'activo': True},
        )

        hoy = timezone.localdate()
        creados = 0

        for local_nombre, visitante_nombre, liga_nombre, hora, minuto in PARTIDOS:
            liga, _ = Liga.objects.get_or_create(
                nombre=liga_nombre,
                defaults={'deporte': deporte, 'activa': True},
            )

            equipo_local, _ = Equipo.objects.get_or_create(
                nombre=local_nombre,
                deporte=deporte,
                defaults={'activo': True},
            )
            equipo_visitante, _ = Equipo.objects.get_or_create(
                nombre=visitante_nombre,
                deporte=deporte,
                defaults={'activo': True},
            )

            # make_aware convierte la hora LOCAL (Lima) a UTC correctamente
            fecha_local = make_aware(
                datetime(hoy.year, hoy.month, hoy.day, hora, minuto, 0)
            )

            nombre_evento = f'{local_nombre} vs {visitante_nombre}'
            evento, created = Evento.objects.get_or_create(
                equipo_local=equipo_local,
                equipo_visitante=equipo_visitante,
                fecha_inicio=fecha_local,
                defaults={
                    'deporte': deporte,
                    'liga': liga,
                    'nombre': nombre_evento,
                    'estado': 'programado',
                    'activo': True,
                },
            )

            if created:
                _crear_mercado_1x2(evento)
                creados += 1
                self.stdout.write(f'  + {nombre_evento}  {hora:02d}:{minuto:02d}')
            else:
                self.stdout.write(f'  ~ {nombre_evento} (ya existe)')

        self.stdout.write(self.style.SUCCESS(
            f'\n{creados} partidos creados. Se activarán automáticamente cuando llegue su hora.'
        ))
