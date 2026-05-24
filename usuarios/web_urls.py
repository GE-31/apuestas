"""
usuarios/web_urls.py — Rutas web de autenticación (no API).

Separado de usuarios/urls.py que contiene los viewsets de DRF.
Se incluye en config/urls.py bajo el prefijo vacío ''.
"""

from django.urls import path

from .views import LoginAdminView, LoginClienteView, LogoutView

app_name = 'auth'

urlpatterns = [
    path('login/',        LoginClienteView.as_view(), name='login_cliente'),
    path('admin-login/',  LoginAdminView.as_view(),   name='login_admin'),
    path('logout/',       LogoutView.as_view(),        name='logout'),
]
