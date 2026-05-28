from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

STAKE_UMBRAL_ALTA          = Decimal('100.0000')
LIMITE_APUESTAS_RAPIDAS    = 5
VENTANA_RAPIDAS_MINUTOS    = 10
LIMITE_APUESTAS_MISMO_EVENTO = 3


def detectar_apuesta_alta(bet):
    """Alerta media si stake >= S/ 100."""
    if bet.stake >= STAKE_UMBRAL_ALTA:
        return {
            'tipo': 'apuesta_alta',
            'severidad': 'media',
            'descripcion': (
                f'Apuesta de monto alto: S/ {bet.stake} '
                f'(umbral: S/ {STAKE_UMBRAL_ALTA}).'
            ),
            'metadata': {
                'stake':   str(bet.stake),
                'umbral':  str(STAKE_UMBRAL_ALTA),
                'bet_id':  bet.id,
            },
        }
    return None


def detectar_muchas_apuestas_rapidas(bet):
    """Alerta alta si el usuario tiene >= 5 apuestas en los últimos 10 minutos."""
    from apuestas_core.models import Bet

    ventana = timezone.now() - timedelta(minutes=VENTANA_RAPIDAS_MINUTOS)
    count = (
        Bet.objects
        .filter(usuario=bet.usuario, fecha_creacion__gte=ventana)
        .count()
    )

    if count >= LIMITE_APUESTAS_RAPIDAS:
        return {
            'tipo': 'muchas_apuestas_rapidas',
            'severidad': 'alta',
            'descripcion': (
                f'{count} apuestas realizadas en los últimos '
                f'{VENTANA_RAPIDAS_MINUTOS} minutos.'
            ),
            'metadata': {
                'count':             count,
                'ventana_minutos':   VENTANA_RAPIDAS_MINUTOS,
                'bet_id':            bet.id,
            },
        }
    return None


def detectar_apuestas_repetidas_evento(bet):
    """Alerta media si el usuario tiene >= 3 apuestas al mismo evento."""
    from apuestas_core.models import Bet

    primera_sel = (
        bet.selecciones
        .select_related('seleccion__mercado__evento')
        .first()
    )
    if not primera_sel:
        return None

    evento_id = primera_sel.seleccion.mercado.evento_id

    count = (
        Bet.objects
        .filter(
            usuario=bet.usuario,
            selecciones__seleccion__mercado__evento_id=evento_id,
        )
        .distinct()
        .count()
    )

    if count >= LIMITE_APUESTAS_MISMO_EVENTO:
        return {
            'tipo': 'apuestas_repetidas_evento',
            'severidad': 'media',
            'descripcion': (
                f'{count} apuestas del usuario al mismo evento '
                f'(ID: {evento_id}).'
            ),
            'metadata': {
                'count':     count,
                'evento_id': evento_id,
                'bet_id':    bet.id,
            },
        }
    return None
