from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from billetera.models import Account, LedgerEntry
from billetera.services.ledger_service import normalizar_decimal
from config.choices import TipoCuentaLedger, TipoTransaccionLedger
from juego_responsable.models import LimiteDeposito


class LimiteDepositoError(Exception):
    pass


COOLDOWN_AUMENTO_LIMITE_HORAS = 24


def obtener_o_crear_limite_deposito(usuario):
    """
    Obtiene o crea los límites de depósito del usuario.

    Si los límites están en 0, significa que aún no se configuraron.
    Para pruebas puedes configurar valores desde el admin.
    """

    limite, _created = LimiteDeposito.objects.get_or_create(
        usuario=usuario,
        defaults={
            "limite_diario": Decimal("100.0000"),
            "limite_semanal": Decimal("500.0000"),
            "limite_mensual": Decimal("1000.0000"),
        },
    )

    return limite


def obtener_wallet_usuario(usuario):
    wallet, _ = Account.objects.get_or_create(
        usuario=usuario,
        tipo=TipoCuentaLedger.WALLET_USUARIO,
        defaults={
            'nombre': f'Wallet de {usuario.username}',
            'activa': True,
        },
    )
    if not wallet.activa:
        raise LimiteDepositoError("El usuario no tiene una wallet activa.")
    return wallet


def obtener_total_recargado(usuario, fecha_inicio, fecha_fin):
    """
    Calcula cuánto recargó el usuario en un rango de fechas.

    Se calcula desde LedgerEntry, no desde saldo guardado.
    Solo cuenta créditos a la wallet por transacciones tipo RECARGA.
    """

    wallet = obtener_wallet_usuario(usuario)

    total = (
        LedgerEntry.objects
        .filter(
            account=wallet,
            direction="CREDIT",
            transaction__tipo=TipoTransaccionLedger.RECARGA,
            fecha_creacion__gte=fecha_inicio,
            fecha_creacion__lte=fecha_fin,
        )
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.0000")
    )

    return normalizar_decimal(total)


def obtener_inicio_dia(ahora=None):
    ahora = ahora or timezone.now()
    return ahora.replace(hour=0, minute=0, second=0, microsecond=0)


def obtener_inicio_semana(ahora=None):
    ahora = ahora or timezone.now()
    inicio_dia = obtener_inicio_dia(ahora)
    return inicio_dia - timezone.timedelta(days=inicio_dia.weekday())


def obtener_inicio_mes(ahora=None):
    ahora = ahora or timezone.now()
    return ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def validar_limite_deposito(usuario, amount):
    """
    Valida que una recarga no supere los límites diario, semanal ni mensual.
    """

    amount = normalizar_decimal(amount)
    ahora = timezone.now()

    limite = obtener_o_crear_limite_deposito(usuario)

    total_dia = obtener_total_recargado(
        usuario,
        obtener_inicio_dia(ahora),
        ahora,
    )

    total_semana = obtener_total_recargado(
        usuario,
        obtener_inicio_semana(ahora),
        ahora,
    )

    total_mes = obtener_total_recargado(
        usuario,
        obtener_inicio_mes(ahora),
        ahora,
    )

    if limite.limite_diario > 0 and total_dia + amount > limite.limite_diario:
        raise LimiteDepositoError(
            f"Límite diario excedido. Usado: {total_dia}, intento: {amount}, límite: {limite.limite_diario}"
        )

    if limite.limite_semanal > 0 and total_semana + amount > limite.limite_semanal:
        raise LimiteDepositoError(
            f"Límite semanal excedido. Usado: {total_semana}, intento: {amount}, límite: {limite.limite_semanal}"
        )

    if limite.limite_mensual > 0 and total_mes + amount > limite.limite_mensual:
        raise LimiteDepositoError(
            f"Límite mensual excedido. Usado: {total_mes}, intento: {amount}, límite: {limite.limite_mensual}"
        )

    return True


def obtener_resumen_limites_deposito(usuario, ahora=None):
    """
    Retorna el estado de uso de límites de depósito del usuario.
    """

    ahora = ahora or timezone.now()
    limite = obtener_o_crear_limite_deposito(usuario)

    periodos = [
        ("diario", "Límite diario", limite.limite_diario, obtener_inicio_dia(ahora)),
        ("semanal", "Límite semanal", limite.limite_semanal, obtener_inicio_semana(ahora)),
        ("mensual", "Límite mensual", limite.limite_mensual, obtener_inicio_mes(ahora)),
    ]

    resumen = []
    for key, label, limit_amount, fecha_inicio in periodos:
        usado = obtener_total_recargado(usuario, fecha_inicio, ahora)
        porcentaje = Decimal("0.0000")
        if limit_amount > 0:
            porcentaje = min((usado / limit_amount) * Decimal("100"), Decimal("100"))

        limite_alcanzado = limit_amount > 0 and usado >= limit_amount

        resumen.append({
            "key": key,
            "label": label,
            "usado": usado,
            "limite": limit_amount,
            "porcentaje": porcentaje.quantize(Decimal("0.01")),
            "progress_class": "limits-progress-fill-warn" if porcentaje >= Decimal("50") else "",
            "status": "MAX" if limite_alcanzado else "OK",
            "status_class": "limits-status-max" if limite_alcanzado else "limits-status-ok",
        })

    return resumen


@transaction.atomic
def solicitar_cambio_limites(
    *,
    usuario,
    limite_diario,
    limite_semanal,
    limite_mensual,
):
    """
    Cambia límites de depósito.

    Regla del reto:
    - Si el usuario baja límites, se aplica inmediatamente.
    - Si el usuario sube límites, se guarda como pendiente y se aplica después de 24h.
    """

    limite = obtener_o_crear_limite_deposito(usuario)

    nuevo_diario = normalizar_decimal(limite_diario)
    nuevo_semanal = normalizar_decimal(limite_semanal)
    nuevo_mensual = normalizar_decimal(limite_mensual)

    if nuevo_diario < 0 or nuevo_semanal < 0 or nuevo_mensual < 0:
        raise LimiteDepositoError("Los límites no pueden ser negativos.")

    ahora = timezone.now()
    requiere_cooldown = False

    # Diario
    if nuevo_diario <= limite.limite_diario:
        limite.limite_diario = nuevo_diario
        limite.cambio_pendiente_diario = None
    else:
        limite.cambio_pendiente_diario = nuevo_diario
        requiere_cooldown = True

    # Semanal
    if nuevo_semanal <= limite.limite_semanal:
        limite.limite_semanal = nuevo_semanal
        limite.cambio_pendiente_semanal = None
    else:
        limite.cambio_pendiente_semanal = nuevo_semanal
        requiere_cooldown = True

    # Mensual
    if nuevo_mensual <= limite.limite_mensual:
        limite.limite_mensual = nuevo_mensual
        limite.cambio_pendiente_mensual = None
    else:
        limite.cambio_pendiente_mensual = nuevo_mensual
        requiere_cooldown = True

    if requiere_cooldown:
        limite.aplicar_cambio_en = ahora + timezone.timedelta(
            hours=COOLDOWN_AUMENTO_LIMITE_HORAS
        )
    else:
        limite.aplicar_cambio_en = None

    limite.save()

    return limite


@transaction.atomic
def aplicar_cambios_pendientes_limites():
    """
    Aplica aumentos de límite cuando ya pasó el cooldown de 24h.
    Esta función luego puede ejecutarse desde Celery.
    """

    ahora = timezone.now()

    limites = LimiteDeposito.objects.filter(
        aplicar_cambio_en__isnull=False,
        aplicar_cambio_en__lte=ahora,
    )

    cantidad = 0

    for limite in limites:
        if limite.cambio_pendiente_diario is not None:
            limite.limite_diario = limite.cambio_pendiente_diario
            limite.cambio_pendiente_diario = None

        if limite.cambio_pendiente_semanal is not None:
            limite.limite_semanal = limite.cambio_pendiente_semanal
            limite.cambio_pendiente_semanal = None

        if limite.cambio_pendiente_mensual is not None:
            limite.limite_mensual = limite.cambio_pendiente_mensual
            limite.cambio_pendiente_mensual = None

        limite.aplicar_cambio_en = None
        limite.save()
        cantidad += 1

    return cantidad
