from rest_framework import serializers

from apuestas_core.models import Bet, BetSelection


class BetSelectionSerializer(serializers.ModelSerializer):
    seleccion_nombre = serializers.CharField(
        source='seleccion.nombre',
        read_only=True
    )

    mercado_nombre = serializers.CharField(
        source='seleccion.mercado.nombre',
        read_only=True
    )

    evento_nombre = serializers.CharField(
        source='seleccion.mercado.evento.nombre',
        read_only=True
    )

    class Meta:
        model = BetSelection
        fields = [
            'id',
            'bet',
            'seleccion',
            'seleccion_nombre',
            'mercado_nombre',
            'evento_nombre',
            'odd',
            'odd_valor_tomado',
            'resultado',
            'fecha_creacion',
        ]
        read_only_fields = [
            'fecha_creacion',
        ]


class BetSerializer(serializers.ModelSerializer):
    selecciones = BetSelectionSerializer(many=True, read_only=True)

    class Meta:
        model = Bet
        fields = [
            'id',
            'usuario',
            'tipo',
            'estado',
            'stake',
            'odds_total',
            'payout_potencial',
            'payout_final',
            'idempotency_key',
            'ip_origen',
            'aceptada_en',
            'liquidada_en',
            'fecha_creacion',
            'fecha_actualizacion',
            'selecciones',
        ]
        read_only_fields = [
            'tipo',
            'estado',
            'odds_total',
            'payout_potencial',
            'payout_final',
            'aceptada_en',
            'liquidada_en',
            'fecha_creacion',
            'fecha_actualizacion',
            'selecciones',
        ]


class CrearApuestaSimpleSerializer(serializers.Serializer):
    usuario_id = serializers.IntegerField()
    odd_id = serializers.IntegerField()
    stake = serializers.DecimalField(max_digits=18, decimal_places=4)
    idempotency_key = serializers.CharField(required=False, allow_blank=True)
    ip_origen = serializers.IPAddressField(required=False, allow_null=True)


class CrearApuestaCombinadaSerializer(serializers.Serializer):
    usuario_id = serializers.IntegerField()
    odd_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=2,
        allow_empty=False,
    )
    stake = serializers.DecimalField(max_digits=18, decimal_places=4)
    idempotency_key = serializers.CharField(required=False, allow_blank=True)
    ip_origen = serializers.IPAddressField(required=False, allow_null=True)


class LiquidarApuestaSerializer(serializers.Serializer):
    bet_id = serializers.IntegerField()
    idempotency_key = serializers.CharField(required=False, allow_blank=True)
