"""
usuarios/web_urls.py — Rutas web de autenticación (no API).

Separado de usuarios/urls.py que contiene los viewsets de DRF.
Se incluye en config/urls.py bajo el prefijo vacío ''.
"""

from django.urls import path

from .views import (
    ConsultarDniView,
    HomeRedirectView,
    LoginAdminView,
    LoginClienteView,
    LogoutView,
    PoliticaPrivacidadView,
    RegistroClienteView,
    VerificarDniView,
)

app_name = 'auth'

urlpatterns = [
    path('',                          HomeRedirectView.as_view(),    name='home'),
    path('login/',                    LoginClienteView.as_view(),    name='login_cliente'),
    path('registro/',                 RegistroClienteView.as_view(), name='registro_cliente'),
    path('admin-login/',              LoginAdminView.as_view(),      name='login_admin'),
    path('logout/',                   LogoutView.as_view(),          name='logout'),
    path('consultar-dni/<str:dni>/',  ConsultarDniView.as_view(),    name='consultar_dni'),
    path('verificar-dni/<str:dni>/',  VerificarDniView.as_view(),    name='verificar_dni'),
    path('politica-privacidad/',      PoliticaPrivacidadView.as_view(), name='politica_privacidad'),
]
