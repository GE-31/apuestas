"""
Limpia todos los datos de apuestas y restablece los saldos a S/ 1,000
para tener una demo limpia.

Uso: python manage.py limpiar_demo
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apuestas_core.models import Bet, BetSelection
from billetera.models import Account, LedgerEntry, LedgerTransaction
from config.choices import TipoCuentaLedger


SALDO_INICIAL = Decimal("1000.0000")


class Command(BaseCommand):
    help = 'Resetea apuestas y saldos de usuarios para demo limpia'

    @transaction.atomic
    def handle(self, *args, **options):
        # 1. Borrar todas las apuestas y selecciones
        bets_count = Bet.objects.count()
        BetSelection.objects.all().delete()
        Bet.objects.all().delete()
        self.stdout.write(f'  Apuestas eliminadas: {bets_count}')

        # 2. Borrar todas las entradas del libro contable
        entries = LedgerEntry.objects.count()
        LedgerEntry.objects.all().delete()
        self.stdout.write(f'  Entradas contables eliminadas: {entries}')

        # 3. Borrar transacciones del libro
        txn_count = LedgerTransaction.objects.count()
        LedgerTransaction.objects.all().delete()
        self.stdout.write(f'  Transacciones eliminadas: {txn_count}')

        # 4. Restaurar saldo S/ 1,000 a cada wallet de usuario
        wallets = Account.objects.filter(
            tipo=TipoCuentaLedger.WALLET_USUARIO,
            activa=True,
        ).select_related('usuario')

        # Cuentas del sistema para balancear el libro
        cuenta_casa = Account.objects.filter(
            tipo=TipoCuentaLedger.CASA,
            activa=True,
        ).first()

        restaurados = 0
        for wallet in wallets:
            if not cuenta_casa:
                break
            # Crear entradas balanceadas: DEBIT casa → CREDIT wallet
            LedgerEntry.objects.create(
                account=cuenta_casa,
                amount=SALDO_INICIAL,
                direction='DEBIT',
                descripcion=f'Reset demo — carga inicial wallet {wallet.usuario}',
            )
            LedgerEntry.objects.create(
                account=wallet,
                amount=SALDO_INICIAL,
                direction='CREDIT',
                descripcion=f'Reset demo — saldo inicial S/ {SALDO_INICIAL}',
            )
            restaurados += 1
            self.stdout.write(f'  Saldo restaurado: {wallet.usuario} → S/ {SALDO_INICIAL}')

        self.stdout.write(self.style.SUCCESS(
            f'\nDemo limpia. {restaurados} usuario(s) con S/ {SALDO_INICIAL} cada uno.'
        ))
