from decimal import Decimal

import pytest

from apuestas_core.services.apuesta_service import (
    ApuestaError,
    MONTO_MAXIMO_APUESTA,
    MONTO_MINIMO_APUESTA,
    validar_monto_apuesta,
)


def test_validar_monto_apuesta_normaliza_a_cuatro_decimales():
    assert validar_monto_apuesta("10.12555") == Decimal("10.1256")


def test_validar_monto_apuesta_rechaza_monto_menor_al_minimo():
    monto_bajo = MONTO_MINIMO_APUESTA - Decimal("0.0001")

    with pytest.raises(ApuestaError, match="monto"):
        validar_monto_apuesta(monto_bajo)


def test_validar_monto_apuesta_rechaza_monto_mayor_al_maximo():
    monto_alto = MONTO_MAXIMO_APUESTA + Decimal("0.0001")

    with pytest.raises(ApuestaError, match="monto"):
        validar_monto_apuesta(monto_alto)
