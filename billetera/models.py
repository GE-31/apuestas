
# Create your models here.
from django.conf import settings
from django.db import models

from config.choices import (
    DireccionLedger,
    TipoCuentaLedger,
    TipoTransaccionLedger,
)


class Account(models.Model):
    """
    Cuenta contable del sistema.

    Importante:
    - No almacena saldo.
    - El saldo se calcula desde LedgerEntry en selectors.py.
    - La lógica de movimientos va en services/.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cuentas_ledger',
        blank=True,
        null=True,
    )

    tipo = models.CharField(
        max_length=40,
        choices=TipoCuentaLedger.choices,
    )

    nombre = models.CharField(max_length=120)

    activa = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'billetera_account'
        verbose_name = 'Cuenta contable'
        verbose_name_plural = 'Cuentas contables'
        ordering = ['tipo', 'nombre']
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['usuario']),
            models.Index(fields=['activa']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'tipo'],
                name='unique_account_tipo_por_usuario'
            )
        ]

    def __str__(self):
        if self.usuario:
            return f'{self.nombre} - {self.usuario}'
        return self.nombre


class LedgerTransaction(models.Model):
    """
    Transacción contable agrupadora.

    Una transacción debe tener mínimo dos LedgerEntry:
    - Un débito.
    - Un crédito.

    La validación de que esté balanceada NO va aquí.
    Irá en billetera/services/ledger_service.py.
    """

    tipo = models.CharField(
        max_length=40,
        choices=TipoTransaccionLedger.choices,
    )

    referencia = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text='Referencia externa o interna de la operación.'
    )

    idempotency_key = models.CharField(
        max_length=120,
        unique=True,
        blank=True,
        null=True,
        help_text='Clave para evitar operaciones duplicadas.'
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
    )

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='transacciones_ledger_creadas',
        blank=True,
        null=True,
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'billetera_ledger_transaction'
        verbose_name = 'Transacción ledger'
        verbose_name_plural = 'Transacciones ledger'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['referencia']),
            models.Index(fields=['idempotency_key']),
            models.Index(fields=['fecha_creacion']),
        ]

    def __str__(self):
        return f'{self.tipo} - {self.id}'


class LedgerEntry(models.Model):
    """
    Entrada contable individual.

    Cada operación financiera debe crear entradas balanceadas.
    Ejemplo:
    - DEBIT en una cuenta.
    - CREDIT en otra cuenta.

    El saldo se obtiene sumando:
    CREDIT - DEBIT.
    """

    transaction = models.ForeignKey(
        LedgerTransaction,
        on_delete=models.CASCADE,
        related_name='entries',
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='entries',
    )

    amount = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        help_text='Monto en fichas virtuales. No usar float.'
    )

    direction = models.CharField(
        max_length=10,
        choices=DireccionLedger.choices,
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'billetera_ledger_entry'
        verbose_name = 'Entrada ledger'
        verbose_name_plural = 'Entradas ledger'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['transaction']),
            models.Index(fields=['account']),
            models.Index(fields=['direction']),
            models.Index(fields=['fecha_creacion']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name='ledger_entry_amount_gt_zero'
            )
        ]

    def __str__(self):
        return f'{self.direction} {self.amount} - {self.account}'