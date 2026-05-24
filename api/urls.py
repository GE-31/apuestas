from django.urls import include, path

urlpatterns = [
    path('usuarios/', include('usuarios.urls')),
    path('billetera/', include('billetera.urls')),
    path('apuestas/', include('apuestas_core.urls')),
]