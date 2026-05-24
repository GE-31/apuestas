from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', include('usuarios.web_urls')),   # /login/ /admin-login/ /logout/
    path('', include('panel.urls')),          # / /eventos/
]
