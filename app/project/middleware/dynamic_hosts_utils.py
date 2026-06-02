"""
Utilidad compartida para actualizar ALLOWED_HOSTS y CSRF_TRUSTED_ORIGINS
desde los dominios de tenants en la base de datos.

Usado por DynamicAllowedHostsMiddleware, DynamicCSRFMiddleware y por el
onboarding al crear un tenant, para que el nuevo subdominio sea accesible de inmediato.
"""
import logging
import time

logger = logging.getLogger(__name__)

# Tiempo de la última actualización (compartido por ambos middlewares).
# Si es None o hace más de _domain_cache_ttl segundos, los middlewares vuelven a consultar.
_last_domain_refresh = None
_domain_cache_ttl = 300  # 5 minutos


def refresh_dynamic_domains():
    """
    Actualiza ALLOWED_HOSTS y CSRF_TRUSTED_ORIGINS con todos los dominios
    activos de tenants desde la base de datos.
    Puede llamarse desde los middlewares (cada TTL) o desde el onboarding (inmediato).
    """
    global _last_domain_refresh
    from django.conf import settings
    from tenants.models import Domain

    try:
        # Todos los dominios registrados deben poder resolver el tenant (ALLOWED_HOSTS).
        # El bloqueo por tenant inactivo o billing va en TenantAccessEnforcementMiddleware.
        active_domains = Domain.objects.values_list('domain', flat=True).distinct()

        # 1. ALLOWED_HOSTS
        domains_added = 0
        for domain in active_domains:
            if domain and domain not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append(domain)
                domains_added += 1
                logger.debug("Agregado dominio a ALLOWED_HOSTS: %s", domain)

        if domains_added > 0:
            logger.info("Actualizados %s dominios en ALLOWED_HOSTS dinámicamente", domains_added)

        # 2. CSRF_TRUSTED_ORIGINS
        origins_added = 0
        for domain in active_domains:
            origins_to_add = []
            if getattr(settings, 'DEBUG', False):
                for port in ('8000', '3000', '8080'):
                    origins_to_add.append(f"http://{domain}:{port}")
                origins_to_add.append(f"https://{domain}")
            else:
                origins_to_add.append(f"https://{domain}")

            for origin in origins_to_add:
                if origin not in settings.CSRF_TRUSTED_ORIGINS:
                    settings.CSRF_TRUSTED_ORIGINS.append(origin)
                    origins_added += 1
                    logger.debug("Agregado origen a CSRF_TRUSTED_ORIGINS: %s", origin)

        if origins_added > 0:
            logger.info(
                "Actualizados %s orígenes CSRF dinámicamente (%s)",
                origins_added,
                "desarrollo" if getattr(settings, 'DEBUG', False) else "producción",
            )

        _last_domain_refresh = time.time()
        return domains_added, origins_added

    except Exception as e:
        logger.debug("Error al actualizar dominios dinámicamente: %s", e)
        return 0, 0


def should_refresh_domains():
    """Indica si conviene volver a ejecutar refresh (por TTL)."""
    if _last_domain_refresh is None:
        return True
    return (time.time() - _last_domain_refresh) > _domain_cache_ttl


def is_host_explicitly_in_allowed(hostname):
    """
    Comprueba si el hostname está como entrada explícita en ALLOWED_HOSTS.
    Si solo está permitido por un patrón tipo .chalanpro.net, devuelve False,
    para poder forzar refresh y que el nuevo dominio quede en lista y en memoria.
    """
    from django.conf import settings
    if not hostname:
        return True
    return hostname in settings.ALLOWED_HOSTS
