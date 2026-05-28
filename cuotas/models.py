from django.db import models
from django.conf import settings

# Create your models here.


from mercados.models import SeleccionMercado


class Odd(models.Model):
    """
    Cuota actual de una selección de mercado.

    Ejemplo:
    - Selección: Gana local
    - Cuota: 2.5000

    Nota:
    - Aquí no va la lógica de recotización.
    - La lógica irá en cuotas/services/odds_service.py.
    """

    seleccion = models.OneToOneField(
        SeleccionMercado,
        on_delete=models.CASCADE,
        related_name='odd'
    )

    valor = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        help_text='Cuota decimal europea. Ejemplo: 2.5000'
    )

    margen_operador = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=0,
        help_text='Margen aplicado por el operador.'
    )

    activa = models.BooleanField(default=True)
    suspendida = models.BooleanField(default=False)

    actualizada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='cuotas_actualizadas'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cuotas_odd'
        verbose_name = 'Cuota'
        verbose_name_plural = 'Cuotas'
        ordering = ['seleccion']
        indexes = [
            models.Index(fields=['activa']),
            models.Index(fields=['suspendida']),
            models.Index(fields=['fecha_actualizacion']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(valor__gt=1),
                name='odd_valor_mayor_que_uno'
            ),
            models.CheckConstraint(
                condition=models.Q(margen_operador__gte=0),
                name='odd_margen_operador_no_negativo'
            ),
        ]

    def __str__(self):
        return f'{self.seleccion} @ {self.valor}'


class OddHistory(models.Model):
    """
    Historial de cambios de cuotas.

    Cada cambio de cuota debe quedar registrado.
    Esto ayuda a auditoría y recotización.
    """

    odd = models.ForeignKey(
        Odd,
        on_delete=models.CASCADE,
        related_name='historial'
    )

    valor_anterior = models.DecimalField(
        max_digits=18,
        decimal_places=4
    )

    valor_nuevo = models.DecimalField(
        max_digits=18,
        decimal_places=4
    )

    margen_operador = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=0
    )

    motivo = models.CharField(
        max_length=180,
        blank=True,
        null=True
    )

    cambiado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='historial_cuotas_cambiadas'
    )

    fecha_cambio = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cuotas_odd_history'
        verbose_name = 'Historial de cuota'
        verbose_name_plural = 'Historial de cuotas'
        ordering = ['-fecha_cambio']
        indexes = [
            models.Index(fields=['odd']),
            models.Index(fields=['fecha_cambio']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(valor_anterior__gt=1),
                name='odd_history_valor_anterior_mayor_que_uno'
            ),
            models.CheckConstraint(
                condition=models.Q(valor_nuevo__gt=1),
                name='odd_history_valor_nuevo_mayor_que_uno'
            ),
        ]

    def __str__(self):
        return f'{self.odd} | {self.valor_anterior} -> {self.valor_nuevo}'
