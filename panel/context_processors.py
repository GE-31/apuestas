from decimal import Decimal

from billetera.models import Account
from billetera.selectors import obtener_saldo_cuenta
from config.choices import TipoCuentaLedger


def cuenta_drawer(request):
    if not request.user.is_authenticated:
        return {}

    saldo = Decimal("0.0000")
    wallet = Account.objects.filter(
        usuario=request.user,
        tipo=TipoCuentaLedger.WALLET_USUARIO,
        activa=True,
    ).first()

    if wallet:
        saldo = obtener_saldo_cuenta(wallet)

    return {
        "cuenta_drawer_saldo": saldo,
        "cuenta_drawer_bono": Decimal("0.0000"),
    }
