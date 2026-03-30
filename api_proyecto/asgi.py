import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from api_proyecto.middleware import JWTAuthMiddleware
from apps.tracking.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_proyecto.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
