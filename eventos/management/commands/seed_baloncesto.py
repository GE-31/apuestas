"""
Comando para poblar datos de prueba de Baloncesto:
  Deporte → 2 Ligas → 8 Equipos → 5 Eventos → Mercados → Cuotas
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from eventos.models import Deporte, Equipo, Evento, Liga
from mercados.models import Mercado, SeleccionMercado
from cuotas.models import Odd


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


def _crear_mercados_evento(evento):
    local = evento.equipo_local.nombre
    visitante = evento.equipo_visitante.nombre

    specs = [
        ('1x2', f'Resultado final 1X2', [
            ('local',     f'Gana {local}',    '1.8500'),
            ('empate',    'Empate',            '3.5000'),
            ('visitante', f'Gana {visitante}', '2.1000'),
        ]),
        ('over_under_25', 'Puntos Mas/Menos 2.5', [
            ('over_25', 'Mas de 2.5',  '1.3500'),
            ('under_25', 'Menos de 2.5', '2.9000'),
        ]),
        ('double_chance', 'Doble oportunidad', [
            ('local_empate',     f'{local} o Empate',      '1.2500'),
            ('local_visitante',  f'{local} o {visitante}', '1.1500'),
            ('empate_visitante', f'Empate o {visitante}',  '1.4000'),
        ]),
        ('draw_no_bet', 'Apuesta sin empate', [
            ('local',     local,     '1.6500'),
            ('visitante', visitante, '2.2500'),
        ]),
        ('btts', 'Ambos equipos anotan', [
            ('ambos_si', 'Si', '1.7500'),
            ('ambos_no', 'No', '2.0000'),
        ]),
    ]

    for tipo_mercado, nombre_mercado, selecciones in specs:
        mercado, _ = Mercado.objects.get_or_create(
            evento=evento,
            tipo=tipo_mercado,
            defaults={'nombre': nombre_mercado, 'activo': True, 'suspendido': False},
        )
        for tipo_sel, nombre_sel, cuota in selecciones:
            seleccion, _ = SeleccionMercado.objects.get_or_create(
                mercado=mercado,
                tipo=tipo_sel,
                defaults={'nombre': nombre_sel, 'activo': True},
            )
            _get_or_create_odd(seleccion, cuota)


class Command(BaseCommand):
    help = 'Crea datos de prueba para el deporte Baloncesto (NBA + Liga ACB)'

    def handle(self, *args, **options):
        self.stdout.write('Creando deporte: Baloncesto...')

        deporte, _ = Deporte.objects.get_or_create(
            nombre='Baloncesto',
            defaults={'descripcion': 'Baloncesto profesional y amateur', 'activo': True},
        )

        # ── Ligas ────────────────────────────────────────────────────────────
        nba, _ = Liga.objects.get_or_create(
            nombre='NBA',
            defaults={'deporte': deporte, 'pais': 'Estados Unidos', 'activa': True},
        )
        acb, _ = Liga.objects.get_or_create(
            nombre='Liga ACB',
            defaults={'deporte': deporte, 'pais': 'España', 'activa': True},
        )
        self.stdout.write('  Ligas: NBA, Liga ACB')

        # ── Equipos NBA ───────────────────────────────────────────────────────
        equipos_nba = [
            ('Los Angeles Lakers',    'LAL', 'Estados Unidos'),
            ('Golden State Warriors', 'GSW', 'Estados Unidos'),
            ('Boston Celtics',        'BOS', 'Estados Unidos'),
            ('Miami Heat',            'MIA', 'Estados Unidos'),
            ('Chicago Bulls',         'CHI', 'Estados Unidos'),
            ('Milwaukee Bucks',       'MIL', 'Estados Unidos'),
        ]
        equipos_acb = [
            ('Real Madrid Baloncesto', 'RMB', 'España'),
            ('FC Barcelona Basket',    'FCB', 'España'),
            ('Valencia Basket',        'VAL', 'España'),
            ('Baskonia',               'BAS', 'España'),
        ]

        eq = {}
        for nombre, abrev, pais in equipos_nba + equipos_acb:
            equipo, _ = Equipo.objects.get_or_create(
                nombre=nombre,
                deporte=deporte,
                defaults={'abreviatura': abrev, 'pais': pais, 'activo': True},
            )
            eq[nombre] = equipo

        self.stdout.write(f'  Equipos: {len(eq)} creados/encontrados')

        # ── Eventos (fechas futuras para pruebas) ────────────────────────────
        now = timezone.now()
        base = now.replace(hour=20, minute=0, second=0, microsecond=0)

        partidos = [
            # NBA
            (eq['Los Angeles Lakers'],    eq['Golden State Warriors'], nba,  0),
            (eq['Boston Celtics'],        eq['Miami Heat'],            nba,  1),
            (eq['Chicago Bulls'],         eq['Milwaukee Bucks'],       nba,  2),
            # ACB
            (eq['Real Madrid Baloncesto'], eq['FC Barcelona Basket'],  acb,  1),
            (eq['Valencia Basket'],        eq['Baskonia'],             acb,  3),
        ]

        eventos_creados = 0
        for local, visitante, liga, dias_offset in partidos:
            fecha = base + timezone.timedelta(days=dias_offset, hours=dias_offset)
            nombre_evento = f'{local.nombre} vs {visitante.nombre}'

            evento, created = Evento.objects.get_or_create(
                equipo_local=local,
                equipo_visitante=visitante,
                defaults={
                    'deporte': deporte,
                    'liga': liga,
                    'nombre': nombre_evento,
                    'estado': 'programado',
                    'fecha_inicio': fecha,
                    'activo': True,
                },
            )

            if created:
                _crear_mercados_evento(evento)
                eventos_creados += 1
                self.stdout.write(f'    + {nombre_evento} ({fecha.strftime("%d/%m %H:%M")})')
            else:
                self.stdout.write(f'    ~ {nombre_evento} (ya existe)')

        self.stdout.write(self.style.SUCCESS(
            f'\nBaloncesto listo: {eventos_creados} eventos nuevos, '
            f'5 mercados x evento (1X2, Over/Under, Doble oportunidad, Sin empate, BTTS).'
        ))
