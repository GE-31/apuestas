from django.contrib.auth import get_user_model

from billetera.serializers import RecargaFichasSerializer, RetiroFichasSerializer
from billetera.services.deposito_service import recargar_fichas_usuario
from billetera.services.retiro_service import retirar_fichas_usuario

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from billetera.models import Account, LedgerEntry, LedgerTransaction
from billetera.serializers import (
    AccountSerializer,
    LedgerEntrySerializer,
    LedgerTransactionSerializer,
    MovimientoSimpleSerializer,
)
from billetera.services.ledger_service import crear_movimiento_simple
from billetera.services.saldo_service import obtener_resumen_saldo


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.select_related('usuario').all()
    serializer_class = AccountSerializer
    search_fields = ['nombre', 'usuario__username', 'usuario__email']
    ordering_fields = ['fecha_creacion', 'tipo', 'nombre']

    @action(detail=True, methods=['get'])
    def saldo(self, request, pk=None):
        account = self.get_object()
        data = obtener_resumen_saldo(account)
        return Response(data)

    @action(detail=True, methods=['get'])
    def movimientos(self, request, pk=None):
        account = self.get_object()
        movimientos = (
            LedgerEntry.objects
            .select_related('transaction', 'account')
            .filter(account=account)
            .order_by('-fecha_creacion')
        )
        serializer = LedgerEntrySerializer(movimientos, many=True)
        return Response(serializer.data)


class LedgerTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        LedgerTransaction.objects
        .select_related('creado_por')
        .prefetch_related('entries')
        .all()
    )
    serializer_class = LedgerTransactionSerializer
    search_fields = ['referencia', 'idempotency_key', 'descripcion']
    ordering_fields = ['fecha_creacion', 'tipo']


class LedgerEntryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        LedgerEntry.objects
        .select_related('transaction', 'account', 'account__usuario')
        .all()
    )
    serializer_class = LedgerEntrySerializer
    search_fields = [
        'transaction__referencia',
        'transaction__idempotency_key',
        'account__nombre',
        'account__usuario__username',
    ]
    ordering_fields = ['fecha_creacion', 'amount', 'direction']


class MovimientoSimpleViewSet(viewsets.ViewSet):
    """
    Endpoint para crear un movimiento simple de partida doble.

    Ejemplo:
    cuenta_debito -> cuenta_credito
    """

    def create(self, request):
        serializer = MovimientoSimpleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cuenta_debito = Account.objects.get(
            pk=serializer.validated_data['cuenta_debito']
        )
        cuenta_credito = Account.objects.get(
            pk=serializer.validated_data['cuenta_credito']
        )

        transaccion = crear_movimiento_simple(
            cuenta_debito=cuenta_debito,
            cuenta_credito=cuenta_credito,
            amount=serializer.validated_data['amount'],
            tipo=serializer.validated_data.get('tipo'),
            referencia=serializer.validated_data.get('referencia'),
            idempotency_key=serializer.validated_data.get('idempotency_key'),
            descripcion=serializer.validated_data.get('descripcion'),
            creado_por=request.user if request.user.is_authenticated else None,
        )

        response_serializer = LedgerTransactionSerializer(transaccion)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
User = get_user_model()
class OperacionesWalletViewSet(viewsets.ViewSet):
    """
    Operaciones de wallet:
    - recarga simulada
    - retiro simulado
    """

    @action(detail=False, methods=['post'])
    def recargar(self, request):
        serializer = RecargaFichasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = User.objects.get(pk=serializer.validated_data['usuario_id'])

        transaccion = recargar_fichas_usuario(
            usuario=usuario,
            amount=serializer.validated_data['amount'],
            idempotency_key=serializer.validated_data.get('idempotency_key'),
            creado_por=request.user if request.user.is_authenticated else None,
        )

        response_serializer = LedgerTransactionSerializer(transaccion)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def retirar(self, request):
        serializer = RetiroFichasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = User.objects.get(pk=serializer.validated_data['usuario_id'])

        transaccion = retirar_fichas_usuario(
            usuario=usuario,
            amount=serializer.validated_data['amount'],
            idempotency_key=serializer.validated_data.get('idempotency_key'),
            creado_por=request.user if request.user.is_authenticated else None,
        )

        response_serializer = LedgerTransactionSerializer(transaccion)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)