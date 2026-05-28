from decimal import Decimal

from billetera.models import Account
from billetera.services.ledger_service import crear_movimiento_simple
from config.choices import TipoCuentaLedger, TipoTransaccionLedger
from juego_responsable.services.limites_service import validar_limite_deposito


class CuentaSistemaNoEncontradaError(Exception):
    pass


def obtener_cuenta_casa():
    cuenta, _ = Account.objects.get_or_create(
        usuario=None,
        tipo=TipoCuentaLedger.CASA,
        defaults={
            'nombre': 'Casa',
            'activa': True,
        },
    )

    if not cuenta.activa:
        raise CuentaSistemaNoEncontradaError('No existe una cuenta activa de tipo CASA.')
    return cuenta


def obtener_wallet_usuario(usuario):
    cuenta, _ = Account.objects.get_or_create(
        usuario=usuario,
        tipo=TipoCuentaLedger.WALLET_USUARIO,
        defaults={
            'nombre': f'Wallet de {usuario.username}',
            'activa': True,
        },
    )
    if not cuenta.activa:
        raise CuentaSistemaNoEncontradaError('El usuario no tiene una wallet activa.')
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

    Reglas:
    - No hay pasarela real.
    - No hay dinero real.
    - Se validan límites de juego responsable.
    - La casa debita y la wallet del usuario acredita.
    """

    validar_limite_deposito(usuario, amount)

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
