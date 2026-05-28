from django.contrib.auth import get_user_model

from billetera.serializers import RecargaFichasSerializer, RetiroFichasSerializer
from billetera.services.deposito_service import (
    CuentaSistemaNoEncontradaError,
    recargar_fichas_usuario,
)
from billetera.services.retiro_service import (
    CuentaSistemaNoEncontradaError as CuentaRetiroError,
    NumeroYapeInvalidoError,
    retirar_fichas_usuario,
)
from juego_responsable.services.limites_service import LimiteDepositoError

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
from billetera.services.saldo_service import SaldoInsuficienteError, obtener_resumen_saldo


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

    def _obtener_usuario_operacion(self, request, usuario_id):
        if not request.user.is_authenticated:
            return None, Response({'detail': 'Autenticacion requerida.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            usuario = User.objects.get(pk=usuario_id)
        except User.DoesNotExist:
            return None, Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        puede_operar = request.user.is_staff or request.user.is_superuser or request.user.pk == usuario.pk
        if not puede_operar:
            return None, Response({'detail': 'No puedes operar la billetera de otro usuario.'}, status=status.HTTP_403_FORBIDDEN)

        return usuario, None

    @action(detail=False, methods=['post'])
    def recargar(self, request):
        serializer = RecargaFichasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario, error_response = self._obtener_usuario_operacion(
            request,
            serializer.validated_data['usuario_id'],
        )
        if error_response:
            return error_response

        try:
            transaccion = recargar_fichas_usuario(
                usuario=usuario,
                amount=serializer.validated_data['amount'],
                idempotency_key=serializer.validated_data.get('idempotency_key'),
                creado_por=request.user if request.user.is_authenticated else None,
            )
        except LimiteDepositoError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except (CuentaSistemaNoEncontradaError, CuentaRetiroError) as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        response_serializer = LedgerTransactionSerializer(transaccion)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def retirar(self, request):
        serializer = RetiroFichasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario, error_response = self._obtener_usuario_operacion(
            request,
            serializer.validated_data['usuario_id'],
        )
        if error_response:
            return error_response

        try:
            transaccion = retirar_fichas_usuario(
                usuario=usuario,
                amount=serializer.validated_data['amount'],
                yape_number=serializer.validated_data['yape_number'],
                idempotency_key=serializer.validated_data.get('idempotency_key'),
                creado_por=request.user if request.user.is_authenticated else None,
            )
        except LimiteDepositoError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except SaldoInsuficienteError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except NumeroYapeInvalidoError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except (CuentaSistemaNoEncontradaError, CuentaRetiroError) as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        response_serializer = LedgerTransactionSerializer(transaccion)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
