from django.db import models
from django.conf import settings
from config.choices import EstadoApuesta, TipoApuesta
from cuotas.models import Odd
from mercados.models import SeleccionMercado

# Create your models here.



class Bet(models.Model):
    """
    Apuesta principal.

    Importante:
    - Aquí no va la lógica de crear apuesta.
    - Aquí no va la lógica de bloquear saldo.
    - Aquí no va la lógica de liquidar.
    - Todo eso va en services/.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='apuestas'
    )

    tipo = models.CharField(
        max_length=20,
        choices=TipoApuesta.choices,
        default=TipoApuesta.SIMPLE
    )

    estado = models.CharField(
        max_length=20,
        choices=EstadoApuesta.choices,
        default=EstadoApuesta.BORRADOR
    )

    stake = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        help_text='Monto apostado en fichas virtuales.'
    )

    odds_total = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        help_text='Cuota total de la apuesta.'
    )

    payout_potencial = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        help_text='Pago potencial si la apuesta gana.'
    )

    payout_final = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        blank=True,
        null=True,
        help_text='Pago final después de liquidar.'
    )

    idempotency_key = models.CharField(
        max_length=120,
        unique=True,
        blank=True,
        null=True,
        help_text='Clave para evitar apuestas duplicadas.'
    )

    ip_origen = models.GenericIPAddressField(
        blank=True,
        null=True
    )

    aceptada_en = models.DateTimeField(
        blank=True,
        null=True
    )

    liquidada_en = models.DateTimeField(
        blank=True,
        null=True
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'apuestas_bet'
        verbose_name = 'Apuesta'
        verbose_name_plural = 'Apuestas'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['estado']),
            models.Index(fields=['tipo']),
            models.Index(fields=['idempotency_key']),
            models.Index(fields=['fecha_creacion']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(stake__gt=0),
                name='bet_stake_mayor_que_cero'
            ),
            models.CheckConstraint(
                condition=models.Q(odds_total__gt=1),
                name='bet_odds_total_mayor_que_uno'
            ),
            models.CheckConstraint(
                condition=models.Q(payout_potencial__gte=0),
                name='bet_payout_potencial_no_negativo'
            ),
        ]

    def __str__(self):
        return f'Bet #{self.id} - {self.usuario} - {self.estado}'


class BetSelection(models.Model):
    """
    Selección incluida dentro de una apuesta.

    Para apuesta simple:
    - La apuesta tendrá una sola selección.

    Para combinada:
    - La apuesta tendrá múltiples selecciones.
    """

    bet = models.ForeignKey(
        Bet,
        on_delete=models.CASCADE,
        related_name='selecciones'
    )

    seleccion = models.ForeignKey(
        SeleccionMercado,
        on_delete=models.PROTECT,
        related_name='apuestas_selecciones'
    )

    odd = models.ForeignKey(
        Odd,
        on_delete=models.PROTECT,
        related_name='apuestas_selecciones'
    )

    odd_valor_tomado = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        help_text='Cuota capturada al momento de aceptar la apuesta.'
    )

    resultado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('ganada', 'Ganada'),
            ('perdida', 'Perdida'),
            ('anulada', 'Anulada'),
        ],
        default='pendiente'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'apuestas_bet_selection'
        verbose_name = 'Selección de apuesta'
        verbose_name_plural = 'Selecciones de apuesta'
        ordering = ['bet', 'id']
        indexes = [
            models.Index(fields=['bet']),
            models.Index(fields=['seleccion']),
            models.Index(fields=['odd']),
            models.Index(fields=['resultado']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(odd_valor_tomado__gt=1),
                name='bet_selection_odd_valor_mayor_que_uno'
            )
        ]

    def __str__(self):
        return f'{self.bet} - {self.seleccion}'
