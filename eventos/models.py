from django.db import models

from config.choices import EstadoEvento


class Deporte(models.Model):
    """
    Catálogo de deportes.
    Ejemplo: Fútbol, Básquet, Tenis.
    """

    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'eventos_deporte'
        verbose_name = 'Deporte'
        verbose_name_plural = 'Deportes'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return self.nombre


class Liga(models.Model):
    """
    Liga o competición deportiva.
    Ejemplo: Liga 1 Perú, Premier League, Champions League.
    """

    nombre = models.CharField(max_length=120, unique=True)
    deporte = models.ForeignKey(
        Deporte,
        on_delete=models.PROTECT,
        related_name='ligas',
    )
    pais = models.CharField(max_length=80, blank=True, default='')
    activa = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'eventos_liga'
        verbose_name = 'Liga'
        verbose_name_plural = 'Ligas'
        ordering = ['deporte__nombre', 'nombre']
        indexes = [
            models.Index(fields=['deporte']),
            models.Index(fields=['activa']),
        ]

    def __str__(self):
        return f'{self.nombre}'


class Equipo(models.Model):
    """
    Equipo o participante deportivo.
    Ejemplo: Perú, Argentina, Brasil.
    """

    nombre = models.CharField(max_length=120)
    abreviatura = models.CharField(max_length=10, blank=True, null=True)

    deporte = models.ForeignKey(
        Deporte,
        on_delete=models.PROTECT,
        related_name='equipos'
    )

    pais = models.CharField(max_length=80, blank=True, null=True)
    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'eventos_equipo'
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['deporte']),
            models.Index(fields=['activo']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['nombre', 'deporte'],
                name='unique_equipo_por_deporte'
            )
        ]

    def __str__(self):
        return self.nombre


class Evento(models.Model):
    """
    Evento deportivo apostable.
    Ejemplo: Perú vs Argentina.

    Nota:
    - Aquí no se liquida la apuesta.
    - Solo se guarda el estado y datos del evento.
    """

    deporte = models.ForeignKey(
        Deporte,
        on_delete=models.PROTECT,
        related_name='eventos'
    )

    liga = models.ForeignKey(
        Liga,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos',
    )

    equipo_local = models.ForeignKey(
        Equipo,
        on_delete=models.PROTECT,
        related_name='eventos_como_local'
    )

    equipo_visitante = models.ForeignKey(
        Equipo,
        on_delete=models.PROTECT,
        related_name='eventos_como_visitante'
    )

    nombre = models.CharField(
        max_length=180,
        help_text='Nombre visible del evento. Ejemplo: Perú vs Argentina.'
    )

    estado = models.CharField(
        max_length=20,
        choices=EstadoEvento.choices,
        default=EstadoEvento.PROGRAMADO
    )

    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(blank=True, null=True)

    marcador_local = models.PositiveIntegerField(blank=True, null=True)
    marcador_visitante = models.PositiveIntegerField(blank=True, null=True)

    periodo_en_vivo = models.PositiveSmallIntegerField(default=1)
    periodo_inicio = models.DateTimeField(blank=True, null=True)

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'eventos_evento'
        verbose_name = 'Evento deportivo'
        verbose_name_plural = 'Eventos deportivos'
        ordering = ['fecha_inicio']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_inicio']),
            models.Index(fields=['deporte']),
            models.Index(fields=['activo']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(equipo_local=models.F('equipo_visitante')),
                name='evento_equipos_diferentes'
            )
        ]

    def __str__(self):
        return self.nombre


class ResultadoEvento(models.Model):
    """
    Resultado oficial del evento.

    Nota:
    - Solo almacena el resultado.
    - La lógica de liquidación irá en apuestas_core/services/liquidacion_service.py.
    """

    evento = models.OneToOneField(
        Evento,
        on_delete=models.CASCADE,
        related_name='resultado'
    )

    marcador_local = models.PositiveIntegerField()
    marcador_visitante = models.PositiveIntegerField()

    resultado_1x2 = models.CharField(
        max_length=20,
        choices=[
            ('local', 'Gana local'),
            ('empate', 'Empate'),
            ('visitante', 'Gana visitante'),
        ]
    )

    registrado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='resultados_registrados'
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'eventos_resultado'
        verbose_name = 'Resultado de evento'
        verbose_name_plural = 'Resultados de eventos'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['resultado_1x2']),
            models.Index(fields=['fecha_registro']),
        ]

    def __str__(self):
        return f'Resultado - {self.evento}'
