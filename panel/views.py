from django.utils.text import slugify
from django.views.generic import TemplateView

from apuestas_core.models import Bet
from config.choices import EstadoApuesta, EstadoEvento
from eventos.models import Evento


class DashboardView(TemplateView):
    template_name = 'panel/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        eventos = list(
            Evento.objects
            .filter(activo=True)
            .select_related('deporte', 'equipo_local', 'equipo_visitante')
            .prefetch_related('mercados__selecciones__odd')
            .order_by('fecha_inicio')
        )

        live_count = sum(1 for e in eventos if e.estado == EstadoEvento.EN_VIVO)

        apuestas = list(
            Bet.objects
            .select_related('usuario')
            .prefetch_related(
                'selecciones__seleccion__mercado__evento__equipo_local',
                'selecciones__seleccion__mercado__evento__equipo_visitante',
            )
            .order_by('-fecha_creacion')[:10]
        )

        active_bets = sum(1 for b in apuestas if b.estado == EstadoApuesta.ACCEPTED)
        ultima_apuesta = apuestas[0] if apuestas else None

        context['eventos'] = eventos[:5]
        context['evento_destacado'] = eventos[0] if eventos else None
        context['total_count'] = len(eventos)
        context['live_count'] = live_count
        context['active_bets_count'] = active_bets
        context['apuestas_recientes'] = apuestas
        context['ultima_apuesta'] = ultima_apuesta
        return context


class EventosView(TemplateView):
    template_name = 'panel/eventos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        eventos = list(
            Evento.objects
            .filter(activo=True)
            .select_related('deporte', 'equipo_local', 'equipo_visitante')
            .prefetch_related('mercados__selecciones__odd')
            .order_by('fecha_inicio')
        )

        deportes_map = {}
        live_count = 0

        for evento in eventos:
            key = slugify(evento.deporte.nombre)
            if key not in deportes_map:
                deportes_map[key] = {
                    'nombre': evento.deporte.nombre,
                    'key': key,
                    'count': 0,
                }
            deportes_map[key]['count'] += 1

            if evento.estado == EstadoEvento.EN_VIVO:
                live_count += 1

        context['eventos'] = eventos
        context['total_count'] = len(eventos)
        context['deportes'] = list(deportes_map.values())
        context['live_count'] = live_count
        return context
