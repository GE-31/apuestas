from django.db import models
from django.conf import settings
from django.utils import timezone

from config.choices import DuracionAutoexclusion, EstadoAutoexclusion
# Create your models here.

class LimiteDeposito(models.Model):
    """
    Límites de depósito de fichas virtuales por usuario.

    Importante:
    - Aquí solo se guardan los límites configurados.
    - La lógica de validación va en services/limites_service.py.
    - Si el usuario baja el límite, se aplica inmediatamente.
    - Si el usuario sube el límite, debe esperar cooldown de 24h.
    """

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='limite_deposito'
    )

    limite_diario = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=0,
        help_text='Límite diario de recarga simulada de fichas.'
    )

    limite_semanal = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=0,
        help_text='Límite semanal de recarga simulada de fichas.'
    )

    limite_mensual = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=0,
        help_text='Límite mensual de recarga simulada de fichas.'
    )

    cambio_pendiente_diario = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        blank=True,
        null=True
    )

    cambio_pendiente_semanal = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        blank=True,
        null=True
    )

    cambio_pendiente_mensual = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        blank=True,
        null=True
    )

    aplicar_cambio_en = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Fecha en la que se aplica el aumento de límite.'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'juego_responsable_limite_deposito'
        verbose_name = 'Límite de depósito'
        verbose_name_plural = 'Límites de depósito'
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['aplicar_cambio_en']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(limite_diario__gte=0),
                name='limite_diario_no_negativo'
            ),
            models.CheckConstraint(
                condition=models.Q(limite_semanal__gte=0),
                name='limite_semanal_no_negativo'
            ),
            models.CheckConstraint(
                condition=models.Q(limite_mensual__gte=0),
                name='limite_mensual_no_negativo'
            ),
        ]

    def __str__(self):
        return f'Límites de {self.usuario}'


class Autoexclusion(models.Model):
    """
    Autoexclusión del usuario.

    Importante:
    - Si está activa, el usuario no debe poder apostar.
    - La lógica de activación, vigencia y bloqueo va en autoexclusion_service.py.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='autoexclusiones'
    )

    estado = models.CharField(
        max_length=20,
        choices=EstadoAutoexclusion.choices,
        default=EstadoAutoexclusion.ACTIVA
    )

    duracion = models.CharField(
        max_length=20,
        choices=DuracionAutoexclusion.choices
    )

    fecha_inicio = models.DateTimeField(default=timezone.now)

    fecha_fin = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Vacío cuando la autoexclusión es indefinida.'
    )

    motivo = models.TextField(
        blank=True,
        null=True
    )

    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='autoexclusiones_creadas'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'juego_responsable_autoexclusion'
        verbose_name = 'Autoexclusión'
        verbose_name_plural = 'Autoexclusiones'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['estado']),
            models.Index(fields=['duracion']),
            models.Index(fields=['fecha_inicio']),
            models.Index(fields=['fecha_fin']),
        ]

    def __str__(self):
        return f'Autoexclusión {self.usuario} - {self.estado}'


class MensajeJuegoResponsable(models.Model):
    """
    Mensajes visibles de juego responsable.

    Sirve para mostrar textos obligatorios en pantallas de apuesta.
    """

    titulo = models.CharField(max_length=120)

    mensaje = models.TextField()

    activo = models.BooleanField(default=True)

    ubicacion = models.CharField(
        max_length=80,
        default='pantallas_apuesta',
        help_text='Ejemplo: pantallas_apuesta, dashboard, footer.'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'juego_responsable_mensaje'
        verbose_name = 'Mensaje de juego responsable'
        verbose_name_plural = 'Mensajes de juego responsable'
        ordering = ['ubicacion', 'titulo']
        indexes = [
            models.Index(fields=['activo']),
            models.Index(fields=['ubicacion']),
        ]

    def __str__(self):
        return self.titulo
