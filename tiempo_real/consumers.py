import json
from channels.generic.websocket import AsyncWebsocketConsumer

LIVE_GROUP = 'eventos_live'


class SaldoConsumer(AsyncWebsocketConsumer):
    """
    WebSocket por usuario: notificaciones de saldo (user_<id>)
    y actualizaciones de eventos en vivo (eventos_live, broadcast global).
    """

    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close()
            return

        self.group_name = f'user_{user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.channel_layer.group_add(LIVE_GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard(LIVE_GROUP, self.channel_name)

    async def balance_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'balance_update',
            'saldo': event['saldo'],
            'mensaje': event.get('mensaje', ''),
        }))

    async def evento_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'evento_update',
            'evento_id': event['evento_id'],
            'estado': event['estado'],
            'marcador_local': event.get('marcador_local'),
            'marcador_visitante': event.get('marcador_visitante'),
        }))
