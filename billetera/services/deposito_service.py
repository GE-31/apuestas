from decimal import Decimal

from billetera.models import Account
from billetera.services.ledger_service import crear_movimiento_simple
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


def recargar_fichas_usuario(
    *,
    usuario,
    amount: Decimal,
    idempotency_key=None,
    creado_por=None,
):
    """
    Recarga simulada de fichas virtuales.

    Importante:
    - No hay pasarela real.
    - No hay dinero real.
    - La casa debita y la wallet del usuario acredita.
    """

    cuenta_casa = obtener_cuenta_casa()
    wallet_usuario = obtener_wallet_usuario(usuario)

    return crear_movimiento_simple(
        cuenta_debito=cuenta_casa,
        cuenta_credito=wallet_usuario,
        amount=amount,
        tipo=TipoTransaccionLedger.RECARGA,
        referencia=f'recarga_usuario_{usuario.id}',
        idempotency_key=idempotency_key,
        descripcion='Recarga simulada de fichas virtuales',
        creado_por=creado_por,
    )