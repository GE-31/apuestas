"""
Auto-liquidación de apuestas al finalizar un evento.

Determina el resultado 1X2 por el marcador final y liquida
todas las apuestas ACCEPTED vinculadas al evento.
"""
from django.utils import timezone

from apuestas_core.models import Bet, BetSelection
from apuestas_core.services.liquidacion_service import (
    liquidar_apuesta_ganada,
    liquidar_apuesta_perdida,
)
from config.choices import EstadoApuesta


def _resultado_1x2(marcador_local: int, marcador_visitante: int) -> str:
    if marcador_local > marcador_visitante:
        return 'local'
    if marcador_visitante > marcador_local:
        return 'visitante'
    return 'empate'


def autoliquidar_evento(evento, liquidado_por=None):
    """
    Liquida todas las apuestas ACCEPTED del evento según el marcador final.
    Retorna (ganadas, perdidas) como conteo.
    """
    ml = evento.marcador_local or 0
    mv = evento.marcador_visitante or 0
    resultado = _resultado_1x2(ml, mv)

    # Todas las BetSelections pendientes vinculadas a este evento
    selecciones = (
        BetSelection.objects
        .filter(
            seleccion__mercado__evento=evento,
            bet__estado=EstadoApuesta.ACCEPTED,
        )
        .select_related('bet__usuario', 'seleccion')
        .order_by('bet_id')
    )

    ganadas = perdidas = 0
    bets_procesadas = set()

    for bs in selecciones:
        bet = bs.bet
        if bet.id in bets_procesadas:
            continue
        bets_procesadas.add(bet.id)

        ikey = f'autoliq-{evento.id}-{bet.id}-{int(timezone.now().timestamp())}'
        try:
            if bs.seleccion.tipo == resultado:
                liquidar_apuesta_ganada(
                    bet_id=bet.id,
                    idempotency_key=ikey,
                    liquidado_por=liquidado_por,
                )
                ganadas += 1
            else:
                liquidar_apuesta_perdida(
                    bet_id=bet.id,
                    idempotency_key=ikey,
                    liquidado_por=liquidado_por,
                )
                perdidas += 1
        except Exception:
            pass

    return ganadas, perdidas, resultado
