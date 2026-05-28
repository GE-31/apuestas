from django.urls import path

from .views import AdminPanelView, BilleteraView, DashboardView, EventosView, MisApuestasView
from auditoria.views import AuditoriaView

app_name = 'panel'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('inicio/', DashboardView.as_view(), name='inicio'),
    path('eventos/', EventosView.as_view(), name='eventos'),
    path('mis-apuestas/', MisApuestasView.as_view(), name='mis_apuestas'),
    path('billetera/', BilleteraView.as_view(), name='billetera'),
    path('admin-panel/', AdminPanelView.as_view(), name='admin_panel'),
    path('admin-panel/auditoria/', AuditoriaView.as_view(), name='admin_auditoria'),
    path('auditoria/', AuditoriaView.as_view(), name='auditoria'),
]
