import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import routing after Django is initialized
from appschedule import routing
from project.middleware.tenant_asgi import TenantASGIMiddleware
from django.conf import settings

# Para desarrollo local, simplificar el stack de WebSocket
# En producción, usar TenantASGIMiddleware para multi-tenant
_routes = AllowedHostsOriginValidator(
    AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
)
if settings.DEBUG:
    websocket_stack = _routes
else:
    websocket_stack = TenantASGIMiddleware(_routes)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": websocket_stack,
})
