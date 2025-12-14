"""
Middleware para actualizar dinámicamente CSRF_TRUSTED_ORIGINS
basado en los dominios de tenants en la base de datos.
"""
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class DynamicCSRFMiddleware(MiddlewareMixin):
    """
    Middleware que actualiza CSRF_TRUSTED_ORIGINS dinámicamente
    basado en los dominios de tenants activos en la base de datos.
    
    Esto permite que nuevos tenants creados después del inicio del servidor
    sean automáticamente incluidos en CSRF_TRUSTED_ORIGINS sin necesidad de reiniciar.
    
    IMPORTANTE: Este middleware DEBE ejecutarse ANTES de CsrfViewMiddleware
    para que los orígenes estén disponibles antes de la validación de CSRF.
    """
    
    # Cache para evitar consultas excesivas a la BD
    _last_domain_check = None
    _domain_cache_ttl = 300  # 5 minutos
    
    def process_request(self, request):
        """
        Actualiza CSRF_TRUSTED_ORIGINS si es necesario.
        Solo verifica cada 5 minutos para evitar sobrecarga.
        Funciona tanto en desarrollo como en producción.
        """
        # Verificar si necesitamos actualizar el cache
        import time
        current_time = time.time()
        
        if (self._last_domain_check is None or 
            current_time - self._last_domain_check > self._domain_cache_ttl):
            
            try:
                # Importar desde tenants.models (schema público) donde están los dominios
                from tenants.models import Domain
                
                # Obtener todos los dominios activos
                active_domains = Domain.objects.filter(
                    tenant__is_active=True
                ).values_list('domain', flat=True).distinct()
                
                # Determinar qué orígenes agregar según el entorno
                origins_added = 0
                for domain in active_domains:
                    origins_to_add = []
                    
                    if settings.DEBUG:
                        # En desarrollo: agregar variantes HTTP con puertos comunes
                        common_ports = ['8000', '3000', '8080']
                        for port in common_ports:
                            origins_to_add.append(f'http://{domain}:{port}')
                        # También HTTPS
                        origins_to_add.append(f'https://{domain}')
                    else:
                        # En producción: solo HTTPS (sin puerto)
                        origins_to_add.append(f'https://{domain}')
                    
                    # Agregar si no está presente
                    for origin in origins_to_add:
                        if origin not in settings.CSRF_TRUSTED_ORIGINS:
                            settings.CSRF_TRUSTED_ORIGINS.append(origin)
                            origins_added += 1
                            logger.debug(f"Agregado origen a CSRF_TRUSTED_ORIGINS: {origin}")
                
                if origins_added > 0:
                    logger.info(f"Actualizados {origins_added} orígenes CSRF dinámicamente ({'desarrollo' if settings.DEBUG else 'producción'})")
                
                self._last_domain_check = current_time
                
            except Exception as e:
                # Silenciar errores para no afectar el funcionamiento normal
                logger.debug(f"Error al actualizar CSRF dinámicamente: {e}")
        
        return None

