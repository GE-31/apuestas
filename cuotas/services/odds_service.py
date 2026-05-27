from django.db import transaction

from auditoria.services.audit_service import auditar_cambio_cuota
from billetera.services.ledger_service import normalizar_decimal
from cuotas.models import Odd, OddHistory


class OddError(Exception):
    pass


def validar_valor_odd(valor):
    """
    Valida que la cuota decimal sea válida.

    Regla:
    - La cuota debe ser mayor que 1.
    - Se usa Decimal con 4 decimales.
    """

    valor = normalizar_decimal(valor)

    if valor <= 1:
        raise OddError("La cuota debe ser mayor que 1.0000.")

    return valor


def validar_margen_operador(margen):
    """
    Valida margen del operador.

    Regla:
    - No puede ser negativo.
    """

    margen = normalizar_decimal(margen)

    if margen < 0:
        raise OddError("El margen del operador no puede ser negativo.")

    return margen


@transaction.atomic
def actualizar_cuota(
    *,
    odd_id,
    nuevo_valor,
    margen_operador=None,
    motivo=None,
    cambiado_por=None,
    ip_origen=None,
    user_agent=None,
):
    """
    Actualiza una cuota y registra historial + auditoría.

    Flujo:
    1. Bloquea la cuota con select_for_update.
    2. Valida el nuevo valor.
    3. Guarda historial de cambio.
    4. Actualiza la cuota.
    5. Registra auditoría inmutable.
    """

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

    valor_anterior = odd.valor
    valor_nuevo = validar_valor_odd(nuevo_valor)

    if margen_operador is None:
        margen_nuevo = odd.margen_operador
    else:
        margen_nuevo = validar_margen_operador(margen_operador)

    if valor_anterior == valor_nuevo and odd.margen_operador == margen_nuevo:
        raise OddError("No hay cambios para actualizar en la cuota.")

    OddHistory.objects.create(
        odd=odd,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        margen_operador=margen_nuevo,
        motivo=motivo,
        cambiado_por=cambiado_por,
    )

    odd.valor = valor_nuevo
    odd.margen_operador = margen_nuevo

    if cambiado_por:
        odd.actualizada_por = cambiado_por

    odd.save(update_fields=[
        "valor",
        "margen_operador",
        "actualizada_por",
        "fecha_actualizacion",
    ])

    auditar_cambio_cuota(
        odd=odd,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        cambiado_por=cambiado_por,
        motivo=motivo,
        ip_origen=ip_origen,
        user_agent=user_agent,
    )

    return odd


@transaction.atomic
def suspender_cuota(
    *,
    odd_id,
    motivo=None,
    cambiado_por=None,
):
    """
    Suspende una cuota para que no pueda ser apostada.
    """

    odd = Odd.objects.select_for_update().get(pk=odd_id)

    odd.suspendida = True

    if cambiado_por:
        odd.actualizada_por = cambiado_por

    odd.save(update_fields=[
        "suspendida",
        "actualizada_por",
        "fecha_actualizacion",
    ])

    auditar_cambio_cuota(
        odd=odd,
        valor_anterior=odd.valor,
        valor_nuevo=odd.valor,
        cambiado_por=cambiado_por,
        motivo=motivo or "Cuota suspendida",
    )

    return odd


@transaction.atomic
def reactivar_cuota(
    *,
    odd_id,
    motivo=None,
    cambiado_por=None,
):
    """
    Reactiva una cuota suspendida.
    """

    odd = Odd.objects.select_for_update().get(pk=odd_id)

    odd.suspendida = False

    if cambiado_por:
        odd.actualizada_por = cambiado_por

    odd.save(update_fields=[
        "suspendida",
        "actualizada_por",
        "fecha_actualizacion",
    ])

    auditar_cambio_cuota(
        odd=odd,
        valor_anterior=odd.valor,
        valor_nuevo=odd.valor,
        cambiado_por=cambiado_por,
        motivo=motivo or "Cuota reactivada",
    )

    return odd