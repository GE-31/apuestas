from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class ApiRootView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        base_url = request.build_absolute_uri('/api/')
        return Response({
            'nombre': 'API Apuesta24/7',
            'estado': 'ok',
            'autenticacion': 'JWT o sesion Django. Los endpoints internos requieren usuario autenticado.',
            'documentacion': {
                'swagger': request.build_absolute_uri('/api/docs/'),
                'redoc': request.build_absolute_uri('/api/redoc/'),
                'schema': request.build_absolute_uri('/api/schema/'),
            },
            'modulos': {
                'usuarios': {
                    'url': f'{base_url}usuarios/',
                    'descripcion': 'Perfiles de usuario y verificacion KYC.',
                },
                'billetera': {
                    'url': f'{base_url}billetera/',
                    'descripcion': 'Cuentas, saldos, movimientos, recargas y retiros simulados.',
                },
                'apuestas': {
                    'url': f'{base_url}apuestas/',
                    'descripcion': 'Consulta, creacion, liquidacion, anulacion y cashout de apuestas.',
                },
            },
        })
