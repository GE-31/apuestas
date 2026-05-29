from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

LIVE_GROUP = 'eventos_live'
 

def broadcast_evento_update(
    evento_id,
    estado,
    marcador_local=None,
    marcador_visitante=None,
    live_started_at=None,
    live_period=None,
    cuotas_vivo=None,
):
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            LIVE_GROUP,
            {
                'type': 'evento_update',
                'evento_id': evento_id,
                'estado': estado,
                'marcador_local': marcador_local,
                'marcador_visitante': marcador_visitante,
                'live_started_at': live_started_at,
                'live_period': live_period,
                'cuotas_vivo': cuotas_vivo or {},
            },
        )
    except Exception:
        pass
