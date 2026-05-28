from decimal import Decimal
import re

from billetera.models import Account
from billetera.services.ledger_service import crear_movimiento_simple
from billetera.services.saldo_service import validar_saldo_suficiente
from config.choices import TipoCuentaLedger, TipoTransaccionLedger


class CuentaSistemaNoEncontradaError(Exception):
    pass


class NumeroYapeInvalidoError(Exception):
    pass


def validar_numero_yape(yape_number):
    yape_number = str(yape_number or '').strip().replace(' ', '')
    if not re.fullmatch(r'9\d{8}', yape_number):
        raise NumeroYapeInvalidoError(
            'Ingresa un numero Yape valido de 9 digitos que empiece con 9.'
        )
    return yape_number


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


def retirar_fichas_usuario(
    *,
    usuario,
    amount: Decimal,
    yape_number,
    idempotency_key=None,
    creado_por=None,
):
    """
    Retiro simulado de saldo virtual en soles.

    Importante:
    - No convierte fichas a dinero.
    - Solo mueve saldo virtual de wallet hacia casa.
    """

    yape_number = validar_numero_yape(yape_number)
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
        descripcion=f'Retiro simulado de saldo virtual en soles hacia Yape +51 {yape_number}',
        creado_por=creado_por,
    )
