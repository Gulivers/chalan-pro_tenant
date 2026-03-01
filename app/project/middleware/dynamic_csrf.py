"""
Middleware para actualizar dinámicamente CSRF_TRUSTED_ORIGINS
basado en los dominios de tenants en la base de datos.
"""
from django.utils.deprecation import MiddlewareMixin

from .dynamic_hosts_utils import refresh_dynamic_domains, should_refresh_domains


class DynamicCSRFMiddleware(MiddlewareMixin):
    """
    Middleware que actualiza CSRF_TRUSTED_ORIGINS dinámicamente
    basado en los dominios de tenants activos en la base de datos.

    Esto permite que nuevos tenants creados después del inicio del servidor
    sean automáticamente incluidos en CSRF_TRUSTED_ORIGINS sin necesidad de reiniciar.
    La actualización también se dispara desde el onboarding al crear un tenant.

    IMPORTANTE: Este middleware DEBE ejecutarse ANTES de CsrfViewMiddleware
    para que los orígenes estén disponibles antes de la validación de CSRF.
    """

    def process_request(self, request):
        """Actualiza CSRF (y ALLOWED_HOSTS) si hace falta; cada 5 min o tras crear tenant."""
        if should_refresh_domains():
            refresh_dynamic_domains()
        return None

