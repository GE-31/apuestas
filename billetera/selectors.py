from decimal import Decimal

from django.db.models import Case, DecimalField, F, Sum, Value, When
from django.db.models.functions import Coalesce

from config.choices import DireccionLedger
from billetera.models import Account, LedgerEntry


def obtener_saldo_cuenta(account: Account) -> Decimal:
    """
    Calcula el saldo de una cuenta desde sus movimientos ledger.

    saldo = créditos - débitos
    """

    resultado = LedgerEntry.objects.filter(account=account).aggregate(
        saldo=Coalesce(
            Sum(
                Case(
                    When(
                        direction=DireccionLedger.CREDIT,
                        then=F('amount'),
                    ),
                    When(
                        direction=DireccionLedger.DEBIT,
                        then=-F('amount'),
                    ),
                    default=Value(Decimal('0.0000')),
                    output_field=DecimalField(max_digits=18, decimal_places=4),
                )
            ),
            Value(Decimal('0.0000')),
            output_field=DecimalField(max_digits=18, decimal_places=4),
        )
    )

    return resultado['saldo']


def obtener_cuentas_usuario(usuario):
    return Account.objects.filter(usuario=usuario, activa=True)


def obtener_movimientos_cuenta(account: Account):
    return (
        LedgerEntry.objects
        .select_related('transaction', 'account')
        .filter(account=account)
        .order_by('-fecha_creacion')
    )