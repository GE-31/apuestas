import logging

from antifraude.rules import (
    detectar_apuesta_alta,
    detectar_apuestas_repetidas_evento,
    detectar_muchas_apuestas_rapidas,
)
from antifraude.services.alert_service import crear_alerta_antifraude

logger = logging.getLogger(__name__)

REGLAS = [
    detectar_apuesta_alta,
    detectar_muchas_apuestas_rapidas,
    detectar_apuestas_repetidas_evento,
]


def analizar_apuesta(bet_id):
    """
    Ejecuta todas las reglas antifraude sobre la apuesta indicada.

    - Corre DESPUÉS de que la transacción de creación se commitea.
    - Nunca bloquea ni revierte la apuesta.
    - Registra FraudAlert por cada regla disparada.
    """
    from apuestas_core.models import Bet

    try:
        bet = (
            Bet.objects
            .select_related('usuario')
            .prefetch_related('selecciones__seleccion__mercado__evento')
            .get(pk=bet_id)
        )
    except Bet.DoesNotExist:
        logger.warning('analizar_apuesta: bet %s no encontrada.', bet_id)
        return

    for regla in REGLAS:
        try:
            resultado = regla(bet)
            if resultado:
                crear_alerta_antifraude(
                    usuario=bet.usuario,
                    bet=bet,
                    tipo_alerta=resultado['tipo'],
                    severidad=resultado['severidad'],
                    descripcion=resultado['descripcion'],
                    metadata=resultado.get('metadata', {}),
                )
                logger.info(
                    'Alerta antifraude [%s/%s] creada para usuario %s — bet %s.',
                    resultado['severidad'],
                    resultado['tipo'],
                    bet.usuario_id,
                    bet.id,
                )
        except Exception:
            logger.exception(
                'Error ejecutando regla antifraude %s para bet %s.',
                regla.__name__,
                bet_id,
            )
