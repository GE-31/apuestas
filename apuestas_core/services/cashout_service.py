from django.db import transaction
from django.utils import timezone

from apuestas_core.models import Bet, BetSelection
from apuestas_core.state_machine import cambiar_estado_apuesta
from billetera.models import Account
from billetera.services.ledger_service import crear_movimiento_simple, normalizar_decimal
from config.choices import EstadoApuesta, EstadoEvento, TipoCuentaLedger, TipoTransaccionLedger


class CashoutError(Exception):
    pass


def obtener_wallet_usuario(usuario):
    wallet = Account.objects.select_for_update().filter(
        usuario=usuario,
        tipo=TipoCuentaLedger.WALLET_USUARIO,
        activa=True,
    ).first()
    if not wallet:
        raise CashoutError("El usuario no tiene una wallet activa.")
    return wallet


def obtener_cuenta_apuestas_pendientes():
    cuenta = Account.objects.select_for_update().filter(
        usuario__isnull=True,
        tipo=TipoCuentaLedger.APUESTAS_PENDIENTES,
        activa=True,
    ).first()
    if not cuenta:
        raise CashoutError("No existe una cuenta activa de apuestas pendientes.")
    return cuenta


def validar_cashout_pre_match(bet):
    if bet.estado != EstadoApuesta.ACCEPTED:
        raise CashoutError("Solo se puede hacer cashout de apuestas activas.")

    selecciones = (
        BetSelection.objects
        .select_related('seleccion__mercado__evento')
        .filter(bet=bet)
    )
    if not selecciones.exists():
        raise CashoutError("La apuesta no tiene selecciones.")

    ahora = timezone.now()
    for bet_selection in selecciones:
        evento = bet_selection.seleccion.mercado.evento
        if evento.estado != EstadoEvento.PROGRAMADO or evento.fecha_inicio <= ahora:
            raise CashoutError("El cashout solo esta disponible antes de que empiece el partido.")


def calcular_oferta_cashout(bet):
    """Calcula la oferta de cashout para mostrar en la UI.

    Actualmente la oferta pre-match devuelve el `stake` normalizado.
    Esta función puede extenderse para ofrecer mejores cálculos.
    """
    # Validar condición mínima para que se muestre oferta
    try:
        validar_cashout_pre_match(bet)
    except CashoutError:
        return None

    return normalizar_decimal(bet.stake)


@transaction.atomic
def cashout_apuesta(*, bet_id, idempotency_key=None, solicitado_por=None):
    bet = (
        Bet.objects
        .select_for_update()
        .select_related('usuario')
        .get(pk=bet_id)
    )

    validar_cashout_pre_match(bet)

    wallet_usuario = obtener_wallet_usuario(bet.usuario)
    cuenta_pendientes = obtener_cuenta_apuestas_pendientes()
    payout = normalizar_decimal(bet.stake)

    movimiento = crear_movimiento_simple(
        cuenta_debito=cuenta_pendientes,
        cuenta_credito=wallet_usuario,
        amount=payout,
        tipo=TipoTransaccionLedger.CASHOUT,
        referencia=f"cashout_apuesta_{bet.id}",
        idempotency_key=idempotency_key,
        descripcion="Cashout pre-match: devolucion de stake",
        creado_por=solicitado_por,
    )

    bet.payout_final = payout
    bet.liquidada_en = timezone.now()
    bet.save(update_fields=["payout_final", "liquidada_en", "fecha_actualizacion"])
    cambiar_estado_apuesta(bet, EstadoApuesta.CASHED_OUT)
    BetSelection.objects.filter(bet=bet).update(resultado="anulada")

    return bet, movimiento
