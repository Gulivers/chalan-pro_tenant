"""
Middleware para actualizar dinámicamente ALLOWED_HOSTS
basado en los dominios de tenants en la base de datos.
"""
from django.utils.deprecation import MiddlewareMixin

from .dynamic_hosts_utils import (
    refresh_dynamic_domains,
    should_refresh_domains,
    is_host_explicitly_in_allowed,
)


class DynamicAllowedHostsMiddleware(MiddlewareMixin):
    """
    Middleware que actualiza ALLOWED_HOSTS dinámicamente
    basado en los dominios de tenants activos en la base de datos.

    Esto permite que nuevos tenants creados después del inicio del servidor
    sean automáticamente incluidos en ALLOWED_HOSTS sin necesidad de reiniciar.
    La actualización también se dispara desde el onboarding al crear un tenant.

    Si el host de la petición no está de forma explícita en ALLOWED_HOSTS (p. ej.
    solo permitido por .chalanpro.net), se fuerza refresh para cargar dominios
    desde la BD y que el tenant se resuelva en este proceso.
    """

    def process_request(self, request):
        hostname = (request.META.get("HTTP_HOST") or "").strip()
        if ":" in hostname:
            hostname = hostname.split(":")[0]
        # Forzar refresh si el host no está explícito (así cualquier worker carga el nuevo tenant)
        if hostname and not is_host_explicitly_in_allowed(hostname):
            refresh_dynamic_domains()
        elif should_refresh_domains():
            refresh_dynamic_domains()
        return None

