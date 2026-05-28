from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.generic import TemplateView

from auditoria.models import AuditLog


class AuditoriaView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'auditoria/auditoria.html'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        req = self.request

        # ── Filtros ──────────────────────────────────────────
        fecha_desde  = req.GET.get('fecha_desde', '')
        fecha_hasta  = req.GET.get('fecha_hasta', '')
        tipo_evento  = req.GET.get('tipo_evento', '')
        buscar       = req.GET.get('buscar', '').strip()
        pagina       = req.GET.get('pagina', 1)
        query_params = {
            key: value
            for key, value in {
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'tipo_evento': tipo_evento,
                'buscar': buscar,
            }.items()
            if value
        }
        querystring = urlencode(query_params)

        fecha_desde_date = parse_date(fecha_desde) if fecha_desde else None
        fecha_hasta_date = parse_date(fecha_hasta) if fecha_hasta else None
        tiene_fecha = bool(fecha_desde_date or fecha_hasta_date)

        qs = (
            AuditLog.objects
            .select_related('creado_por', 'creado_por__estado_sesion_cuenta')
            .order_by('-fecha_creacion')
        )
        if not tiene_fecha:
            qs = qs.none()
        elif fecha_desde_date and fecha_hasta_date:
            qs = qs.filter(
                fecha_creacion__date__gte=fecha_desde_date,
                fecha_creacion__date__lte=fecha_hasta_date,
            )
        else:
            fecha_exacta = fecha_desde_date or fecha_hasta_date
            qs = qs.filter(fecha_creacion__date=fecha_exacta)

        if tipo_evento:
            qs = qs.filter(tipo_evento=tipo_evento)

        if buscar:
            from django.db.models import Q
            qs = qs.filter(
                Q(entidad__icontains=buscar) |
                Q(entidad_id__icontains=buscar) |
                Q(accion__icontains=buscar) |
                Q(creado_por__username__icontains=buscar) |
                Q(ip_origen__icontains=buscar)
            )

        # ── Paginación ───────────────────────────────────────
        paginador = Paginator(qs, 25)
        try:
            pagina_obj = paginador.page(pagina)
        except Exception:
            pagina_obj = paginador.page(1)

        # ── Stats globales ───────────────────────────────────
        hoy = timezone.now().date()
        todos = AuditLog.objects.all()
        stats = {
            'total_hoy':      todos.filter(fecha_creacion__date=hoy).count(),
            'apuestas_hoy':   todos.filter(fecha_creacion__date=hoy, tipo_evento__in=['bet_created', 'bet_settled']).count(),
            'wallet_hoy':     todos.filter(fecha_creacion__date=hoy, tipo_evento='wallet_movement').count(),
            'alertas_hoy':    todos.filter(fecha_creacion__date=hoy, tipo_evento='fraud_alert').count(),
            'total_general':  todos.count(),
        }

        context.update({
            'logs':          pagina_obj,
            'paginador':     paginador,
            'stats':         stats,
            'tipos_evento':  AuditLog.TipoEvento.choices,
            # Filtros activos (para repoblar el form)
            'f_fecha_desde': fecha_desde,
            'f_fecha_hasta': fecha_hasta,
            'f_tipo_evento': tipo_evento,
            'f_buscar':      buscar,
            'tiene_fecha':    tiene_fecha,
            'pagination_prefix': f'{querystring}&' if querystring else '',
        })
        return context
