from django.apps import AppConfig
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def load_domains_to_csrf_trusted_origins():
    """
    Carga dinámicamente los dominios de la tabla tenants_domain
    y los agrega a CSRF_TRUSTED_ORIGINS.
    
    Funciona tanto en desarrollo (localhost con puertos) como en producción (HTTPS).
    """
    try:
        from tenants.models import Domain
        
        # Obtener todos los dominios activos desde la BD
        active_domains = Domain.objects.filter(tenant__is_active=True).values_list('domain', flat=True)
        
        # Determinar qué orígenes agregar según el entorno
        if settings.DEBUG:
            # En desarrollo: agregar variantes HTTP con puertos comunes
            common_ports = ['8000', '3000', '8080']
            for domain in active_domains:
                origins_to_add = []
                # Variantes HTTP con puertos (desarrollo)
                for port in common_ports:
                    origins_to_add.append(f'http://{domain}:{port}')
                # También HTTPS para desarrollo con puerto
                origins_to_add.append(f'https://{domain}')
                
                # Agregar a CSRF_TRUSTED_ORIGINS si no está ya presente
                for origin in origins_to_add:
                    if origin not in settings.CSRF_TRUSTED_ORIGINS:
                        settings.CSRF_TRUSTED_ORIGINS.append(origin)
                        logger.info(f"✓ Agregado dominio a CSRF_TRUSTED_ORIGINS: {origin}")
        else:
            # En producción: solo HTTPS (sin puerto)
            for domain in active_domains:
                origin = f'https://{domain}'
                if origin not in settings.CSRF_TRUSTED_ORIGINS:
                    settings.CSRF_TRUSTED_ORIGINS.append(origin)
                    logger.info(f"✓ Agregado dominio a CSRF_TRUSTED_ORIGINS: {origin}")
        
        logger.info(f"✓ Cargados {len(active_domains)} dominios dinámicamente para CSRF ({'desarrollo' if settings.DEBUG else 'producción'})")
        
    except Exception as e:
        # Si hay error (por ejemplo, durante migraciones o primera carga)
        logger.warning(f"No se pudieron cargar dominios dinámicamente para CSRF: {e}")


class TenantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tenants'
    
    def ready(self):
        """
        Se ejecuta cuando Django ha cargado todas las apps.
        Aquí podemos acceder a los modelos y la base de datos de forma segura.
        """
        # Solo cargar dominios si no estamos ejecutando migraciones
        import sys
        if 'migrate' not in sys.argv and 'makemigrations' not in sys.argv:
            load_domains_to_csrf_trusted_origins()
