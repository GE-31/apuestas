from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction

from billetera.models import LedgerEntry, LedgerTransaction


class LedgerError(Exception):
    pass


DECIMAL_PLACES = Decimal("0.0001")


def normalizar_decimal(valor):
    """
    Normaliza montos a 4 decimales.
    No usar float para montos.
    """

    if not isinstance(valor, Decimal):
        valor = Decimal(str(valor))

    return valor.quantize(DECIMAL_PLACES, rounding=ROUND_HALF_UP)


def validar_amount(amount):
    amount = normalizar_decimal(amount)

    if amount <= 0:
        raise LedgerError("El monto debe ser mayor que cero.")

    return amount


def validar_entries_balanceadas(entries_data):
    """
    Valida partida doble.

    Reglas:
    - Mínimo 2 entradas.
    - Todo amount debe ser positivo.
    - La suma de DEBIT debe ser igual a la suma de CREDIT.
    """

    if len(entries_data) < 2:
        raise LedgerError("Una transacción ledger requiere mínimo dos entradas.")

    total_debit = Decimal("0.0000")
    total_credit = Decimal("0.0000")

    for entry in entries_data:
        amount = validar_amount(entry["amount"])
        direction = entry["direction"]

        if direction == "DEBIT":
            total_debit += amount
        elif direction == "CREDIT":
            total_credit += amount
        else:
            raise LedgerError("Dirección inválida. Use DEBIT o CREDIT.")

    total_debit = normalizar_decimal(total_debit)
    total_credit = normalizar_decimal(total_credit)

    if total_debit != total_credit:
        raise LedgerError(
            f"Transacción no balanceada. DEBIT={total_debit}, CREDIT={total_credit}"
        )

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
    Crea una transacción ledger con partida doble.

    También registra auditoría inmutable del movimiento.

    entries_data ejemplo:
    [
        {
            "account": cuenta_origen,
            "amount": Decimal("10.0000"),
            "direction": "DEBIT",
            "descripcion": "..."
        },
        {
            "account": cuenta_destino,
            "amount": Decimal("10.0000"),
            "direction": "CREDIT",
            "descripcion": "..."
        }
    ]
    """

    if idempotency_key:
        transaccion_existente = LedgerTransaction.objects.filter(
            idempotency_key=idempotency_key
        ).first()

        if transaccion_existente:
            return transaccion_existente

    validar_entries_balanceadas(entries_data)

    ledger_transaction = LedgerTransaction.objects.create(
        tipo=tipo,
        referencia=referencia,
        idempotency_key=idempotency_key,
        descripcion=descripcion,
        creado_por=creado_por,
    )

    for entry in entries_data:
        LedgerEntry.objects.create(
            transaction=ledger_transaction,
            account=entry["account"],
            amount=normalizar_decimal(entry["amount"]),
            direction=entry["direction"],
            descripcion=entry.get("descripcion") or descripcion,
        )

    # Import aquí para evitar problemas de import circular.
    from auditoria.services.audit_service import auditar_movimiento_wallet

    auditar_movimiento_wallet(
        transaction=ledger_transaction,
        creado_por=creado_por,
    )

    return ledger_transaction


def crear_movimiento_simple(
    *,
    cuenta_debito,
    cuenta_credito,
    amount,
    tipo,
    referencia=None,
    idempotency_key=None,
    descripcion=None,
    creado_por=None,
):
    """
    Crea un movimiento simple de dos entradas:

    DEBIT  cuenta_debito
    CREDIT cuenta_credito
    """

    amount = validar_amount(amount)

    entries_data = [
        {
            "account": cuenta_debito,
            "amount": amount,
            "direction": "DEBIT",
            "descripcion": descripcion,
        },
        {
            "account": cuenta_credito,
            "amount": amount,
            "direction": "CREDIT",
            "descripcion": descripcion,
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