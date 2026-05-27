from django.urls import path

from .views import BilleteraView, DashboardView, EventosView, MisApuestasView

app_name = 'panel'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('eventos/', EventosView.as_view(), name='eventos'),
    path('mis-apuestas/', MisApuestasView.as_view(), name='mis_apuestas'),
    path('billetera/', BilleteraView.as_view(), name='billetera'),
]
