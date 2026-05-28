from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.utils.text import slugify
from django.views.generic import TemplateView
from decimal import Decimal

from apuestas_core.models import Bet
from apuestas_core.services.liquidacion_service import (
    anular_apuesta,
    liquidar_apuesta_ganada,
    liquidar_apuesta_perdida,
)
from billetera.models import Account
from billetera.selectors import obtener_saldo_cuenta
from config.choices import EstadoApuesta, EstadoEvento, TipoCuentaLedger, TipoMercado
from eventos.models import Deporte, Equipo, Evento, Liga
from juego_responsable.services.limites_service import obtener_resumen_limites_deposito
from mercados.services.football_markets_service import ordered_selections
from usuarios.models import PerfilUsuario

from .forms import DeporteAdminForm, EquipoAdminForm, EventoAdminForm, EventoLigaUpdateForm, LigaAdminForm


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class MisApuestasView(LoginRequiredMixin, TemplateView):
    template_name = 'panel/mis_apuestas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from decimal import Decimal

        mostrar_todos_clientes = (
            self.request.user.is_staff or self.request.user.is_superuser
        )

        apuestas_qs = (
            Bet.objects
            .select_related('usuario')
            .prefetch_related(
                'selecciones__seleccion__mercado__evento__equipo_local',
                'selecciones__seleccion__mercado__evento__equipo_visitante',
                'selecciones__seleccion__mercado',
            )
            .order_by('-fecha_creacion')
        )

        if not mostrar_todos_clientes:
            apuestas_qs = apuestas_qs.filter(usuario=self.request.user)

        apuestas = list(
            apuestas_qs
        )

        count_all       = len(apuestas)
        count_activas   = sum(1 for b in apuestas if b.estado == EstadoApuesta.ACCEPTED)
        count_ganadas   = sum(1 for b in apuestas if b.estado == EstadoApuesta.WON)
        count_perdidas  = sum(1 for b in apuestas if b.estado == EstadoApuesta.LOST)
        count_anuladas  = sum(1 for b in apuestas if b.estado in (EstadoApuesta.VOID, EstadoApuesta.CANCELLED))

        total_apostado  = sum(b.stake for b in apuestas if b.estado != EstadoApuesta.VOID)
        total_cobrado   = sum(b.payout_final for b in apuestas if b.estado == EstadoApuesta.WON and b.payout_final)
        saldo_perdido = sum(b.stake for b in apuestas if b.estado == EstadoApuesta.LOST)
        pago_potencial  = sum(b.payout_potencial for b in apuestas if b.estado == EstadoApuesta.ACCEPTED)

        odds_vals = [b.odds_total for b in apuestas if b.odds_total and b.estado != EstadoApuesta.VOID]
        cuota_promedio  = (sum(odds_vals) / len(odds_vals)) if odds_vals else Decimal('0')

        context.update({
            'apuestas': apuestas,
            'mostrar_todos_clientes': mostrar_todos_clientes,
            'count_all': count_all,
            'count_activas': count_activas,
            'count_ganadas': count_ganadas,
            'count_perdidas': count_perdidas,
            'count_anuladas': count_anuladas,
            'total_apostado': total_apostado,
            'total_cobrado': total_cobrado,
            'saldo_perdido': saldo_perdido,
            'pago_potencial': pago_potencial,
            'cuota_promedio': cuota_promedio,
        })
        context.update(get_saldos_usuario(self.request.user))
        return context


class BilleteraView(LoginRequiredMixin, TemplateView):
    template_name = 'panel/billetera.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_saldos_usuario(self.request.user, incluir_limites=True))
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'panel/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        eventos = list(
            Evento.objects
            .filter(activo=True)
            .select_related('deporte', 'liga', 'equipo_local', 'equipo_visitante')
            .prefetch_related('mercados__selecciones__odd')
            .order_by('liga__nombre', 'fecha_inicio')
        )

        live_count = sum(1 for e in eventos if e.estado == EstadoEvento.EN_VIVO)

        # Attach primary (first active) market to each event — uses prefetch cache
        for evento in eventos:
            evento.mercado_principal = next(
                (
                    m for m in evento.mercados.all()
                    if m.activo and not m.suspendido and m.tipo == TipoMercado.UNO_X_DOS
                ),
                None,
            )
            if evento.mercado_principal:
                evento.mercado_principal.selecciones_ordenadas = ordered_selections(
                    evento.mercado_principal.selecciones.all()
                )
            evento.mercados_extra = []
            for mercado in evento.mercados.all():
                if (
                    mercado.activo
                    and not mercado.suspendido
                    and mercado.tipo != TipoMercado.UNO_X_DOS
                ):
                    mercado.selecciones_ordenadas = ordered_selections(mercado.selecciones.all())
                    evento.mercados_extra.append(mercado)

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

        # Group events by liga for main content
        ligas_map = {}
        for evento in eventos:
            liga_key  = slugify(evento.liga.nombre) if evento.liga else 'sin-liga'
            liga_nombre = evento.liga.nombre if evento.liga else 'Sin liga asignada'
            dep_nombre = evento.deporte.nombre
            dep_key   = slugify(dep_nombre)
            if liga_key not in ligas_map:
                ligas_map[liga_key] = {
                    'key': liga_key,
                    'nombre': liga_nombre,
                    'deporte': dep_nombre,
                    'deporte_key': dep_key,
                    'pais': evento.liga.pais if evento.liga else '',
                    'eventos': [],
                }
            ligas_map[liga_key]['eventos'].append(evento)

        # Sidebar built from ALL active ligas (so they always appear even without events)
        all_ligas = Liga.objects.filter(activa=True).select_related('deporte').order_by('deporte__nombre', 'nombre')
        deportes_map = {}
        for liga in all_ligas:
            dep_nombre = liga.deporte.nombre
            dep_key    = slugify(dep_nombre)
            liga_key   = slugify(liga.nombre)
            if dep_key not in deportes_map:
                deportes_map[dep_key] = {'nombre': dep_nombre, 'key': dep_key, 'ligas': []}
            deportes_map[dep_key]['ligas'].append({'key': liga_key, 'nombre': liga.nombre})

        context['ligas_agrupadas'] = list(ligas_map.values())
        context['deportes_sidebar'] = list(deportes_map.values())
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
            .select_related('deporte', 'liga', 'equipo_local', 'equipo_visitante')
            .prefetch_related('mercados__selecciones__odd')
            .order_by('liga__nombre', 'fecha_inicio')
        )

        ligas_map = {}
        deportes_map = {}
        live_count = 0

        for evento in eventos:
            # Agrupar por liga
            liga_key = slugify(evento.liga.nombre) if evento.liga else 'sin-liga'
            liga_nombre = evento.liga.nombre if evento.liga else 'Sin liga asignada'
            if liga_key not in ligas_map:
                ligas_map[liga_key] = {
                    'key': liga_key,
                    'nombre': liga_nombre,
                    'deporte': evento.deporte.nombre,
                    'eventos': [],
                }
            ligas_map[liga_key]['eventos'].append(evento)

            # Filtros por deporte (para tabs)
            dep_key = slugify(evento.deporte.nombre)
            if dep_key not in deportes_map:
                deportes_map[dep_key] = {
                    'nombre': evento.deporte.nombre,
                    'key': dep_key,
                    'count': 0,
                }
            deportes_map[dep_key]['count'] += 1

            if evento.estado == EstadoEvento.EN_VIVO:
                live_count += 1

        context['eventos'] = eventos
        context['ligas'] = list(ligas_map.values())
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

        from django.utils import timezone as tz
        from django.db.models import Q
        hoy = tz.now().date()
        apuestas_todas = (
            Bet.objects
            .select_related('usuario')
            .prefetch_related(
                'selecciones__seleccion__mercado__evento__equipo_local',
                'selecciones__seleccion__mercado__evento__equipo_visitante',
            )
            .filter(
                Q(fecha_creacion__date=hoy) | Q(estado=EstadoApuesta.ACCEPTED)
            )
            .order_by('estado', '-fecha_creacion')
        )

        context.update({
            'deporte_form': kwargs.get('deporte_form') or DeporteAdminForm(),
            'liga_form': kwargs.get('liga_form') or LigaAdminForm(),
            'equipo_form': kwargs.get('equipo_form') or EquipoAdminForm(),
            'evento_form': kwargs.get('evento_form') or EventoAdminForm(),
            'deportes_lista': Deporte.objects.order_by('nombre'),
            'ligas_lista': Liga.objects.select_related('deporte').order_by('deporte__nombre', 'nombre'),
            'deportes_count': Deporte.objects.count(),
            'ligas_count': Liga.objects.count(),
            'equipos_count': Equipo.objects.count(),
            'eventos_count': Evento.objects.count(),
            'apuestas_count': Bet.objects.count(),
            'usuarios_count': PerfilUsuario.objects.count(),
            'apuestas_recientes_admin': apuestas,
            'eventos_recientes_admin': eventos,
            'apuestas_todas': apuestas_todas,
            'apuestas_pendientes_count': Bet.objects.filter(estado=EstadoApuesta.ACCEPTED).count(),
            'apuestas_won_count': Bet.objects.filter(estado=EstadoApuesta.WON).count(),
            'apuestas_lost_count': Bet.objects.filter(estado=EstadoApuesta.LOST).count(),
            'apuestas_void_count': Bet.objects.filter(estado=EstadoApuesta.VOID).count(),
            'eventos_lista': (
                Evento.objects
                .select_related('deporte', 'liga', 'equipo_local', 'equipo_visitante')
                .order_by('-fecha_creacion')
            ),
            'ligas_lista_all': Liga.objects.filter(activa=True).select_related('deporte').order_by('nombre'),
        })
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if action == 'liquidar':
            return self._handle_liquidar(request)

        if action == 'update_liga':
            form = EventoLigaUpdateForm(request.POST)
            if form.is_valid():
                try:
                    evento = form.save()
                    liga_nombre = evento.liga.nombre if evento.liga else 'Sin liga'
                    messages.success(request, f'Liga de "{evento.nombre}" actualizada a "{liga_nombre}".')
                except Exception as exc:
                    messages.error(request, str(exc))
            else:
                messages.error(request, 'Error al actualizar la liga.')
            return redirect('/admin-panel/#eventos')

        form_map = {
            'deporte': DeporteAdminForm,
            'liga': LigaAdminForm,
            'equipo': EquipoAdminForm,
            'evento': EventoAdminForm,
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
                    return redirect('/admin-panel/#eventos')
                elif action == 'liga':
                    form.save()
                    messages.success(request, 'Liga creada correctamente.')
                    return redirect('/admin-panel/#ligas')
                elif action == 'equipo':
                    form.save()
                    messages.success(request, 'Equipo creado correctamente.')
                    return redirect('/admin-panel/#equipos')
                else:
                    form.save()
                    messages.success(request, 'Deporte creado correctamente.')
                    return redirect('/admin-panel/#deportes')
            except Exception as exc:
                form.add_error(None, str(exc))

        context_key = f'{action}_form'
        context = self.get_context_data(**{context_key: form})
        return self.render_to_response(context)

    def _handle_liquidar(self, request):
        from django.utils import timezone as tz
        bet_id = request.POST.get('bet_id')
        resultado = request.POST.get('resultado')
        ikey = f'admin-liq-{bet_id}-{int(tz.now().timestamp())}'
        try:
            if resultado == 'won':
                liquidar_apuesta_ganada(bet_id=bet_id, idempotency_key=ikey, liquidado_por=request.user)
                messages.success(request, f'Apuesta #{bet_id} marcada como Ganada.')
            elif resultado == 'lost':
                liquidar_apuesta_perdida(bet_id=bet_id, idempotency_key=ikey, liquidado_por=request.user)
                messages.success(request, f'Apuesta #{bet_id} marcada como Perdida.')
            elif resultado == 'void':
                anular_apuesta(bet_id=bet_id, idempotency_key=ikey, anulado_por=request.user)
                messages.success(request, f'Apuesta #{bet_id} anulada.')
            else:
                messages.error(request, 'Resultado no válido.')
        except Exception as exc:
            messages.error(request, str(exc))
        return redirect('/admin-panel/#apuestas')


def get_saldos_usuario(usuario, incluir_limites=False):
    saldo_virtual = get_saldo_por_tipo(usuario, TipoCuentaLedger.WALLET_USUARIO)
    saldo_en_juego = get_saldo_por_tipo(usuario, TipoCuentaLedger.APUESTAS_PENDIENTES)
    saldo_total = saldo_virtual + saldo_en_juego

    saldos = {
        'saldo_virtual': saldo_virtual,
        'saldo_en_juego': saldo_en_juego,
        'saldo_total': saldo_total,
    }

    if incluir_limites:
        saldos['limites_deposito'] = obtener_resumen_limites_deposito(usuario)

    return saldos


def get_saldo_por_tipo(usuario, tipo):
    cuenta = Account.objects.filter(
        usuario=usuario,
        tipo=tipo,
        activa=True,
    ).first()

    if not cuenta:
        return Decimal('0.0000')

    return obtener_saldo_cuenta(cuenta)
