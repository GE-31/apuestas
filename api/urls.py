from django.urls import include, path

urlpatterns = [
    path('usuarios/', include('usuarios.urls')),
]