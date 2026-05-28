from django.urls import re_path
from tiempo_real.consumers import SaldoConsumer

websocket_urlpatterns = [
    re_path(r'^ws/saldo/$', SaldoConsumer.as_asgi()),
]
