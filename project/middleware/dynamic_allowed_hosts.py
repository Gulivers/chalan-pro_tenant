"""
Middleware para actualizar dinámicamente ALLOWED_HOSTS
basado en los dominios de tenants en la base de datos.
"""
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class DynamicAllowedHostsMiddleware(MiddlewareMixin):
    """
    Middleware que actualiza ALLOWED_HOSTS dinámicamente
    basado en los dominios de tenants activos en la base de datos.
    
    Esto permite que nuevos tenants creados después del inicio del servidor
    sean automáticamente incluidos en ALLOWED_HOSTS sin necesidad de reiniciar.
    
    IMPORTANTE: Este middleware DEBE ejecutarse ANTES de SecurityMiddleware
    para que los dominios estén disponibles antes de la validación de ALLOWED_HOSTS.
    """
    
    # Cache para evitar consultas excesivas a la BD
    _last_domain_check = None
    _domain_cache_ttl = 300  # 5 minutos
    
    def process_request(self, request):
        """
        Actualiza ALLOWED_HOSTS si es necesario.
        Solo verifica cada 5 minutos para evitar sobrecarga.
        """
        # Verificar si necesitamos actualizar el cache
        import time
        current_time = time.time()
        
        if (self._last_domain_check is None or 
            current_time - self._last_domain_check > self._domain_cache_ttl):
            
            try:
                # Importar desde tenants.models (schema público) donde están los dominios
                from tenants.models import Domain
                
                # Obtener todos los dominios activos de tenants (desde schema público)
                active_domains = Domain.objects.filter(
                    tenant__is_active=True
                ).values_list('domain', flat=True).distinct()
                
                # Agregar dominios que no estén ya en ALLOWED_HOSTS
                domains_added = 0
                for domain in active_domains:
                    if domain and domain not in settings.ALLOWED_HOSTS:
                        settings.ALLOWED_HOSTS.append(domain)
                        domains_added += 1
                        logger.debug(f"Agregado dominio a ALLOWED_HOSTS: {domain}")
                
                if domains_added > 0:
                    logger.info(f"Actualizados {domains_added} dominios en ALLOWED_HOSTS dinámicamente")
                
                self._last_domain_check = current_time
                
            except Exception as e:
                # Silenciar errores para no afectar el funcionamiento normal
                # Solo loguear en modo debug para no llenar los logs
                logger.debug(f"Error al actualizar ALLOWED_HOSTS dinámicamente: {e}")
        
        return None

