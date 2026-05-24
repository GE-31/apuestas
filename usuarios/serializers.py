from rest_framework import serializers

from usuarios.models import PerfilUsuario, VerificacionKYC


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = [
            'id',
            'usuario',
            'dni',
            'nombres',
            'apellidos',
            'fecha_nacimiento',
            'telefono',
            'direccion',
            'estado_cuenta',
            'fecha_registro',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'estado_cuenta',
            'fecha_registro',
            'fecha_actualizacion',
        ]


class VerificacionKYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificacionKYC
        fields = [
            'id',
            'perfil',
            'dni_verificado',
            'mayor_edad_verificado',
            'observacion',
            'verificado_por',
            'fecha_verificacion',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'dni_verificado',
            'mayor_edad_verificado',
            'verificado_por',
            'fecha_verificacion',
            'fecha_creacion',
            'fecha_actualizacion',
        ]