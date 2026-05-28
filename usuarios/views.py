import urllib.request
import urllib.error
import json

from django.conf import settings
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views import View

from .forms import LoginAdminForm, LoginClienteForm, RegistroClienteForm
from .models import EstadoSesionUsuario


def marcar_sesion_usuario(user, activa):
    if not user or not user.is_authenticated:
        return
    estado, _ = EstadoSesionUsuario.objects.get_or_create(usuario=user)
    estado.sesion_activa = activa
    now = timezone.now()
    update_fields = ['sesion_activa', 'fecha_actualizacion']
    if activa:
        estado.ultima_conexion = now
        update_fields.append('ultima_conexion')
    else:
        estado.ultima_salida = now
        update_fields.append('ultima_salida')
    estado.save(update_fields=update_fields)


def obtener_ip_request(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def auditar_sesion_request(request, user, accion):
    if not user or not user.is_authenticated:
        return
    try:
        from auditoria.services.audit_service import auditar_sesion_cuenta

        auditar_sesion_cuenta(
            usuario=user,
            accion=accion,
            ip_origen=obtener_ip_request(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
    except Exception:
        pass


class HomeRedirectView(View):
    """Entrada principal: siempre muestra primero el login."""

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            marcar_sesion_usuario(request.user, False)
            auditar_sesion_request(request, request.user, 'logout')
            logout(request)
        return redirect('/login/')


class LoginClienteView(FormView):
    """
    Login para clientes regulares.
    - Si el usuario ya está autenticado, redirige según rol.
    - Tras autenticación exitosa: clientes → dashboard, staff → admin.
    """

    template_name = 'auth/login_cliente.html'
    form_class = LoginClienteForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self._success_url(request.user))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        marcar_sesion_usuario(user, True)
        auditar_sesion_request(self.request, user, 'login')
        return redirect(self._success_url(user))

    def _success_url(self, user):
        if user.is_staff or user.is_superuser:
            return '/admin-panel/'
        return '/inicio/'


class LoginAdminView(FormView):
    """
    Login exclusivo para administradores y staff.
    - Si el usuario no es staff/superuser, el formulario es válido
      pero se añade un error de permisos (no se autentica).
    - Nunca autentica a un usuario sin permisos de admin.
    """

    template_name = 'auth/login_admin.html'
    form_class = LoginAdminForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return redirect('/admin-panel/')
            return redirect('/eventos/')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = form.get_user()
        if not (user.is_staff or user.is_superuser):
            form.add_error(
                None,
                'No tienes permisos de administrador para acceder a este panel.'
            )
            return self.form_invalid(form)
        login(self.request, user)
        marcar_sesion_usuario(user, True)
        auditar_sesion_request(self.request, user, 'login')
        return redirect('/admin-panel/')


class RegistroClienteView(FormView):
    """
    Registro de nuevos clientes.
    GET  → formulario vacío.
    POST → crea User + PerfilUsuario y autenticar, redirige al dashboard.
    """

    template_name = 'auth/registro_cliente.html'
    form_class    = RegistroClienteForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/eventos/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        marcar_sesion_usuario(user, True)
        auditar_sesion_request(self.request, user, 'login')
        return redirect('/eventos/')


class ConsultarDniView(View):
    """
    Proxy hacia API Peru — consulta DNI.
    El token queda en el servidor; el frontend nunca lo ve.
    Solo acepta GET con DNI de 8 dígitos.
    """

    def get(self, request, dni, *args, **kwargs):
        if not dni.isdigit() or len(dni) != 8:
            return JsonResponse({'error': 'DNI inválido.'}, status=400)

        token = getattr(settings, 'APISPERU_TOKEN', '')
        url = f'https://dniruc.apisperu.com/api/v1/dni/{dni}?token={token}'

        try:
            req = urllib.request.Request(url, headers={'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return JsonResponse({'error': f'API Peru respondió con error {e.code}.'}, status=502)
        except Exception:
            return JsonResponse({'error': 'No se pudo contactar la API Peru.'}, status=502)

        # La API devuelve: nombres, apellidoPaterno, apellidoMaterno, dni
        nombres   = data.get('nombres', '')
        ap_pat    = data.get('apellidoPaterno', '')
        ap_mat    = data.get('apellidoMaterno', '')
        apellidos = f'{ap_pat} {ap_mat}'.strip()

        if not nombres and not apellidos:
            return JsonResponse({'error': 'DNI no encontrado.'}, status=404)

        return JsonResponse({
            'nombres':   nombres.title(),
            'apellidos': apellidos.title(),
            'dni':       data.get('dni', dni),
        })


class VerificarDniView(View):
    """
    Comprueba en BD si un DNI ya está registrado.
    Responde { "duplicate": true/false } — sin exponer datos personales.
    """

    def get(self, request, dni, *args, **kwargs):
        from usuarios.models import PerfilUsuario
        if not dni.isdigit() or not (1 <= len(dni) <= 12):
            return JsonResponse({'duplicate': False})
        duplicate = PerfilUsuario.objects.filter(dni=dni).exists()
        return JsonResponse({'duplicate': duplicate})


class LogoutView(FormView):
    """
    Cierra la sesión y redirige al login de clientes.
    Acepta GET y POST.
    """

    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        return self._do_logout(request)

    def post(self, request, *args, **kwargs):
        return self._do_logout(request)

    def _do_logout(self, request):
        user = request.user
        marcar_sesion_usuario(request.user, False)
        auditar_sesion_request(request, user, 'logout')
        logout(request)
        return redirect('/login/')


class PoliticaPrivacidadView(TemplateView):
    template_name = 'legal/politica_privacidad.html'
