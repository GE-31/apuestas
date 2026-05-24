from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from usuarios.models import PerfilUsuario, VerificacionKYC
from usuarios.serializers import PerfilUsuarioSerializer, VerificacionKYCSerializer
from usuarios.services.kyc_service import verificar_kyc


class PerfilUsuarioViewSet(viewsets.ModelViewSet):
    queryset = PerfilUsuario.objects.select_related('usuario').all()
    serializer_class = PerfilUsuarioSerializer
    search_fields = ['dni', 'nombres', 'apellidos', 'usuario__username']
    ordering_fields = ['fecha_registro', 'apellidos', 'nombres']

    @action(detail=True, methods=['post'])
    def verificar_kyc(self, request, pk=None):
        perfil = self.get_object()
        kyc = verificar_kyc(
            perfil=perfil,
            usuario_admin=request.user,
            observacion=request.data.get('observacion', '')
        )
        serializer = VerificacionKYCSerializer(kyc)
        return Response(serializer.data)


class VerificacionKYCViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VerificacionKYC.objects.select_related('perfil', 'verificado_por').all()
    serializer_class = VerificacionKYCSerializer
    search_fields = ['perfil__dni', 'perfil__nombres', 'perfil__apellidos']
    ordering_fields = ['fecha_creacion', 'fecha_verificacion']