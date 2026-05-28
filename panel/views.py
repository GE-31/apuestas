from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.utils import timezone as tz
from django.utils.dateparse import parse_date
from django.utils.text import slugify
from django.views.generic import TemplateView
from datetime import timedelta
from decimal import Decimal

from apuestas_core.models import Bet
from apuestas_core.services.liquidacion_service import (
    anular_apuesta,
    liquidar_apuesta_ganada,
    liquidar_apuesta_perdida,
)
from auditoria.models import AuditIntegrityCheck, AuditLog
from auditoria.services.audit_service import ejecutar_verificacion_integridad
from billetera.models import Account
from billetera.selectors import obtener_saldo_cuenta
from config.choices import EstadoApuesta, EstadoEvento, TipoCuentaLedger
from eventos.models import Deporte, Equipo, Evento, Liga
from usuarios.models import PerfilUsuario

from .forms import DeporteAdminForm, EquipoAdminForm, EventoAdminForm, LigaAdminForm


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
        auditoria_context = self._get_auditoria_context()

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
        })
        context.update(auditoria_context)
        return context

    def _get_auditoria_context(self):
        hoy = tz.localdate()
        rango = self.request.GET.get('auditoria_rango') or 'ultimos_7'
        fecha_desde = parse_date(self.request.GET.get('auditoria_desde') or '')
        fecha_hasta = parse_date(self.request.GET.get('auditoria_hasta') or '')

        if not fecha_desde and not fecha_hasta:
            if rango == 'hoy':
                fecha_desde = hoy
                fecha_hasta = hoy
            elif rango == 'ultimos_30':
                fecha_desde = hoy - timedelta(days=29)
                fecha_hasta = hoy
            elif rango == 'todos':
                fecha_desde = None
                fecha_hasta = None
            else:
                rango = 'ultimos_7'
                fecha_desde = hoy - timedelta(days=6)
                fecha_hasta = hoy

        logs_queryset = AuditLog.objects.select_related('creado_por').order_by('-fecha_creacion')
        if fecha_desde:
            logs_queryset = logs_queryset.filter(fecha_creacion__date__gte=fecha_desde)
        if fecha_hasta:
            logs_queryset = logs_queryset.filter(fecha_creacion__date__lte=fecha_hasta)

        ultimo_check = (
            AuditIntegrityCheck.objects
            .select_related('ejecutado_por')
            .order_by('-fecha_ejecucion')
            .first()
        )

        return {
            'auditoria_logs': logs_queryset[:50],
            'auditoria_count': AuditLog.objects.count(),
            'auditoria_filtrados_count': logs_queryset.count(),
            'auditoria_integrity_checks': (
                AuditIntegrityCheck.objects
                .select_related('ejecutado_por')
                .order_by('-fecha_ejecucion')[:5]
            ),
            'auditoria_ultimo_check': ultimo_check,
            'auditoria_ultimo_check_errores': (ultimo_check.errores_detectados or [])[:5] if ultimo_check else [],
            'auditoria_filtro_rango': rango,
            'auditoria_fecha_desde': fecha_desde.isoformat() if fecha_desde else '',
            'auditoria_fecha_hasta': fecha_hasta.isoformat() if fecha_hasta else '',
            'auditoria_querystring': self.request.GET.urlencode(),
        }

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if action == 'liquidar':
            return self._handle_liquidar(request)

        if action == 'auditoria_verificar':
            return self._handle_auditoria_verificar(request)

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

    def _handle_auditoria_verificar(self, request):
        next_url = request.POST.get('next') or '/admin-panel/#auditoria'
        if not next_url.startswith('/admin-panel/'):
            next_url = '/admin-panel/#auditoria'

        try:
            check = ejecutar_verificacion_integridad(ejecutado_por=request.user)
            if check.es_valida:
                messages.success(
                    request,
                    f'Cadena de auditoria valida. Registros verificados: {check.total_registros}.'
                )
            else:
                messages.error(
                    request,
                    f'La cadena de auditoria tiene {len(check.errores_detectados or [])} error(es).'
                )
        except Exception as exc:
            messages.error(request, str(exc))
        return redirect(next_url)


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
