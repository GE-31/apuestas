import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Inicializar Django antes de importar channels/routing
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter          # noqa: E402
from channels.auth import AuthMiddlewareStack                        # noqa: E402
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler  # noqa: E402

application = ProtocolTypeRouter({
    # Archivos estáticos + HTTP normal (solo DEBUG=True)
    "http": ASGIStaticFilesHandler(django_asgi_app),
    # WebSocket: vacío por ahora, se poblará cuando se implementen consumers
    "websocket": AuthMiddlewareStack(
        URLRouter([])
    ),
})
