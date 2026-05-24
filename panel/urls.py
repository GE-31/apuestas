from django.urls import path

from .views import DashboardView, EventosView

app_name = 'panel'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('eventos/', EventosView.as_view(), name='eventos'),
]
