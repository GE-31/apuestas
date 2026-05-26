from django.db import models
from django.conf import settings
# Create your models here.


class AuditLog(models.Model):
    """
    Registro de auditoría inmutable.

    Importante:
    - Esta tabla debe tratarse como append-only.
    - No se deben editar registros existentes.
    - Cada registro guarda previous_hash y current_hash.
    - La lógica de cálculo de hash irá en services/hash_chain_service.py.
    """

    class TipoEvento(models.TextChoices):
        WALLET_MOVEMENT = 'wallet_movement', 'Movimiento de wallet'
        BET_CREATED = 'bet_created', 'Apuesta creada'
        BET_SETTLED = 'bet_settled', 'Apuesta liquidada'
        ODD_CHANGED = 'odd_changed', 'Cambio de cuota'
        USER_KYC = 'user_kyc', 'Cambio KYC'
        RESPONSIBLE_GAMING = 'responsible_gaming', 'Juego responsable'
        FRAUD_ALERT = 'fraud_alert', 'Alerta antifraude'
        SYSTEM = 'system', 'Sistema'

    tipo_evento = models.CharField(
        max_length=40,
        choices=TipoEvento.choices
    )

    entidad = models.CharField(
        max_length=80,
        help_text='Nombre de la entidad auditada. Ejemplo: Bet, LedgerTransaction, Odd.'
    )

    entidad_id = models.CharField(
        max_length=80,
        help_text='ID de la entidad auditada.'
    )

    accion = models.CharField(
        max_length=80,
        help_text='Acción realizada. Ejemplo: created, updated, settled, blocked.'
    )

    payload = models.JSONField(
        help_text='Datos relevantes del evento auditado.'
    )

    previous_hash = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text='Hash del registro anterior.'
    )

    current_hash = models.CharField(
        max_length=64,
        unique=True,
        help_text='Hash calculado del registro actual.'
    )

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='auditorias_creadas'
    )

    ip_origen = models.GenericIPAddressField(
        blank=True,
        null=True
    )

    user_agent = models.TextField(
        blank=True,
        null=True
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auditoria_audit_log'
        verbose_name = 'Registro de auditoría'
        verbose_name_plural = 'Registros de auditoría'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['tipo_evento']),
            models.Index(fields=['entidad']),
            models.Index(fields=['entidad_id']),
            models.Index(fields=['accion']),
            models.Index(fields=['fecha_creacion']),
            models.Index(fields=['current_hash']),
        ]

    def __str__(self):
        return f'{self.tipo_evento} - {self.entidad} #{self.entidad_id}'


class AuditIntegrityCheck(models.Model):
    """
    Resultado de verificación de integridad de la cadena de auditoría.

    Sirve para que el admin vea si la cadena sigue válida.
    """

    ejecutado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='verificaciones_auditoria'
    )

    es_valida = models.BooleanField(default=True)

    total_registros = models.PositiveIntegerField(default=0)

    errores_detectados = models.JSONField(
        blank=True,
        null=True,
        help_text='Lista de errores encontrados durante la verificación.'
    )

    fecha_ejecucion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auditoria_integrity_check'
        verbose_name = 'Verificación de integridad'
        verbose_name_plural = 'Verificaciones de integridad'
        ordering = ['-fecha_ejecucion']
        indexes = [
            models.Index(fields=['es_valida']),
            models.Index(fields=['fecha_ejecucion']),
        ]

    def __str__(self):
        estado = 'válida' if self.es_valida else 'con errores'
        return f'Verificación {estado} - {self.fecha_ejecucion}'