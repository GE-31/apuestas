
# Create your models here.
from django.conf import settings
from django.db import models

from config.choices import EstadoCuenta


class PerfilUsuario(models.Model):
    """
    Perfil extendido del usuario del sistema.

    Nota:
    - Aquí NO va la lógica de negocio fuerte.
    - La validación de DNI, mayoría de edad y KYC irá en validators.py/services.py.
    """

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_apuestas'
    )

    dni = models.CharField(
        max_length=8,
        unique=True,
        help_text='DNI peruano de 8 dígitos.'
    )

    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)

    fecha_nacimiento = models.DateField()

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    direccion = models.TextField(
        blank=True,
        null=True
    )

    estado_cuenta = models.CharField(
        max_length=30,
        choices=EstadoCuenta.choices,
        default=EstadoCuenta.PENDIENTE_VERIFICACION
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usuarios_perfil'
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuarios'
        ordering = ['apellidos', 'nombres']
        indexes = [
            models.Index(fields=['dni']),
            models.Index(fields=['estado_cuenta']),
        ]

    def __str__(self):
        return f'{self.dni} - {self.apellidos}, {self.nombres}'


class VerificacionKYC(models.Model):
    """
    Registro del proceso KYC simulado.

    Guarda el resultado de verificación, pero no ejecuta la lógica.
    La lógica se implementará en usuarios/services/kyc_service.py.
    """

    perfil = models.OneToOneField(
        PerfilUsuario,
        on_delete=models.CASCADE,
        related_name='kyc'
    )

    dni_verificado = models.BooleanField(default=False)
    mayor_edad_verificado = models.BooleanField(default=False)

    observacion = models.TextField(
        blank=True,
        null=True
    )

    verificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='kyc_verificados'
    )

    fecha_verificacion = models.DateTimeField(
        blank=True,
        null=True
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usuarios_kyc'
        verbose_name = 'Verificación KYC'
        verbose_name_plural = 'Verificaciones KYC'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['dni_verificado']),
            models.Index(fields=['mayor_edad_verificado']),
        ]

    def __str__(self):
        return f'KYC - {self.perfil.dni}'