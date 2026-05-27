from django.db import models


class TipoAlerta(models.TextChoices):
    APUESTA_ALTA              = 'apuesta_alta',              'Apuesta de monto alto'
    MUCHAS_APUESTAS_RAPIDAS   = 'muchas_apuestas_rapidas',   'Muchas apuestas rápidas'
    APUESTAS_REPETIDAS_EVENTO = 'apuestas_repetidas_evento', 'Apuestas repetidas en mismo evento'


class SeveridadAlerta(models.TextChoices):
    BAJA  = 'baja',  'Baja'
    MEDIA = 'media', 'Media'
    ALTA  = 'alta',  'Alta'


class EstadoAlerta(models.TextChoices):
    ABIERTA    = 'abierta',    'Abierta'
    REVISADA   = 'revisada',   'Revisada'
    DESCARTADA = 'descartada', 'Descartada'


class FraudAlert(models.Model):
    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='alertas_fraude',
    )
    bet = models.ForeignKey(
        'apuestas_core.Bet',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertas_fraude',
    )
    tipo_alerta = models.CharField(
        max_length=40,
        choices=TipoAlerta.choices,
    )
    severidad = models.CharField(
        max_length=10,
        choices=SeveridadAlerta.choices,
        default=SeveridadAlerta.BAJA,
    )
    descripcion = models.TextField()
    estado = models.CharField(
        max_length=15,
        choices=EstadoAlerta.choices,
        default=EstadoAlerta.ABIERTA,
    )
    metadata = models.JSONField(default=dict, blank=True)

    fecha_creacion     = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table          = 'antifraude_fraud_alert'
        verbose_name      = 'Alerta de fraude'
        verbose_name_plural = 'Alertas de fraude'
        ordering          = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['tipo_alerta']),
            models.Index(fields=['severidad']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_creacion']),
        ]

    def __str__(self):
        return f'[{self.severidad.upper()}] {self.tipo_alerta} — {self.usuario}'
