from django.urls import include, path
from rest_framework.routers import DefaultRouter

from billetera.viewsets import (
    AccountViewSet,
    LedgerEntryViewSet,
    LedgerTransactionViewSet,
    MovimientoSimpleViewSet,
)

router = DefaultRouter()
router.register(r'cuentas', AccountViewSet, basename='cuentas')
router.register(r'transacciones', LedgerTransactionViewSet, basename='transacciones-ledger')
router.register(r'entradas', LedgerEntryViewSet, basename='entradas-ledger')
router.register(r'movimiento-simple', MovimientoSimpleViewSet, basename='movimiento-simple')

urlpatterns = [
    path('', include(router.urls)),
]