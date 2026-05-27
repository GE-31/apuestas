from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.views.generic.edit import FormView

from .forms import LoginAdminForm, LoginClienteForm, RegistroClienteForm


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
            return '/admin/'
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
                return redirect('/admin/')
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
        return redirect('/admin/')


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
