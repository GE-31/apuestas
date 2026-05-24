from decimal import Decimal

from billetera.models import Account
from billetera.services.ledger_service import crear_movimiento_simple
from billetera.services.saldo_service import validar_saldo_suficiente
from config.choices import TipoCuentaLedger, TipoTransaccionLedger


class CuentaSistemaNoEncontradaError(Exception):
    pass


def obtener_cuenta_casa():
    cuenta = Account.objects.filter(
        usuario__isnull=True,
        tipo=TipoCuentaLedger.CASA,
        activa=True,
    ).first()

    if not cuenta:
        raise CuentaSistemaNoEncontradaError(
            'No existe una cuenta activa de tipo CASA.'
        )

    return cuenta


def obtener_wallet_usuario(usuario):
    cuenta = Account.objects.filter(
        usuario=usuario,
        tipo=TipoCuentaLedger.WALLET_USUARIO,
        activa=True,
    ).first()

    if not cuenta:
        raise CuentaSistemaNoEncontradaError(
            'El usuario no tiene una wallet activa.'
        )

    return cuenta


def retirar_fichas_usuario(
    *,
    usuario,
    amount: Decimal,
    idempotency_key=None,
    creado_por=None,
):
    """
    Retiro simulado de fichas virtuales.

    Importante:
    - No convierte fichas a dinero.
    - Solo mueve fichas virtuales de wallet hacia casa.
    """

    wallet_usuario = obtener_wallet_usuario(usuario)
    cuenta_casa = obtener_cuenta_casa()

    validar_saldo_suficiente(wallet_usuario, amount)

    return crear_movimiento_simple(
        cuenta_debito=wallet_usuario,
        cuenta_credito=cuenta_casa,
        amount=amount,
        tipo=TipoTransaccionLedger.RETIRO,
        referencia=f'retiro_usuario_{usuario.id}',
        idempotency_key=idempotency_key,
        descripcion='Retiro simulado de fichas virtuales',
        creado_por=creado_por,
    )