import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Inicializar Django antes de importar channels/routing
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter          # noqa: E402
from channels.auth import AuthMiddlewareStack                        # noqa: E402
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler  # noqa: E402
from tiempo_real.routing import websocket_urlpatterns               # noqa: E402

application = ProtocolTypeRouter({
    "http": ASGIStaticFilesHandler(django_asgi_app),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
