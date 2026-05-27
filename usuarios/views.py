import urllib.request
import urllib.error
import json

from django.conf import settings
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views import View

from .forms import LoginAdminForm, LoginClienteForm, RegistroClienteForm


class HomeRedirectView(View):
    """Entrada principal: siempre muestra primero el login."""

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
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
        return redirect(self._success_url(user))

    def _success_url(self, user):
        if user.is_staff or user.is_superuser:
            return '/admin-panel/'
        return '/eventos/'


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
        logout(request)
        return redirect('/login/')


class PoliticaPrivacidadView(TemplateView):
    template_name = 'legal/politica_privacidad.html'
