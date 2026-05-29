from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic import TemplateView
from decimal import Decimal

from apuestas_core.models import Bet
from apuestas_core.services.cashout_service import cashout_apuesta
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

    def post(self, request, *args, **kwargs):
        if request.POST.get('action') != 'cashout':
            return redirect('/mis-apuestas/')

        bet_id = request.POST.get('bet_id')
        try:
            cashout_apuesta(
                bet_id=bet_id,
                idempotency_key=f'cashout-web-{bet_id}-{int(timezone.now().timestamp())}',
                solicitado_por=request.user,
            )
            messages.success(request, f'Cashout aplicado a la apuesta #{bet_id}.')
        except Exception as exc:
            messages.error(request, str(exc))
        return redirect('/mis-apuestas/')

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

        from apuestas_core.services.cashout_service import (
            calcular_valor_cashout,
            es_cashout_disponible,
        )
        ahora = timezone.now()
        for apuesta in apuestas:
            apuesta.cashout_disponible = False
            apuesta.cashout_valor = None
            if apuesta.estado == EstadoApuesta.ACCEPTED:
                apuesta.cashout_disponible = es_cashout_disponible(apuesta, ahora)
                if apuesta.cashout_disponible:
                    apuesta.cashout_valor = calcular_valor_cashout(apuesta)

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
        estado_filtro = self.request.GET.get('estado')
        solo_en_vivo = estado_filtro in ('en_vivo', 'live')
        eventos_visibles = [
            evento for evento in eventos
            if not solo_en_vivo or evento.estado == EstadoEvento.EN_VIVO
        ]

        hoy = timezone.localdate()
        live_count = sum(1 for e in eventos if e.estado == EstadoEvento.EN_VIVO)
        eventos_hoy_count = sum(
            1 for e in eventos
            if timezone.localtime(e.fecha_inicio).date() == hoy
        )

        # Attach primary market and sort selections LOCAL → EMPATE → VISITANTE
        mercados_extra_principales = [
            TipoMercado.OVER_UNDER_25,
            TipoMercado.BTTS,
            TipoMercado.DOUBLE_CHANCE,
            TipoMercado.DRAW_NO_BET,
        ]
        mercados_extra_order = {
            tipo: index for index, tipo in enumerate(mercados_extra_principales)
        }

        for evento in eventos_visibles:
            mp = next(
                (
                    m for m in evento.mercados.all()
                    if m.activo and not m.suspendido and m.tipo == TipoMercado.UNO_X_DOS
                ),
                None,
            )
            evento.mercado_principal = mp
            if mp:
                mp.selecciones_ordenadas = ordered_selections(mp.selecciones.all())
            evento.mercados_extra = []
            mercados_extra = [
                mercado for mercado in evento.mercados.all()
                if (
                    mercado.activo
                    and not mercado.suspendido
                    and mercado.tipo in mercados_extra_principales
                )
            ]
            mercados_extra.sort(
                key=lambda mercado: mercados_extra_order.get(mercado.tipo, 99)
            )
            for mercado in mercados_extra[:4]:
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

        active_bets = Bet.objects.filter(
            usuario=self.request.user,
            estado=EstadoApuesta.ACCEPTED,
        ).count()
        ultima_apuesta = apuestas[0] if apuestas else None

        # Group events for main content. In live mode, show every live match together,
        # regardless of its league, so the "En vivo" card behaves like a global filter.
        if solo_en_vivo:
            ligas_agrupadas = [{
                'key': 'en-vivo',
                'nombre': 'Partidos en vivo',
                'deporte': 'En vivo',
                'deporte_key': 'en-vivo',
                'pais': 'Todas las ligas',
                'eventos': eventos_visibles,
            }] if eventos_visibles else []
        else:
            ligas_map = {}
            for evento in eventos_visibles:
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
            ligas_agrupadas = list(ligas_map.values())

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

        context['ligas_agrupadas'] = ligas_agrupadas
        context['deportes_sidebar'] = list(deportes_map.values())
        context['total_count'] = len(eventos_visibles)
        context['eventos_hoy_count'] = eventos_hoy_count
        context['live_count'] = live_count
        context['live_filter_active'] = solo_en_vivo
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

        from config.choices import EstadoEvento as EE
        eventos_envivo = (
            Evento.objects
            .select_related('deporte', 'liga', 'equipo_local', 'equipo_visitante')
            .filter(activo=True, estado__in=[EE.PROGRAMADO, EE.EN_VIVO, EE.SUSPENDIDO])
            .order_by('fecha_inicio')
        )

        context.update({
            'deporte_form': kwargs.get('deporte_form') or DeporteAdminForm(),
            'liga_form': kwargs.get('liga_form') or LigaAdminForm(),
            'equipo_form': kwargs.get('equipo_form') or EquipoAdminForm(),
            'evento_form': kwargs.get('evento_form') or EventoAdminForm(),
            'deportes_lista': Deporte.objects.order_by('nombre'),
            'ligas_lista': Liga.objects.select_related('deporte').order_by('deporte__nombre', 'nombre'),
            'eventos_envivo': eventos_envivo,
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

        if action in ('iniciar_en_vivo', 'iniciar_segundo_tiempo', 'actualizar_marcador', 'finalizar_evento', 'suspender_evento'):
            return self._handle_live(request, action)

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
                apuesta, _ = liquidar_apuesta_ganada(bet_id=bet_id, idempotency_key=ikey, liquidado_por=request.user)
                messages.success(request, f'Apuesta #{bet_id} marcada como Ganada.')
            elif resultado == 'lost':
                apuesta, _ = liquidar_apuesta_perdida(bet_id=bet_id, idempotency_key=ikey, liquidado_por=request.user)
                messages.success(request, f'Apuesta #{bet_id} marcada como Perdida.')
            elif resultado == 'void':
                apuesta, _ = anular_apuesta(bet_id=bet_id, idempotency_key=ikey, anulado_por=request.user)
                messages.success(request, f'Apuesta #{bet_id} anulada.')
            else:
                messages.error(request, 'Resultado no válido.')
                return redirect('/admin-panel/#apuestas')

            self._notificar_saldo_ws(apuesta, resultado)

        except Exception as exc:
            messages.error(request, str(exc))
        return redirect('/admin-panel/#apuestas')

    def _handle_live(self, request, action):
        from tiempo_real.services import broadcast_evento_update
        from config.choices import EstadoEvento as EE

        evento_id = request.POST.get('evento_id')
        try:
            evento = Evento.objects.get(pk=evento_id)
        except Evento.DoesNotExist:
            messages.error(request, 'Evento no encontrado.')
            return redirect('/admin-panel/#envivo')

        if evento.estado == EE.FINALIZADO or not evento.activo:
            messages.error(request, 'Este evento ya está finalizado y no puede modificarse.')
            return redirect('/admin-panel/#envivo')

        if action == 'iniciar_en_vivo':
            evento.estado = EE.EN_VIVO
            evento.periodo_en_vivo = 1
            evento.periodo_inicio = timezone.now()
            update_fields = ['estado', 'periodo_en_vivo', 'periodo_inicio']
            if evento.marcador_local is None:
                evento.marcador_local = 0
                update_fields.append('marcador_local')
            if evento.marcador_visitante is None:
                evento.marcador_visitante = 0
                update_fields.append('marcador_visitante')
            evento.save(update_fields=update_fields)
            from cuotas.services.live_odds_service import actualizar_cuotas_vivo
            cuotas_vivo = actualizar_cuotas_vivo(evento)
            broadcast_evento_update(
                evento.id,
                EE.EN_VIVO,
                evento.marcador_local,
                evento.marcador_visitante,
                evento.periodo_inicio.isoformat(),
                evento.periodo_en_vivo,
                cuotas_vivo=cuotas_vivo,
            )
            messages.success(request, f'"{evento.nombre}" ahora está EN VIVO.')

        elif action == 'iniciar_segundo_tiempo':
            evento.estado = EE.EN_VIVO
            evento.periodo_en_vivo = 2
            evento.periodo_inicio = timezone.now()
            evento.save(update_fields=['estado', 'periodo_en_vivo', 'periodo_inicio'])
            from cuotas.services.live_odds_service import actualizar_cuotas_vivo
            cuotas_vivo = actualizar_cuotas_vivo(evento)
            broadcast_evento_update(
                evento.id,
                EE.EN_VIVO,
                evento.marcador_local,
                evento.marcador_visitante,
                evento.periodo_inicio.isoformat(),
                evento.periodo_en_vivo,
                cuotas_vivo=cuotas_vivo,
            )
            messages.success(request, f'Segundo tiempo iniciado para "{evento.nombre}".')

        elif action == 'actualizar_marcador':
            try:
                ml = int(request.POST.get('marcador_local', 0))
                mv = int(request.POST.get('marcador_visitante', 0))
            except (TypeError, ValueError):
                messages.error(request, 'Marcador inválido.')
                return redirect('/admin-panel/#envivo')
            marcador_actual_local = evento.marcador_local or 0
            marcador_actual_visitante = evento.marcador_visitante or 0
            if ml < marcador_actual_local or mv < marcador_actual_visitante:
                messages.error(request, 'El marcador no puede bajar — los goles no se pueden quitar.')
                return redirect('/admin-panel/#envivo')
            evento.marcador_local = ml
            evento.marcador_visitante = mv
            evento.save(update_fields=['marcador_local', 'marcador_visitante'])
            from cuotas.services.live_odds_service import actualizar_cuotas_vivo
            cuotas_vivo = actualizar_cuotas_vivo(evento)
            broadcast_evento_update(
                evento.id,
                evento.estado,
                ml,
                mv,
                evento.periodo_inicio.isoformat() if evento.periodo_inicio else None,
                evento.periodo_en_vivo,
                cuotas_vivo=cuotas_vivo,
            )
            messages.success(request, f'Marcador actualizado: {ml} - {mv}.')

        elif action == 'finalizar_evento':
            evento.estado = EE.FINALIZADO
            evento.activo = False
            evento.save(update_fields=['estado', 'activo'])
            broadcast_evento_update(evento.id, EE.FINALIZADO, evento.marcador_local, evento.marcador_visitante)

            # Auto-liquidar todas las apuestas del evento y notificar saldos
            from apuestas_core.services.autoliquidacion_service import autoliquidar_evento
            from apuestas_core.models import Bet, BetSelection
            from config.choices import EstadoApuesta as EA

            ganadas, perdidas, resultado_1x2 = autoliquidar_evento(evento, liquidado_por=request.user)

            # Notificar por WebSocket a cada usuario cuya apuesta fue liquidada
            bets_liquidadas = Bet.objects.filter(
                selecciones__seleccion__mercado__evento=evento,
                estado__in=[EA.WON, EA.LOST],
            ).select_related('usuario').distinct()
            for bet in bets_liquidadas:
                self._notificar_saldo_ws(
                    bet,
                    'won' if bet.estado == EA.WON else 'lost',
                )

            res_label = {'local': 'Gana local', 'visitante': 'Gana visitante', 'empate': 'Empate'}.get(resultado_1x2, resultado_1x2)
            messages.success(
                request,
                f'"{evento.nombre}" finalizado — {res_label} ({evento.marcador_local}-{evento.marcador_visitante}). '
                f'{ganadas} apuesta(s) pagadas, {perdidas} perdida(s).'
            )

        elif action == 'suspender_evento':
            evento.estado = EE.SUSPENDIDO
            evento.save(update_fields=['estado'])
            broadcast_evento_update(evento.id, EE.SUSPENDIDO, evento.marcador_local, evento.marcador_visitante)
            messages.success(request, f'"{evento.nombre}" suspendido.')

        return redirect('/admin-panel/#envivo')

    def _notificar_saldo_ws(self, apuesta, resultado):
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            from billetera.selectors import obtener_saldo_cuenta
            from billetera.models import Account
            from config.choices import TipoCuentaLedger

            usuario = apuesta.usuario
            wallet = Account.objects.filter(
                usuario=usuario,
                tipo=TipoCuentaLedger.WALLET_USUARIO,
                activa=True,
            ).first()
            if not wallet:
                return

            saldo = float(obtener_saldo_cuenta(wallet))
            mensajes = {'won': '¡Ganaste! Tu saldo fue acreditado.', 'lost': 'Apuesta perdida.', 'void': 'Apuesta anulada. Stake devuelto.'}
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{usuario.id}',
                {
                    'type': 'balance_update',
                    'saldo': round(saldo, 2),
                    'mensaje': mensajes.get(resultado, ''),
                }
            )
        except Exception:
            pass


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
