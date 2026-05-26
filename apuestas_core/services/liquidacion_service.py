from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apuestas_core.models import Bet, BetSelection
from apuestas_core.state_machine import cambiar_estado_apuesta
from billetera.models import Account
from billetera.services.ledger_service import (
    crear_movimiento_simple,
    crear_transaccion_ledger,
    normalizar_decimal,
)
from config.choices import (
    EstadoApuesta,
    TipoCuentaLedger,
    TipoTransaccionLedger,
)


class LiquidacionError(Exception):
    pass


def obtener_wallet_usuario(usuario):
    wallet = Account.objects.select_for_update().filter(
        usuario=usuario,
        tipo=TipoCuentaLedger.WALLET_USUARIO,
        activa=True,
    ).first()

    if not wallet:
        raise LiquidacionError("El usuario no tiene una wallet activa.")

    return wallet


def obtener_cuenta_apuestas_pendientes():
    cuenta = Account.objects.select_for_update().filter(
        usuario__isnull=True,
        tipo=TipoCuentaLedger.APUESTAS_PENDIENTES,
        activa=True,
    ).first()

    if not cuenta:
        raise LiquidacionError("No existe una cuenta activa de apuestas pendientes.")

    return cuenta


def obtener_cuenta_casa():
    cuenta = Account.objects.select_for_update().filter(
        usuario__isnull=True,
        tipo=TipoCuentaLedger.CASA,
        activa=True,
    ).first()

    if not cuenta:
        raise LiquidacionError("No existe una cuenta activa de casa.")

    return cuenta


def validar_apuesta_liquidable(bet: Bet):
    if bet.estado != EstadoApuesta.ACCEPTED:
        raise LiquidacionError("Solo se pueden liquidar apuestas aceptadas.")

    return True


@transaction.atomic
def liquidar_apuesta_ganada(*, bet_id, idempotency_key=None, liquidado_por=None):
    """
    Liquida una apuesta ganadora.

    Ejemplo:
    stake = 10
    odds = 2.5
    payout_final = 25
    ganancia_extra = 15

    Movimiento contable correcto:
    DEBIT  10  apuestas_pendientes
    DEBIT  15  casa
    CREDIT 25  wallet_usuario

    Así la cuenta apuestas_pendientes no queda negativa.
    """

    bet = (
        Bet.objects
        .select_for_update()
        .select_related("usuario")
        .get(pk=bet_id)
    )

    validar_apuesta_liquidable(bet)

    wallet_usuario = obtener_wallet_usuario(bet.usuario)
    cuenta_pendientes = obtener_cuenta_apuestas_pendientes()
    cuenta_casa = obtener_cuenta_casa()

    stake = normalizar_decimal(bet.stake)
    payout_final = normalizar_decimal(bet.stake * bet.odds_total)
    ganancia_extra = normalizar_decimal(payout_final - stake)

    movimiento = crear_transaccion_ledger(
        tipo=TipoTransaccionLedger.LIQUIDACION_APUESTA,
        entries_data=[
            {
                "account": cuenta_pendientes,
                "amount": stake,
                "direction": "DEBIT",
                "descripcion": "Devolución del stake bloqueado por apuesta ganadora",
            },
            {
                "account": cuenta_casa,
                "amount": ganancia_extra,
                "direction": "DEBIT",
                "descripcion": "Pago de ganancia de apuesta ganadora",
            },
            {
                "account": wallet_usuario,
                "amount": payout_final,
                "direction": "CREDIT",
                "descripcion": "Liquidación de apuesta ganadora",
            },
        ],
        referencia=f"liquidacion_apuesta_{bet.id}",
        idempotency_key=idempotency_key,
        descripcion="Liquidación de apuesta ganadora",
        creado_por=liquidado_por,
    )

    bet.payout_final = payout_final
    bet.liquidada_en = timezone.now()
    bet.save(update_fields=["payout_final", "liquidada_en", "fecha_actualizacion"])

    cambiar_estado_apuesta(bet, EstadoApuesta.WON)

    BetSelection.objects.filter(bet=bet).update(resultado="ganada")

    return bet, movimiento


@transaction.atomic
def liquidar_apuesta_perdida(*, bet_id, idempotency_key=None, liquidado_por=None):
    """
    Liquida una apuesta perdedora.

    Movimiento contable:
    DEBIT  apuestas_pendientes
    CREDIT casa
    """

    bet = (
        Bet.objects
        .select_for_update()
        .select_related("usuario")
        .get(pk=bet_id)
    )

    validar_apuesta_liquidable(bet)

    cuenta_pendientes = obtener_cuenta_apuestas_pendientes()
    cuenta_casa = obtener_cuenta_casa()

    stake = normalizar_decimal(bet.stake)

    movimiento = crear_movimiento_simple(
        cuenta_debito=cuenta_pendientes,
        cuenta_credito=cuenta_casa,
        amount=stake,
        tipo=TipoTransaccionLedger.LIQUIDACION_APUESTA,
        referencia=f"liquidacion_apuesta_{bet.id}",
        idempotency_key=idempotency_key,
        descripcion="Liquidación de apuesta perdedora",
        creado_por=liquidado_por,
    )

    bet.payout_final = Decimal("0.0000")
    bet.liquidada_en = timezone.now()
    bet.save(update_fields=["payout_final", "liquidada_en", "fecha_actualizacion"])

    cambiar_estado_apuesta(bet, EstadoApuesta.LOST)

    BetSelection.objects.filter(bet=bet).update(resultado="perdida")

    return bet, movimiento


@transaction.atomic
def anular_apuesta(*, bet_id, idempotency_key=None, anulado_por=None):
    """
    Anula una apuesta aceptada.

    Movimiento contable:
    DEBIT  apuestas_pendientes
    CREDIT wallet_usuario
    """

    bet = (
        Bet.objects
        .select_for_update()
        .select_related("usuario")
        .get(pk=bet_id)
    )

    validar_apuesta_liquidable(bet)

    wallet_usuario = obtener_wallet_usuario(bet.usuario)
    cuenta_pendientes = obtener_cuenta_apuestas_pendientes()

    stake = normalizar_decimal(bet.stake)

    movimiento = crear_movimiento_simple(
        cuenta_debito=cuenta_pendientes,
        cuenta_credito=wallet_usuario,
        amount=stake,
        tipo=TipoTransaccionLedger.LIQUIDACION_APUESTA,
        referencia=f"anulacion_apuesta_{bet.id}",
        idempotency_key=idempotency_key,
        descripcion="Anulación de apuesta y devolución de stake",
        creado_por=anulado_por,
    )

    bet.payout_final = stake
    bet.liquidada_en = timezone.now()
    bet.save(update_fields=["payout_final", "liquidada_en", "fecha_actualizacion"])

    cambiar_estado_apuesta(bet, EstadoApuesta.VOID)

    BetSelection.objects.filter(bet=bet).update(resultado="anulada")

    return bet, movimiento