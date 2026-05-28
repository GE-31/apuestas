from django.contrib.auth import get_user_model

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apuestas_core.models import Bet, BetSelection
from apuestas_core.serializers import (
    BetSerializer,
    BetSelectionSerializer,
    CrearApuestaCombinadaSerializer,
    CrearApuestaSimpleSerializer,
    LiquidarApuestaSerializer,
)
from apuestas_core.services.apuesta_service import crear_apuesta_combinada, crear_apuesta_simple
from apuestas_core.services.cashout_service import cashout_apuesta
from apuestas_core.services.liquidacion_service import (
    anular_apuesta,
    liquidar_apuesta_ganada,
    liquidar_apuesta_perdida,
)

User = get_user_model()


class BetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Bet.objects
        .select_related('usuario')
        .prefetch_related(
            'selecciones',
            'selecciones__seleccion',
            'selecciones__seleccion__mercado',
            'selecciones__seleccion__mercado__evento',
            'selecciones__odd',
        )
        .all()
    )
    serializer_class = BetSerializer
    search_fields = [
        'usuario__username',
        'usuario__email',
        'idempotency_key',
        'ip_origen',
    ]
    ordering_fields = [
        'fecha_creacion',
        'stake',
        'odds_total',
        'payout_potencial',
        'estado',
    ]


class BetSelectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        BetSelection.objects
        .select_related(
            'bet',
            'bet__usuario',
            'seleccion',
            'seleccion__mercado',
            'seleccion__mercado__evento',
            'odd',
        )
        .all()
    )
    serializer_class = BetSelectionSerializer
    search_fields = [
        'bet__usuario__username',
        'seleccion__nombre',
        'seleccion__mercado__nombre',
        'seleccion__mercado__evento__nombre',
    ]
    ordering_fields = [
        'fecha_creacion',
        'odd_valor_tomado',
        'resultado',
    ]


class OperacionesApuestaViewSet(viewsets.ViewSet):
    """
    Operaciones principales de apuestas:
    - crear apuesta simple
    - crear apuesta combinada
    - liquidar ganada
    - liquidar perdida
    - anular apuesta
    """

    @action(detail=False, methods=['post'])
    def crear_simple(self, request):
        serializer = CrearApuestaSimpleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            usuario = User.objects.get(pk=serializer.validated_data['usuario_id'])
        except User.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            apuesta = crear_apuesta_simple(
                usuario=usuario,
                odd_id=serializer.validated_data['odd_id'],
                stake=serializer.validated_data['stake'],
                idempotency_key=serializer.validated_data.get('idempotency_key'),
                ip_origen=serializer.validated_data.get('ip_origen'),
            )
        except (ValueError, Exception) as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = BetSerializer(apuesta)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def crear_combinada(self, request):
        serializer = CrearApuestaCombinadaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            usuario = User.objects.get(pk=serializer.validated_data['usuario_id'])
        except User.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            apuesta = crear_apuesta_combinada(
                usuario=usuario,
                odd_ids=serializer.validated_data['odd_ids'],
                stake=serializer.validated_data['stake'],
                idempotency_key=serializer.validated_data.get('idempotency_key'),
                ip_origen=serializer.validated_data.get('ip_origen'),
            )
        except (ValueError, Exception) as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = BetSerializer(apuesta)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def liquidar_ganada(self, request):
        serializer = LiquidarApuestaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        apuesta, _movimiento = liquidar_apuesta_ganada(
            bet_id=serializer.validated_data['bet_id'],
            idempotency_key=serializer.validated_data.get('idempotency_key'),
            liquidado_por=request.user if request.user.is_authenticated else None,
        )

        response_serializer = BetSerializer(apuesta)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def liquidar_perdida(self, request):
        serializer = LiquidarApuestaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        apuesta, _movimiento = liquidar_apuesta_perdida(
            bet_id=serializer.validated_data['bet_id'],
            idempotency_key=serializer.validated_data.get('idempotency_key'),
            liquidado_por=request.user if request.user.is_authenticated else None,
        )

        response_serializer = BetSerializer(apuesta)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def anular(self, request):
        serializer = LiquidarApuestaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        apuesta, _movimiento = anular_apuesta(
            bet_id=serializer.validated_data['bet_id'],
            idempotency_key=serializer.validated_data.get('idempotency_key'),
            anulado_por=request.user if request.user.is_authenticated else None,
        )

        response_serializer = BetSerializer(apuesta)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def cashout(self, request):
        serializer = LiquidarApuestaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            apuesta, _movimiento = cashout_apuesta(
                bet_id=serializer.validated_data['bet_id'],
                idempotency_key=serializer.validated_data.get('idempotency_key'),
                solicitado_por=request.user if request.user.is_authenticated else None,
            )
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = BetSerializer(apuesta)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
