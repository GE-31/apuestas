from celery import shared_task
from django.utils import timezone


@shared_task(name='eventos.auto_activar_programados')
def auto_activar_eventos_programados():
    """
    Revisa cada minuto si hay eventos PROGRAMADOS cuya hora ya llegó
    y los activa en vivo automáticamente.
    """
    from config.choices import EstadoEvento
    from eventos.models import Evento
    from tiempo_real.services import broadcast_evento_update
    from cuotas.services.live_odds_service import actualizar_cuotas_vivo

    ahora = timezone.now()

    eventos = Evento.objects.filter(
        estado=EstadoEvento.PROGRAMADO,
        activo=True,
        fecha_inicio__lte=ahora,
    ).select_related('deporte', 'liga', 'equipo_local', 'equipo_visitante')

    activados = 0
    for evento in eventos:
        evento.estado = EstadoEvento.EN_VIVO
        evento.periodo_en_vivo = 1
        evento.periodo_inicio = ahora
        if evento.marcador_local is None:
            evento.marcador_local = 0
        if evento.marcador_visitante is None:
            evento.marcador_visitante = 0
        evento.save(update_fields=[
            'estado', 'periodo_en_vivo', 'periodo_inicio',
            'marcador_local', 'marcador_visitante',
        ])

        cuotas_vivo = actualizar_cuotas_vivo(evento)

        broadcast_evento_update(
            evento.id,
            EstadoEvento.EN_VIVO,
            evento.marcador_local,
            evento.marcador_visitante,
            evento.periodo_inicio.isoformat(),
            evento.periodo_en_vivo,
            cuotas_vivo=cuotas_vivo,
        )
        activados += 1

    return f'{activados} evento(s) activados en vivo.'
