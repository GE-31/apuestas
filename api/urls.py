from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from api.views import ApiRootView

urlpatterns = [
    path('', ApiRootView.as_view(), name='api-root'),
    path('schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='api-redoc'),
    path('usuarios/', include('usuarios.urls')),
    path('billetera/', include('billetera.urls')),
    path('apuestas/', include('apuestas_core.urls')),
]
