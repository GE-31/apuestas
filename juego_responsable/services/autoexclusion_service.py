from django.db import transaction
from django.utils import timezone

from config.choices import DuracionAutoexclusion, EstadoAutoexclusion, EstadoCuenta
from juego_responsable.models import Autoexclusion


class AutoexclusionError(Exception):
    pass


def calcular_fecha_fin_autoexclusion(duracion, fecha_inicio=None):
    """
    Calcula la fecha fin según la duración elegida.
    Si es indefinida, devuelve None.
    """

    fecha_inicio = fecha_inicio or timezone.now()

    if duracion == DuracionAutoexclusion.SIETE_DIAS:
        return fecha_inicio + timezone.timedelta(days=7)

    if duracion == DuracionAutoexclusion.TREINTA_DIAS:
        return fecha_inicio + timezone.timedelta(days=30)

    if duracion == DuracionAutoexclusion.NOVENTA_DIAS:
        return fecha_inicio + timezone.timedelta(days=90)

    if duracion == DuracionAutoexclusion.INDEFINIDA:
        return None

    raise AutoexclusionError("Duración de autoexclusión inválida.")


def obtener_autoexclusion_activa(usuario):
    """
    Retorna la autoexclusión activa del usuario si existe.
    """

    ahora = timezone.now()

    return (
        Autoexclusion.objects
        .filter(
            usuario=usuario,
            estado=EstadoAutoexclusion.ACTIVA,
        )
        .filter(
            # Indefinida: fecha_fin null
            # Temporal vigente: fecha_fin mayor a ahora
            models_q_fecha_fin_null_o_futura(ahora)
        )
        .order_by('-fecha_inicio')
        .first()
    )


def models_q_fecha_fin_null_o_futura(ahora):
    """
    Separado para mantener legible la consulta.
    """
    from django.db.models import Q

    return Q(fecha_fin__isnull=True) | Q(fecha_fin__gt=ahora)


def usuario_tiene_autoexclusion_activa(usuario):
    """
    Indica si el usuario tiene autoexclusión activa.
    """

    return obtener_autoexclusion_activa(usuario) is not None


def validar_usuario_no_autoexcluido(usuario):
    """
    Bloquea apuestas si el usuario tiene autoexclusión activa.
    """

    autoexclusion = obtener_autoexclusion_activa(usuario)

    if autoexclusion:
        raise AutoexclusionError(
            "El usuario tiene una autoexclusión activa y no puede apostar."
        )

    return True


@transaction.atomic
def crear_autoexclusion(
    *,
    usuario,
    duracion,
    motivo=None,
    creada_por=None,
):
    """
    Crea una autoexclusión para el usuario.

    Regla:
    - Si ya tiene una autoexclusión activa, no se crea otra.
    - La autoexclusión bloquea apuestas.
    - Si el perfil del usuario existe, se marca como autoexcluido.
    """

    if usuario_tiene_autoexclusion_activa(usuario):
        raise AutoexclusionError(
            "El usuario ya tiene una autoexclusión activa."
        )

    fecha_inicio = timezone.now()
    fecha_fin = calcular_fecha_fin_autoexclusion(
        duracion=duracion,
        fecha_inicio=fecha_inicio,
    )

    autoexclusion = Autoexclusion.objects.create(
        usuario=usuario,
        estado=EstadoAutoexclusion.ACTIVA,
        duracion=duracion,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        motivo=motivo,
        creada_por=creada_por,
    )

    perfil = getattr(usuario, "perfil_apuestas", None)

    if perfil:
        perfil.estado_cuenta = EstadoCuenta.AUTOEXCLUIDO
        perfil.save(update_fields=["estado_cuenta", "fecha_actualizacion"])

    return autoexclusion


@transaction.atomic
def finalizar_autoexclusiones_vencidas():
    """
    Marca como finalizadas las autoexclusiones temporales vencidas.

    Ojo:
    - Las indefinidas no vencen porque fecha_fin es None.
    """

    ahora = timezone.now()

    autoexclusiones = Autoexclusion.objects.filter(
        estado=EstadoAutoexclusion.ACTIVA,
        fecha_fin__isnull=False,
        fecha_fin__lte=ahora,
    )

    cantidad = autoexclusiones.update(
        estado=EstadoAutoexclusion.FINALIZADA,
        fecha_actualizacion=ahora,
    )

    return cantidad