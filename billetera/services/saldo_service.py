from decimal import Decimal

from billetera.models import Account
from billetera.selectors import obtener_saldo_cuenta


class SaldoInsuficienteError(Exception):
    pass


def obtener_saldo_disponible(account: Account) -> Decimal:
    """
    Retorna el saldo disponible de una cuenta.

    Regla del proyecto:
    - El saldo NO se guarda en Account.
    - El saldo se calcula desde LedgerEntry.
    """

    return obtener_saldo_cuenta(account)


def validar_saldo_suficiente(account: Account, amount: Decimal) -> bool:
    """
    Valida si una cuenta tiene saldo suficiente.

    Esta validación se usa antes de:
    - apostar
    - retirar
    - transferir
    - bloquear fondos
    """

    saldo_actual = obtener_saldo_disponible(account)

    if saldo_actual < amount:
        raise SaldoInsuficienteError(
            f'Saldo insuficiente. Saldo actual: {saldo_actual}, monto requerido: {amount}'
        )

    return True


def obtener_resumen_saldo(account: Account) -> dict:
    """
    Retorna un resumen simple del saldo de una cuenta.
    Útil para API y panel.
    """

    saldo = obtener_saldo_disponible(account)

    return {
        'account_id': account.id,
        'tipo': account.tipo,
        'nombre': account.nombre,
        'saldo': saldo,
        'activa': account.activa,
    }