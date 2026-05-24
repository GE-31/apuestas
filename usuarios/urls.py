from django.urls import include, path
from rest_framework.routers import DefaultRouter

from usuarios.viewsets import PerfilUsuarioViewSet, VerificacionKYCViewSet

router = DefaultRouter()
router.register(r'perfiles', PerfilUsuarioViewSet, basename='perfil-usuario')
router.register(r'kyc', VerificacionKYCViewSet, basename='verificacion-kyc')

urlpatterns = [
    path('', include(router.urls)),
]