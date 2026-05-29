from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from auditoria.services.audit_service import auditar_apuesta_liquidada
from apuestas_core.models import Bet, BetSelection
from apuestas_core.state_machine import cambiar_estado_apuesta
from billetera.models import Account
from billetera.services.ledger_service import crear_movimiento_simple, normalizar_decimal
from config.choices import EstadoApuesta, EstadoEvento, TipoCuentaLedger, TipoTransaccionLedger


MARGEN_CASHOUT = Decimal("0.10")  # 10% fee de la casa al hacer cashout


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


def calcular_valor_cashout(bet) -> Decimal:
    """
    Calcula cuánto paga el cashout según el estado actual del partido.

    Fórmula:
      cashout = payout_potencial × (1 / cuota_actual) × (1 - margen)

    - Si el equipo va ganando  → cuota_actual baja  → cashout > stake
    - Si el equipo va perdiendo → cuota_actual sube  → cashout < stake
    - Si el partido no ha empezado → devuelve el stake (cashout pre-match)
    """
    selecciones = (
        BetSelection.objects
        .select_related('seleccion__odd', 'seleccion__mercado__evento')
        .filter(bet=bet)
    )

    if not selecciones.exists():
        return normalizar_decimal(bet.stake)

    bs = selecciones.first()
    evento = bs.seleccion.mercado.evento

    # Pre-match: devuelve stake completo
    if evento.estado == EstadoEvento.PROGRAMADO:
        return normalizar_decimal(bet.stake)

    # En vivo: fórmula dinámica
    try:
        cuota_actual = normalizar_decimal(bs.seleccion.odd.valor)
    except Exception:
        return normalizar_decimal(bet.stake)

    payout_potencial = normalizar_decimal(bet.payout_potencial)
    cashout_bruto = payout_potencial * (Decimal("1") / cuota_actual)
    cashout_neto = cashout_bruto * (Decimal("1") - MARGEN_CASHOUT)

    # Mínimo S/ 0.50 para no devolver cantidades ridículas
    return max(normalizar_decimal(cashout_neto), Decimal("0.5000"))


def es_cashout_disponible(bet, ahora=None) -> bool:
    """
    El cashout está disponible si la apuesta está ACCEPTED y el evento
    está PROGRAMADO (pre-match) o EN_VIVO.
    """
    if bet.estado != EstadoApuesta.ACCEPTED:
        return False

    if ahora is None:
        ahora = timezone.now()

    selecciones = list(
        BetSelection.objects
        .select_related('seleccion__mercado__evento')
        .filter(bet=bet)
    )
    if not selecciones:
        return False

    return all(
        sel.seleccion.mercado.evento.estado in (
            EstadoEvento.PROGRAMADO, EstadoEvento.EN_VIVO
        )
        and sel.seleccion.mercado.evento.activo
        for sel in selecciones
    )


@transaction.atomic
def cashout_apuesta(*, bet_id, idempotency_key=None, solicitado_por=None):
    bet = (
        Bet.objects
        .select_for_update()
        .select_related('usuario')
        .get(pk=bet_id)
    )

    if not es_cashout_disponible(bet):
        raise CashoutError("El cashout no está disponible para esta apuesta.")

    wallet_usuario = obtener_wallet_usuario(bet.usuario)
    cuenta_pendientes = obtener_cuenta_apuestas_pendientes()

    payout = calcular_valor_cashout(bet)

    # El payout no puede superar lo que hay bloqueado (el stake original)
    # si supera el stake, la diferencia sale de la cuenta casa
    stake = normalizar_decimal(bet.stake)

    if payout <= stake:
        # Cashout menor al stake: solo devolvemos parte de los fondos bloqueados
        movimiento = crear_movimiento_simple(
            cuenta_debito=cuenta_pendientes,
            cuenta_credito=wallet_usuario,
            amount=payout,
            tipo=TipoTransaccionLedger.CASHOUT,
            referencia=f"cashout_apuesta_{bet.id}",
            idempotency_key=idempotency_key,
            descripcion=f"Cashout en vivo (perdiendo): devuelve S/ {payout}",
            creado_por=solicitado_por,
        )
        # El resto del stake se queda en apuestas_pendientes hasta balancear
        # Lo movemos a la cuenta casa
        resto = stake - payout
        if resto > Decimal("0.0001"):
            from billetera.models import Account as Acc
            cuenta_casa = Acc.objects.select_for_update().filter(
                usuario__isnull=True,
                tipo=TipoCuentaLedger.CASA,
                activa=True,
            ).first()
            if cuenta_casa:
                crear_movimiento_simple(
                    cuenta_debito=cuenta_pendientes,
                    cuenta_credito=cuenta_casa,
                    amount=resto,
                    tipo=TipoTransaccionLedger.CASHOUT,
                    referencia=f"cashout_resto_{bet.id}",
                    descripcion="Resto de stake al hacer cashout perdiendo",
                    creado_por=solicitado_por,
                )
    else:
        # Cashout mayor al stake: devolvemos el stake de pendientes
        # y la ganancia extra sale de la cuenta casa
        from billetera.models import Account as Acc
        cuenta_casa = Acc.objects.select_for_update().filter(
            usuario__isnull=True,
            tipo=TipoCuentaLedger.CASA,
            activa=True,
        ).first()
        if not cuenta_casa:
            raise CashoutError("No existe cuenta de casa activa.")

        ganancia_extra = payout - stake

        movimiento = crear_movimiento_simple(
            cuenta_debito=cuenta_pendientes,
            cuenta_credito=wallet_usuario,
            amount=stake,
            tipo=TipoTransaccionLedger.CASHOUT,
            referencia=f"cashout_stake_{bet.id}",
            idempotency_key=idempotency_key,
            descripcion=f"Cashout en vivo (ganando): devuelve stake S/ {stake}",
            creado_por=solicitado_por,
        )
        crear_movimiento_simple(
            cuenta_debito=cuenta_casa,
            cuenta_credito=wallet_usuario,
            amount=ganancia_extra,
            tipo=TipoTransaccionLedger.CASHOUT,
            referencia=f"cashout_ganancia_{bet.id}",
            descripcion=f"Cashout en vivo (ganando): ganancia extra S/ {ganancia_extra}",
            creado_por=solicitado_por,
        )

    bet.payout_final = payout
    bet.liquidada_en = timezone.now()
    bet.save(update_fields=["payout_final", "liquidada_en", "fecha_actualizacion"])
    cambiar_estado_apuesta(bet, EstadoApuesta.CASHED_OUT)
    BetSelection.objects.filter(bet=bet).update(resultado="anulada")

    auditar_apuesta_liquidada(
        bet=bet,
        accion="cashed_out",
        creado_por=solicitado_por,
    )

    return bet, movimiento
