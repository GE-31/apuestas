from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from billetera.models import Account, LedgerEntry, LedgerTransaction
from config.choices import DireccionLedger, TipoTransaccionLedger


class LedgerError(Exception):
    pass


def normalizar_decimal(valor):
    """
    Convierte un valor a Decimal con 4 decimales.
    No usar float para montos.
    """
    return Decimal(str(valor)).quantize(Decimal("0.0001"))


def calcular_total_entries(entries_data):
    """
    Calcula la suma contable:
    CREDIT suma positivo.
    DEBIT suma negativo.

    Para que la transacción esté balanceada, el resultado debe ser 0.
    """
    total = Decimal("0.0000")

    for entry in entries_data:
        amount = normalizar_decimal(entry["amount"])
        direction = entry["direction"]

        if amount <= 0:
            raise LedgerError("El monto debe ser mayor a cero.")

        if direction == DireccionLedger.CREDIT:
            total += amount
        elif direction == DireccionLedger.DEBIT:
            total -= amount
        else:
            raise LedgerError("Dirección ledger inválida.")

    return total.quantize(Decimal("0.0001"))


def validar_entries_balanceadas(entries_data):
    """
    Valida que una operación tenga mínimo dos entradas
    y que la suma global sea cero.
    """
    if len(entries_data) < 2:
        raise LedgerError("Una transacción ledger debe tener al menos dos entradas.")

    total = calcular_total_entries(entries_data)

    if total != Decimal("0.0000"):
        raise LedgerError("La transacción ledger no está balanceada.")

    return True


@transaction.atomic
def crear_transaccion_ledger(
    *,
    tipo,
    entries_data,
    referencia=None,
    idempotency_key=None,
    descripcion=None,
    creado_por=None,
):
    """
    Crea una transacción ledger con sus entradas.

    entries_data ejemplo:
    [
        {
            "account": cuenta_origen,
            "amount": Decimal("100.0000"),
            "direction": DireccionLedger.DEBIT,
            "descripcion": "Salida de fichas"
        },
        {
            "account": cuenta_destino,
            "amount": Decimal("100.0000"),
            "direction": DireccionLedger.CREDIT,
            "descripcion": "Ingreso de fichas"
        }
    ]

    Importante:
    - Aquí sí va lógica de negocio.
    - Usa transaction.atomic().
    - Valida partida doble.
    - Usa idempotency_key para evitar duplicados.
    """

    if idempotency_key:
        transaccion_existente = LedgerTransaction.objects.filter(
            idempotency_key=idempotency_key
        ).first()

        if transaccion_existente:
            return transaccion_existente

    validar_entries_balanceadas(entries_data)

    transaccion_ledger = LedgerTransaction.objects.create(
        tipo=tipo,
        referencia=referencia,
        idempotency_key=idempotency_key,
        descripcion=descripcion,
        creado_por=creado_por,
    )

    for entry in entries_data:
        account = Account.objects.select_for_update().get(pk=entry["account"].pk)

        LedgerEntry.objects.create(
            transaction=transaccion_ledger,
            account=account,
            amount=normalizar_decimal(entry["amount"]),
            direction=entry["direction"],
            descripcion=entry.get("descripcion", ""),
        )

    return transaccion_ledger


def verificar_transaccion_balanceada(transaccion_ledger):
    """
    Verifica si una transacción ya creada está balanceada.
    Sirve para auditoría o tests.
    """
    total_credit = (
        LedgerEntry.objects
        .filter(
            transaction=transaccion_ledger,
            direction=DireccionLedger.CREDIT,
        )
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.0000")
    )

    total_debit = (
        LedgerEntry.objects
        .filter(
            transaction=transaccion_ledger,
            direction=DireccionLedger.DEBIT,
        )
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.0000")
    )

    return normalizar_decimal(total_credit) == normalizar_decimal(total_debit)


def crear_movimiento_simple(
    *,
    cuenta_debito,
    cuenta_credito,
    amount,
    tipo=TipoTransaccionLedger.TRANSFERENCIA,
    referencia=None,
    idempotency_key=None,
    descripcion=None,
    creado_por=None,
):
    """
    Crea un movimiento simple de partida doble:
    una cuenta se debita y otra se acredita.
    """

    amount = normalizar_decimal(amount)

    entries_data = [
        {
            "account": cuenta_debito,
            "amount": amount,
            "direction": DireccionLedger.DEBIT,
            "descripcion": descripcion or "Débito de fichas virtuales",
        },
        {
            "account": cuenta_credito,
            "amount": amount,
            "direction": DireccionLedger.CREDIT,
            "descripcion": descripcion or "Crédito de fichas virtuales",
        },
    ]

    return crear_transaccion_ledger(
        tipo=tipo,
        entries_data=entries_data,
        referencia=referencia,
        idempotency_key=idempotency_key,
        descripcion=descripcion,
        creado_por=creado_por,
    )