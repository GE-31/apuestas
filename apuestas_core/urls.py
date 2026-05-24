from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apuestas_core.viewsets import (
    BetSelectionViewSet,
    BetViewSet,
    OperacionesApuestaViewSet,
)

router = DefaultRouter()
router.register(r'apuestas', BetViewSet, basename='apuestas')
router.register(r'selecciones', BetSelectionViewSet, basename='apuestas-selecciones')
router.register(r'operaciones', OperacionesApuestaViewSet, basename='apuestas-operaciones')

urlpatterns = [
    path('', include(router.urls)),
]