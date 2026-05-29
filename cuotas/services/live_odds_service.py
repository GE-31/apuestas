"""
Servicio de cuotas dinámicas para partidos En Vivo.

Lógica basada en apuestas reales:
- El equipo que va ganando tiene cuota más baja (probabilidad alta de ganar).
- El equipo que va perdiendo tiene cuota más alta (necesita remontar).
- En empate las cuotas se ajustan a un balance.
- Margen de casa del 6% aplicado sobre probabilidades justas.
"""
from decimal import Decimal

from config.choices import TipoMercado, TipoSeleccionMercado
from cuotas.models import Odd, OddHistory

MARGEN_CASA = Decimal("1.06")  # 6% overround en vivo

# Probabilidades base según diferencia de goles (local - visitante)
# Formato: (prob_local, prob_empate, prob_visitante)
_PROB_TABLE = {
    -4: (Decimal("0.03"), Decimal("0.07"), Decimal("0.90")),
    -3: (Decimal("0.05"), Decimal("0.09"), Decimal("0.86")),
    -2: (Decimal("0.09"), Decimal("0.15"), Decimal("0.76")),
    -1: (Decimal("0.19"), Decimal("0.24"), Decimal("0.57")),
     0: (Decimal("0.42"), Decimal("0.27"), Decimal("0.31")),
     1: (Decimal("0.61"), Decimal("0.23"), Decimal("0.16")),
     2: (Decimal("0.77"), Decimal("0.15"), Decimal("0.08")),
     3: (Decimal("0.86"), Decimal("0.09"), Decimal("0.05")),
     4: (Decimal("0.90"), Decimal("0.07"), Decimal("0.03")),
}


def _get_probs(diferencia: int):
    clamped = max(-4, min(4, diferencia))
    return _PROB_TABLE[clamped]


def calcular_cuotas_vivo(marcador_local: int, marcador_visitante: int) -> dict:
    """
    Calcula cuotas 1X2 dinámicas según el marcador actual.
    Retorna dict {tipo_seleccion: Decimal}.
    """
    diff = marcador_local - marcador_visitante
    pl, pe, pv = _get_probs(diff)

    def _odd(prob: Decimal) -> Decimal:
        raw = Decimal("1") / (prob * MARGEN_CASA)
        # Redondear a 2 decimales, mínimo 1.05
        rounded = raw.quantize(Decimal("0.01"))
        return max(Decimal("1.05"), rounded)

    return {
        TipoSeleccionMercado.LOCAL:     _odd(pl),
        TipoSeleccionMercado.EMPATE:    _odd(pe),
        TipoSeleccionMercado.VISITANTE: _odd(pv),
    }


def actualizar_cuotas_vivo(evento) -> dict:
    """
    Recalcula, guarda en DB y retorna las nuevas cuotas del mercado 1X2.

    Retorna dict {tipo_seleccion: float} listo para broadcast WebSocket,
    o dict vacío si el evento no tiene mercado 1X2 activo.
    """
    try:
        mercado = evento.mercados.select_related().get(
            tipo=TipoMercado.UNO_X_DOS,
            activo=True,
        )
    except Exception:
        return {}

    ml = evento.marcador_local or 0
    mv = evento.marcador_visitante or 0
    nuevas = calcular_cuotas_vivo(ml, mv)

    resultado = {}
    for seleccion in mercado.selecciones.select_related("odd").all():
        nuevo_valor = nuevas.get(seleccion.tipo)
        if nuevo_valor is None:
            continue

        try:
            odd = seleccion.odd
        except Odd.DoesNotExist:
            continue

        nuevo_decimal = nuevo_valor.quantize(Decimal("0.0001"))
        if odd.valor != nuevo_decimal:
            OddHistory.objects.create(
                odd=odd,
                valor_anterior=odd.valor,
                valor_nuevo=nuevo_decimal,
                motivo=f"Live update {ml}-{mv}",
            )
            odd.valor = nuevo_decimal
            odd.save(update_fields=["valor", "fecha_actualizacion"])

        resultado[seleccion.tipo] = float(odd.valor)

    return resultado
