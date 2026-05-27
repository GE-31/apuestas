from django.db import models
from config.choices import TipoMercado, TipoSeleccionMercado
from eventos.models import Evento

# Create your models here.

class Mercado(models.Model):
    """
    Mercado apostable asociado a un evento deportivo.

    Ejemplo:
    - Evento: Perú vs Argentina
    - Mercado: 1X2
    """

    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='mercados'
    )

    tipo = models.CharField(
        max_length=30,
        choices=TipoMercado.choices,
        default=TipoMercado.UNO_X_DOS
    )

    nombre = models.CharField(
        max_length=120,
        help_text='Ejemplo: Resultado final 1X2'
    )

    descripcion = models.TextField(
        blank=True,
        null=True
    )

    activo = models.BooleanField(default=True)
    suspendido = models.BooleanField(default=False)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mercados_mercado'
        verbose_name = 'Mercado'
        verbose_name_plural = 'Mercados'
        ordering = ['evento', 'tipo']
        indexes = [
            models.Index(fields=['evento']),
            models.Index(fields=['tipo']),
            models.Index(fields=['activo']),
            models.Index(fields=['suspendido']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['evento', 'tipo'],
                name='unique_mercado_tipo_por_evento'
            )
        ]

    def __str__(self):
        return f'{self.evento} - {self.nombre}'


class SeleccionMercado(models.Model):
    """
    Selección apostable dentro de un mercado.

    Para mercado 1X2:
    - local
    - empate
    - visitante
    """

    mercado = models.ForeignKey(
        Mercado,
        on_delete=models.CASCADE,
        related_name='selecciones'
    )

    tipo = models.CharField(
        max_length=30,
        choices=TipoSeleccionMercado.choices
    )

    nombre = models.CharField(
        max_length=120,
        help_text='Ejemplo: Gana local, Empate, Gana visitante'
    )

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mercados_seleccion'
        verbose_name = 'Selección de mercado'
        verbose_name_plural = 'Selecciones de mercado'
        ordering = ['mercado', 'tipo']
        indexes = [
            models.Index(fields=['mercado']),
            models.Index(fields=['tipo']),
            models.Index(fields=['activo']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['mercado', 'tipo'],
                name='unique_seleccion_tipo_por_mercado'
            )
        ]

    def __str__(self):
        return f'{self.mercado} - {self.nombre}'