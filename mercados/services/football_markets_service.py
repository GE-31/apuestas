from decimal import Decimal

from config.choices import TipoMercado, TipoSeleccionMercado
from cuotas.models import Odd
from mercados.models import Mercado, SeleccionMercado


SELECTION_ORDER = {
    TipoSeleccionMercado.LOCAL: 10,
    TipoSeleccionMercado.EMPATE: 20,
    TipoSeleccionMercado.VISITANTE: 30,
    TipoSeleccionMercado.LOCAL_EMPATE: 40,
    TipoSeleccionMercado.LOCAL_VISITANTE: 50,
    TipoSeleccionMercado.EMPATE_VISITANTE: 60,
    TipoSeleccionMercado.OVER_05: 70,
    TipoSeleccionMercado.UNDER_05: 80,
    TipoSeleccionMercado.OVER_15: 90,
    TipoSeleccionMercado.UNDER_15: 100,
    TipoSeleccionMercado.OVER_25: 110,
    TipoSeleccionMercado.UNDER_25: 120,
    TipoSeleccionMercado.OVER_35: 130,
    TipoSeleccionMercado.UNDER_35: 140,
    TipoSeleccionMercado.AMBOS_SI: 150,
    TipoSeleccionMercado.AMBOS_NO: 160,
    TipoSeleccionMercado.EXACT_0: 170,
    TipoSeleccionMercado.EXACT_1: 180,
    TipoSeleccionMercado.EXACT_2: 190,
    TipoSeleccionMercado.EXACT_3: 200,
    TipoSeleccionMercado.EXACT_4_PLUS: 210,
}


def ordered_selections(selecciones):
    return sorted(
        selecciones,
        key=lambda seleccion: SELECTION_ORDER.get(seleccion.tipo, 999),
    )


def ensure_default_football_markets(evento, user=None):
    """Create a practical soccer market set for a simulated sportsbook event."""
    local = evento.equipo_local.nombre
    visitante = evento.equipo_visitante.nombre

    market_specs = [
        (
            TipoMercado.OVER_UNDER_05,
            'Goles totales Mas/Menos 0.5',
            [
                (TipoSeleccionMercado.OVER_05, 'Mas de 0.5 goles', Decimal('1.08')),
                (TipoSeleccionMercado.UNDER_05, 'Menos de 0.5 goles', Decimal('7.50')),
            ],
        ),
        (
            TipoMercado.OVER_UNDER_15,
            'Goles totales Mas/Menos 1.5',
            [
                (TipoSeleccionMercado.OVER_15, 'Mas de 1.5 goles', Decimal('1.35')),
                (TipoSeleccionMercado.UNDER_15, 'Menos de 1.5 goles', Decimal('3.10')),
            ],
        ),
        (
            TipoMercado.OVER_UNDER_25,
            'Goles totales Mas/Menos 2.5',
            [
                (TipoSeleccionMercado.OVER_25, 'Mas de 2.5 goles', Decimal('1.85')),
                (TipoSeleccionMercado.UNDER_25, 'Menos de 2.5 goles', Decimal('1.95')),
            ],
        ),
        (
            TipoMercado.OVER_UNDER_35,
            'Goles totales Mas/Menos 3.5',
            [
                (TipoSeleccionMercado.OVER_35, 'Mas de 3.5 goles', Decimal('3.20')),
                (TipoSeleccionMercado.UNDER_35, 'Menos de 3.5 goles', Decimal('1.33')),
            ],
        ),
        (
            TipoMercado.DOUBLE_CHANCE,
            'Doble oportunidad',
            [
                (TipoSeleccionMercado.LOCAL_EMPATE, f'{local} o Empate', Decimal('1.35')),
                (TipoSeleccionMercado.LOCAL_VISITANTE, f'{local} o {visitante}', Decimal('1.28')),
                (TipoSeleccionMercado.EMPATE_VISITANTE, f'Empate o {visitante}', Decimal('1.55')),
            ],
        ),
        (
            TipoMercado.DRAW_NO_BET,
            'Apuesta sin empate',
            [
                (TipoSeleccionMercado.LOCAL, local, Decimal('1.70')),
                (TipoSeleccionMercado.VISITANTE, visitante, Decimal('2.10')),
            ],
        ),
        (
            TipoMercado.BTTS,
            'Ambos equipos anotan',
            [
                (TipoSeleccionMercado.AMBOS_SI, 'Si', Decimal('1.90')),
                (TipoSeleccionMercado.AMBOS_NO, 'No', Decimal('1.85')),
            ],
        ),
        (
            TipoMercado.EXACT_GOALS,
            'Cantidad exacta de goles',
            [
                (TipoSeleccionMercado.EXACT_0, '0 goles', Decimal('9.00')),
                (TipoSeleccionMercado.EXACT_1, '1 gol', Decimal('4.50')),
                (TipoSeleccionMercado.EXACT_2, '2 goles', Decimal('3.40')),
                (TipoSeleccionMercado.EXACT_3, '3 goles', Decimal('4.20')),
                (TipoSeleccionMercado.EXACT_4_PLUS, '4+ goles', Decimal('3.80')),
            ],
        ),
    ]

    for tipo, nombre, selections in market_specs:
        mercado, _ = Mercado.objects.get_or_create(
            evento=evento,
            tipo=tipo,
            defaults={
                'nombre': nombre,
                'activo': True,
                'suspendido': False,
            },
        )
        for sel_tipo, sel_nombre, odd_valor in selections:
            seleccion, _ = SeleccionMercado.objects.get_or_create(
                mercado=mercado,
                tipo=sel_tipo,
                defaults={
                    'nombre': sel_nombre,
                    'activo': True,
                },
            )
            Odd.objects.get_or_create(
                seleccion=seleccion,
                defaults={
                    'valor': odd_valor,
                    'margen_operador': 0,
                    'activa': True,
                    'suspendida': False,
                    'actualizada_por': user,
                },
            )
