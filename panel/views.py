from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.utils.text import slugify
from django.views.generic import TemplateView
from decimal import Decimal

from apuestas_core.models import Bet
from billetera.models import Account
from billetera.selectors import obtener_saldo_cuenta
from config.choices import EstadoApuesta, EstadoEvento, TipoCuentaLedger
from eventos.models import Deporte, Equipo, Evento
from usuarios.models import PerfilUsuario

from .forms import ApuestaAdminForm, EquipoAdminForm, EventoAdminForm, RecargaAdminForm


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class MisApuestasView(LoginRequiredMixin, TemplateView):
    template_name = 'panel/mis_apuestas.html'


class BilleteraView(LoginRequiredMixin, TemplateView):
    template_name = 'panel/billetera.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_saldos_usuario(self.request.user))
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
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
        context.update(get_saldos_usuario(self.request.user))
        return context


class EventosView(LoginRequiredMixin, TemplateView):
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
        context['user_id'] = self.request.user.id
        return context


class AdminPanelView(StaffRequiredMixin, TemplateView):
    template_name = 'panel/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        apuestas = Bet.objects.select_related('usuario').order_by('-fecha_creacion')[:8]
        eventos = (
            Evento.objects
            .select_related('deporte', 'equipo_local', 'equipo_visitante')
            .order_by('-fecha_creacion')[:8]
        )

        context.update({
            'equipo_form': kwargs.get('equipo_form') or EquipoAdminForm(),
            'evento_form': kwargs.get('evento_form') or EventoAdminForm(),
            'recarga_form': kwargs.get('recarga_form') or RecargaAdminForm(),
            'apuesta_form': kwargs.get('apuesta_form') or ApuestaAdminForm(),
            'deportes_count': Deporte.objects.count(),
            'equipos_count': Equipo.objects.count(),
            'eventos_count': Evento.objects.count(),
            'apuestas_count': Bet.objects.count(),
            'usuarios_count': PerfilUsuario.objects.count(),
            'apuestas_recientes_admin': apuestas,
            'eventos_recientes_admin': eventos,
        })
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        form_map = {
            'equipo': EquipoAdminForm,
            'evento': EventoAdminForm,
            'recarga': RecargaAdminForm,
            'apuesta': ApuestaAdminForm,
        }
        form_class = form_map.get(action)
        if not form_class:
            messages.error(request, 'Accion no reconocida.')
            return redirect('/admin-panel/')

        form = form_class(request.POST)
        if form.is_valid():
            try:
                if action == 'evento':
                    form.save(request.user)
                    messages.success(request, 'Evento, mercado y cuotas creados correctamente.')
                elif action == 'recarga':
                    form.save(request.user)
                    messages.success(request, 'Fichas recargadas y guardadas en la base de datos.')
                elif action == 'apuesta':
                    form.save(request)
                    messages.success(request, 'Apuesta creada correctamente.')
                else:
                    form.save()
                    messages.success(request, 'Equipo creado correctamente.')
                return redirect('/admin-panel/')
            except Exception as exc:
                form.add_error(None, str(exc))

        context_key = f'{action}_form'
        context = self.get_context_data(**{context_key: form})
        return self.render_to_response(context)


def get_saldos_usuario(usuario):
    saldo_virtual = get_saldo_por_tipo(usuario, TipoCuentaLedger.WALLET_USUARIO)
    saldo_en_juego = get_saldo_por_tipo(usuario, TipoCuentaLedger.APUESTAS_PENDIENTES)
    saldo_total = saldo_virtual + saldo_en_juego

    return {
        'saldo_virtual': saldo_virtual,
        'saldo_en_juego': saldo_en_juego,
        'saldo_total': saldo_total,
    }


def get_saldo_por_tipo(usuario, tipo):
    cuenta = Account.objects.filter(
        usuario=usuario,
        tipo=tipo,
        activa=True,
    ).first()

    if not cuenta:
        return Decimal('0.0000')

    return obtener_saldo_cuenta(cuenta)
