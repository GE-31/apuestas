from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apuestas_core.models import Bet, BetSelection
from config.choices import (
    EstadoApuesta,
    EstadoCuenta,
    EstadoEvento,
    TipoApuesta,
    TipoCuentaLedger,
    TipoTransaccionLedger,
)
from cuotas.models import Odd
from billetera.models import Account
from billetera.services.ledger_service import crear_movimiento_simple, normalizar_decimal
from billetera.services.saldo_service import validar_saldo_suficiente


class ApuestaError(Exception):
    pass


MONTO_MINIMO_APUESTA = Decimal("1.0000")
MONTO_MAXIMO_APUESTA = Decimal("1000.0000")


def obtener_wallet_usuario(usuario):
    wallet = Account.objects.select_for_update().filter(
        usuario=usuario,
        tipo=TipoCuentaLedger.WALLET_USUARIO,
        activa=True,
    ).first()

    if not wallet:
        raise ApuestaError("El usuario no tiene una wallet activa.")

    return wallet


def obtener_cuenta_apuestas_pendientes():
    cuenta = Account.objects.select_for_update().filter(
        usuario__isnull=True,
        tipo=TipoCuentaLedger.APUESTAS_PENDIENTES,
        activa=True,
    ).first()

    if not cuenta:
        raise ApuestaError("No existe una cuenta activa de apuestas pendientes.")

    return cuenta


def validar_usuario_puede_apostar(usuario):
    """
    Valida KYC y estado de cuenta.

    La lógica de KYC se hizo en usuarios.
    Aquí solo consumimos el estado resultante.
    """

    perfil = getattr(usuario, "perfil_apuestas", None)

    if not perfil:
        raise ApuestaError("El usuario no tiene perfil de apuestas.")

    if perfil.estado_cuenta != EstadoCuenta.VERIFICADO:
        raise ApuestaError("El usuario no está verificado o está bloqueado.")

    return True


def validar_monto_apuesta(stake):
    stake = normalizar_decimal(stake)

    if stake < MONTO_MINIMO_APUESTA:
        raise ApuestaError(f"El monto mínimo de apuesta es {MONTO_MINIMO_APUESTA}.")

    if stake > MONTO_MAXIMO_APUESTA:
        raise ApuestaError(f"El monto máximo de apuesta es {MONTO_MAXIMO_APUESTA}.")

    return stake


def validar_odd_apostable(odd):
    seleccion = odd.seleccion
    mercado = seleccion.mercado
    evento = mercado.evento

    if not odd.activa or odd.suspendida:
        raise ApuestaError("La cuota no está disponible.")

    if not seleccion.activo:
        raise ApuestaError("La selección no está activa.")

    if not mercado.activo or mercado.suspendido:
        raise ApuestaError("El mercado no está disponible.")

    if evento.estado != EstadoEvento.PROGRAMADO:
        raise ApuestaError("El evento ya inició o no está disponible para apuesta pre-match.")

    return True


@transaction.atomic
def crear_apuesta_simple(
    *,
    usuario,
    odd_id,
    stake,
    idempotency_key=None,
    ip_origen=None,
):
    """
    Crea una apuesta simple.

    Flujo:
    1. Valida usuario verificado.
    2. Valida odd, mercado y evento.
    3. Valida saldo suficiente.
    4. Bloquea fondos: wallet_usuario -> apuestas_pendientes.
    5. Crea Bet en estado accepted.
    6. Crea BetSelection con la cuota tomada.
    """

    if idempotency_key:
        apuesta_existente = Bet.objects.filter(
            idempotency_key=idempotency_key
        ).first()

        if apuesta_existente:
            return apuesta_existente

    validar_usuario_puede_apostar(usuario)

    stake = validar_monto_apuesta(stake)

    odd = (
        Odd.objects
        .select_for_update()
        .select_related(
            "seleccion",
            "seleccion__mercado",
            "seleccion__mercado__evento",
        )
        .get(pk=odd_id)
    )

    validar_odd_apostable(odd)

    wallet_usuario = obtener_wallet_usuario(usuario)
    cuenta_pendientes = obtener_cuenta_apuestas_pendientes()

    validar_saldo_suficiente(wallet_usuario, stake)

    odds_total = normalizar_decimal(odd.valor)
    payout_potencial = normalizar_decimal(stake * odds_total)

    movimiento = crear_movimiento_simple(
        cuenta_debito=wallet_usuario,
        cuenta_credito=cuenta_pendientes,
        amount=stake,
        tipo=TipoTransaccionLedger.BLOQUEO_APUESTA,
        referencia=f"bloqueo_apuesta_usuario_{usuario.id}",
        idempotency_key=f"bloqueo-{idempotency_key}" if idempotency_key else None,
        descripcion="Bloqueo de fondos por apuesta aceptada",
        creado_por=usuario,
    )

    apuesta = Bet.objects.create(
        usuario=usuario,
        tipo=TipoApuesta.SIMPLE,
        estado=EstadoApuesta.ACCEPTED,
        stake=stake,
        odds_total=odds_total,
        payout_potencial=payout_potencial,
        idempotency_key=idempotency_key,
        ip_origen=ip_origen,
        aceptada_en=timezone.now(),
    )

    BetSelection.objects.create(
        bet=apuesta,
        seleccion=odd.seleccion,
        odd=odd,
        odd_valor_tomado=odds_total,
        resultado="pendiente",
    )

    # Se deja la referencia del movimiento con el ID real de la apuesta.
    movimiento.referencia = f"apuesta_{apuesta.id}"
    movimiento.save(update_fields=["referencia"])

    return apuesta