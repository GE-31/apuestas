from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apuestas_core.models import Bet, BetSelection
from billetera.models import Account
from billetera.services.ledger_service import crear_movimiento_simple, normalizar_decimal
from billetera.services.saldo_service import validar_saldo_suficiente
from config.choices import (
    EstadoApuesta,
    EstadoCuenta,
    EstadoEvento,
    TipoApuesta,
    TipoCuentaLedger,
    TipoTransaccionLedger,
)
from cuotas.models import Odd
from juego_responsable.services.autoexclusion_service import validar_usuario_no_autoexcluido
from auditoria.services.audit_service import auditar_apuesta_creada

class ApuestaError(Exception):
    pass


MONTO_MINIMO_APUESTA = Decimal("1.0000")
MONTO_MAXIMO_APUESTA = Decimal("1000.0000")
MAX_SELECCIONES_COMBINADA = 12


def obtener_wallet_usuario(usuario):
    """
    Obtiene la wallet activa del usuario con bloqueo pesimista.
    """

    wallet = Account.objects.select_for_update().filter(
        usuario=usuario,
        tipo=TipoCuentaLedger.WALLET_USUARIO,
        activa=True,
    ).first()

    if not wallet:
        raise ApuestaError("El usuario no tiene una wallet activa.")

    return wallet


def obtener_cuenta_apuestas_pendientes():
    """
    Obtiene la cuenta del sistema donde se bloquean los fondos apostados.
    """

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
    Valida que el usuario pueda apostar.

    Reglas:
    - Debe tener perfil de apuestas.
    - Debe estar verificado.
    - No debe estar bloqueado.
    - No debe estar autoexcluido.
    """

    perfil = getattr(usuario, "perfil_apuestas", None)

    if not perfil:
        raise ApuestaError("El usuario no tiene perfil de apuestas.")

    if perfil.estado_cuenta != EstadoCuenta.VERIFICADO:
        raise ApuestaError("El usuario no está verificado o está bloqueado.")

    validar_usuario_no_autoexcluido(usuario)

    return True


def validar_monto_apuesta(stake):
    """
    Valida monto mínimo y máximo de apuesta.
    """

    stake = normalizar_decimal(stake)

    if stake < MONTO_MINIMO_APUESTA:
        raise ApuestaError(f"El monto mínimo de apuesta es {MONTO_MINIMO_APUESTA}.")

    if stake > MONTO_MAXIMO_APUESTA:
        raise ApuestaError(f"El monto máximo de apuesta es {MONTO_MAXIMO_APUESTA}.")

    return stake


def validar_odd_apostable(odd):
    """
    Valida que la cuota, selección, mercado y evento estén disponibles.
    """

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


def _obtener_odds_apostables_bloqueadas(odd_ids):
    odd_ids_unicos = list(dict.fromkeys(odd_ids))

    if len(odd_ids_unicos) != len(odd_ids):
        raise ApuestaError("La apuesta combinada no puede repetir cuotas.")

    odds = list(
        Odd.objects
        .select_for_update()
        .select_related(
            "seleccion",
            "seleccion__mercado",
            "seleccion__mercado__evento",
        )
        .filter(pk__in=odd_ids_unicos)
        .order_by("pk")
    )

    if len(odds) != len(odd_ids_unicos):
        raise ApuestaError("Una o más cuotas no existen.")

    eventos_usados = set()
    for odd in odds:
        validar_odd_apostable(odd)
        evento_id = odd.seleccion.mercado.evento_id
        if evento_id in eventos_usados:
            raise ApuestaError("La combinada no puede incluir más de una selección del mismo evento.")
        eventos_usados.add(evento_id)

    return odds


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
    1. Evita duplicados con idempotency_key.
    2. Valida usuario verificado y no autoexcluido.
    3. Valida monto.
    4. Valida odd, mercado y evento.
    5. Valida saldo suficiente.
    6. Bloquea fondos: wallet_usuario -> apuestas_pendientes.
    7. Crea Bet en estado accepted.
    8. Crea BetSelection con la cuota tomada.
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

    movimiento.referencia = f"apuesta_{apuesta.id}"
    movimiento.save(update_fields=["referencia"])

    auditar_apuesta_creada(
        bet=apuesta,
        creado_por=usuario,
        ip_origen=ip_origen,
    )

    # Análisis antifraude post-commit — nunca bloquea la apuesta
    _apuesta_id = apuesta.id
    transaction.on_commit(lambda: _ejecutar_antifraude(_apuesta_id))

    return apuesta


@transaction.atomic
def crear_apuesta_combinada(
    *,
    usuario,
    odd_ids,
    stake,
    idempotency_key=None,
    ip_origen=None,
):
    """
    Crea una apuesta combinada/múltiple.

    La cuota total es el producto de todas las cuotas tomadas. El stake se
    bloquea una sola vez con partida doble: wallet_usuario -> apuestas_pendientes.
    """

    if idempotency_key:
        apuesta_existente = Bet.objects.filter(
            idempotency_key=idempotency_key
        ).first()

        if apuesta_existente:
            return apuesta_existente

    if len(odd_ids) < 2:
        raise ApuestaError("Una apuesta combinada requiere al menos dos selecciones.")

    if len(odd_ids) > MAX_SELECCIONES_COMBINADA:
        raise ApuestaError(
            f"Una apuesta combinada permite máximo {MAX_SELECCIONES_COMBINADA} selecciones."
        )

    validar_usuario_puede_apostar(usuario)

    stake = validar_monto_apuesta(stake)
    odds = _obtener_odds_apostables_bloqueadas(odd_ids)

    wallet_usuario = obtener_wallet_usuario(usuario)
    cuenta_pendientes = obtener_cuenta_apuestas_pendientes()

    validar_saldo_suficiente(wallet_usuario, stake)

    odds_total = Decimal("1.0000")
    for odd in odds:
        odds_total *= normalizar_decimal(odd.valor)
    odds_total = normalizar_decimal(odds_total)
    payout_potencial = normalizar_decimal(stake * odds_total)

    movimiento = crear_movimiento_simple(
        cuenta_debito=wallet_usuario,
        cuenta_credito=cuenta_pendientes,
        amount=stake,
        tipo=TipoTransaccionLedger.BLOQUEO_APUESTA,
        referencia=f"bloqueo_apuesta_combinada_usuario_{usuario.id}",
        idempotency_key=f"bloqueo-{idempotency_key}" if idempotency_key else None,
        descripcion="Bloqueo de fondos por apuesta combinada aceptada",
        creado_por=usuario,
    )

    apuesta = Bet.objects.create(
        usuario=usuario,
        tipo=TipoApuesta.COMBINADA,
        estado=EstadoApuesta.ACCEPTED,
        stake=stake,
        odds_total=odds_total,
        payout_potencial=payout_potencial,
        idempotency_key=idempotency_key,
        ip_origen=ip_origen,
        aceptada_en=timezone.now(),
    )

    for odd in odds:
        BetSelection.objects.create(
            bet=apuesta,
            seleccion=odd.seleccion,
            odd=odd,
            odd_valor_tomado=normalizar_decimal(odd.valor),
            resultado="pendiente",
        )

    movimiento.referencia = f"apuesta_{apuesta.id}"
    movimiento.save(update_fields=["referencia"])

    auditar_apuesta_creada(
        bet=apuesta,
        creado_por=usuario,
        ip_origen=ip_origen,
    )

    _apuesta_id = apuesta.id
    transaction.on_commit(lambda: _ejecutar_antifraude(_apuesta_id))

    return apuesta


def _ejecutar_antifraude(bet_id):
    try:
        from antifraude.services.fraud_detection_service import analizar_apuesta
        analizar_apuesta(bet_id)
    except Exception:
        import logging
        logging.getLogger(__name__).exception(
            'Error en análisis antifraude para bet %s.', bet_id
        )
