from rest_framework import serializers

from billetera.models import Account, LedgerEntry, LedgerTransaction
from billetera.services.saldo_service import obtener_saldo_disponible


class AccountSerializer(serializers.ModelSerializer):
    saldo = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            'id',
            'usuario',
            'tipo',
            'nombre',
            'activa',
            'saldo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'saldo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]

    def get_saldo(self, obj):
        return obtener_saldo_disponible(obj)


class LedgerEntrySerializer(serializers.ModelSerializer):
    account_nombre = serializers.CharField(
        source='account.nombre',
        read_only=True
    )

    transaction_tipo = serializers.CharField(
        source='transaction.tipo',
        read_only=True
    )

    class Meta:
        model = LedgerEntry
        fields = [
            'id',
            'transaction',
            'transaction_tipo',
            'account',
            'account_nombre',
            'amount',
            'direction',
            'descripcion',
            'fecha_creacion',
        ]
        read_only_fields = [
            'fecha_creacion',
        ]


class LedgerTransactionSerializer(serializers.ModelSerializer):
    entries = LedgerEntrySerializer(many=True, read_only=True)

    class Meta:
        model = LedgerTransaction
        fields = [
            'id',
            'tipo',
            'referencia',
            'idempotency_key',
            'descripcion',
            'creado_por',
            'fecha_creacion',
            'entries',
        ]
        read_only_fields = [
            'fecha_creacion',
            'entries',
        ]


class MovimientoSimpleSerializer(serializers.Serializer):
    cuenta_debito = serializers.IntegerField()
    cuenta_credito = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=4)
    tipo = serializers.CharField(required=False)
    referencia = serializers.CharField(required=False, allow_blank=True)
    idempotency_key = serializers.CharField(required=False, allow_blank=True)
    descripcion = serializers.CharField(required=False, allow_blank=True)


class RecargaFichasSerializer(serializers.Serializer):
    usuario_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=4)
    idempotency_key = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor que cero.")
        return value


class RetiroFichasSerializer(serializers.Serializer):
    usuario_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=4)
    idempotency_key = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor que cero.")
        return value
