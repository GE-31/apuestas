from decimal import Decimal

import pytest

from billetera.services.ledger_service import (
    LedgerError,
    normalizar_decimal,
    validar_entries_balanceadas,
)
from billetera.serializers import RecargaFichasSerializer, RetiroFichasSerializer


def test_normalizar_decimal_usa_cuatro_decimales():
    assert normalizar_decimal("12.34567") == Decimal("12.3457")


def test_validar_entries_balanceadas_acepta_debito_y_credito_iguales():
    entries = [
        {"account": object(), "amount": Decimal("25.0000"), "direction": "DEBIT"},
        {"account": object(), "amount": Decimal("25.0000"), "direction": "CREDIT"},
    ]

    assert validar_entries_balanceadas(entries) is True


def test_validar_entries_balanceadas_rechaza_movimiento_descuadrado():
    entries = [
        {"account": object(), "amount": Decimal("25.0000"), "direction": "DEBIT"},
        {"account": object(), "amount": Decimal("24.9900"), "direction": "CREDIT"},
    ]

    with pytest.raises(LedgerError, match="no balanceada"):
        validar_entries_balanceadas(entries)


def test_validar_entries_balanceadas_rechaza_montos_no_positivos():
    entries = [
        {"account": object(), "amount": Decimal("0.0000"), "direction": "DEBIT"},
        {"account": object(), "amount": Decimal("0.0000"), "direction": "CREDIT"},
    ]

    with pytest.raises(LedgerError, match="mayor que cero"):
        validar_entries_balanceadas(entries)


@pytest.mark.parametrize("serializer_class", [RecargaFichasSerializer, RetiroFichasSerializer])
def test_operaciones_wallet_rechazan_montos_no_positivos(serializer_class):
    serializer = serializer_class(data={"usuario_id": 1, "amount": "0.0000"})

    assert serializer.is_valid() is False
    assert "amount" in serializer.errors
