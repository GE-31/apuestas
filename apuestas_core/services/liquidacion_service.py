from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apuestas_core.models import Bet, BetSelection
from apuestas_core.state_machine import cambiar_estado_apuesta
from billetera.models import Account
from billetera.services.ledger_service import crear_movimiento_simple, normalizar_decimal
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

    Movimiento contable:
    apuestas_pendientes -> wallet_usuario

    Nota:
    - payout_final = stake * odds_total
    - La cuenta apuestas_pendientes entrega el pago final a la wallet.
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

    payout_final = normalizar_decimal(bet.stake * bet.odds_total)

    movimiento = crear_movimiento_simple(
        cuenta_debito=cuenta_pendientes,
        cuenta_credito=wallet_usuario,
        amount=payout_final,
        tipo=TipoTransaccionLedger.LIQUIDACION_APUESTA,
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
    apuestas_pendientes -> casa

    Nota:
    - payout_final = 0
    - La casa recibe el stake bloqueado.
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
    Anula una apuesta aceptada y devuelve el stake al usuario.

    Movimiento contable:
    apuestas_pendientes -> wallet_usuario
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