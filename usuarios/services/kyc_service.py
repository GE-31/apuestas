from django.utils import timezone

from config.choices import EstadoCuenta
from usuarios.validators import validar_dni_basico, validar_mayoria_edad


def verificar_kyc(perfil, usuario_admin=None, observacion=''):
    dni_valido = validar_dni_basico(perfil.dni)
    mayor_edad = validar_mayoria_edad(perfil.fecha_nacimiento)

    kyc, _ = perfil.kyc.__class__.objects.get_or_create(perfil=perfil)

    kyc.dni_verificado = dni_valido
    kyc.mayor_edad_verificado = mayor_edad
    kyc.observacion = observacion
    kyc.verificado_por = usuario_admin
    kyc.fecha_verificacion = timezone.now()
    kyc.save()

    if dni_valido and mayor_edad:
        perfil.estado_cuenta = EstadoCuenta.VERIFICADO
    else:
        perfil.estado_cuenta = EstadoCuenta.PENDIENTE_VERIFICACION

    perfil.save(update_fields=['estado_cuenta', 'fecha_actualizacion'])

    return kyc