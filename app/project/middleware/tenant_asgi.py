"""
Middleware ASGI para identificar el tenant en conexiones WebSocket con django-tenants.
Este middleware debe ejecutarse antes de que se procese la conexión WebSocket.
"""
from django_tenants.utils import get_tenant_model, get_public_schema_name
from django.db import connection
from channels.db import database_sync_to_async
import logging

logger = logging.getLogger(__name__)


class TenantASGIMiddleware:
    """
    Middleware ASGI para identificar y configurar el tenant en conexiones WebSocket.
    
    Este middleware:
    1. Extrae el hostname del scope de la conexión WebSocket
    2. Normaliza el hostname (remueve puerto)
    3. Identifica el tenant usando django-tenants
    4. Configura el schema del tenant en la conexión de base de datos
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        # Log para debugging
        logger.info(f'🔍 ASGI scope type: {scope.get("type")}, path: {scope.get("path")}, headers: {dict(scope.get("headers", []))}')
        
        # Solo procesar conexiones WebSocket
        if scope['type'] == 'websocket':
            # Extraer hostname del scope
            hostname = self._get_hostname_from_scope(scope)
            logger.info(f'🔍 WebSocket connection - hostname: {hostname}, path: {scope.get("path")}')
            
            if hostname:
                # Normalizar hostname (remover puerto)
                normalized_hostname = self._normalize_hostname(hostname)
                
                # Identificar y configurar el tenant (usar database_sync_to_async para consultas DB)
                tenant = await self._get_tenant_from_hostname_async(normalized_hostname)
                
                if tenant:
                    # Configurar el schema del tenant en la conexión
                    await self._set_tenant_async(tenant)
                    logger.info(f'✅ Tenant configurado para WebSocket: {tenant.schema_name} (hostname: {normalized_hostname})')
                else:
                    # Si no se encuentra tenant, usar schema público
                    await self._set_schema_to_public_async()
                    logger.warning(f'⚠️ No se encontró tenant para hostname: {normalized_hostname}, usando schema público')
        else:
            # Log para peticiones HTTP que no son WebSocket
            logger.debug(f'🔍 HTTP request - path: {scope.get("path")}, method: {scope.get("method")}')
        
        # Continuar con el siguiente middleware/aplicación
        return await self.app(scope, receive, send)
    
    def _get_hostname_from_scope(self, scope):
        """
        Extrae el hostname del scope de ASGI.
        Busca en headers primero, luego en server.
        """
        # Buscar en headers (más común en producción con proxy)
        headers = dict(scope.get('headers', []))
        
        # Buscar Host header (bytes -> str)
        host_header = headers.get(b'host', b'')
        if host_header:
            return host_header.decode('utf-8')
        
        # Buscar X-Forwarded-Host header (si hay proxy)
        forwarded_host = headers.get(b'x-forwarded-host', b'')
        if forwarded_host:
            # Puede tener múltiples valores separados por coma
            return forwarded_host.decode('utf-8').split(',')[0].strip()
        
        # Si no hay headers, usar server info
        server = scope.get('server')
        if server:
            host, port = server
            if port and port not in [80, 443]:
                return f'{host}:{port}'
            return host
        
        return None
    
    def _normalize_hostname(self, hostname):
        """
        Normaliza el hostname removiendo el puerto si existe.
        Similar a TenantHostnameNormalizerMiddleware.
        """
        if not hostname:
            return None
        
        # Remover puerto si existe
        if ':' in hostname:
            return hostname.split(':')[0]
        
        return hostname
    
    def _get_tenant_from_hostname(self, hostname):
        """
        Identifica el tenant basándose en el hostname usando django-tenants.
        Versión síncrona para usar con database_sync_to_async.
        """
        if not hostname:
            return None
        
        try:
            # Buscar el dominio en la base de datos
            # django-tenants busca por dominio exacto o subdominio
            from django_tenants.utils import get_tenant_domain_model
            DomainModel = get_tenant_domain_model()
            
            # Buscar dominio exacto
            domain = DomainModel.objects.filter(domain=hostname).first()
            
            if domain:
                return domain.tenant
            
            # Si no se encuentra dominio exacto, intentar buscar por subdominio
            # Esto es útil si el hostname incluye el subdominio completo
            # Por ejemplo: 'globo_dyned2.chalan-pro.net' -> buscar 'globo_dyned2'
            parts = hostname.split('.')
            if len(parts) > 1:
                # Intentar con el primer subdominio
                subdomain = parts[0]
                domain = DomainModel.objects.filter(domain__icontains=subdomain).first()
                if domain:
                    return domain.tenant
            
            return None
            
        except Exception as e:
            logger.error(f'❌ Error al identificar tenant para hostname {hostname}: {e}')
            return None
    
    @database_sync_to_async
    def _get_tenant_from_hostname_async(self, hostname):
        """Wrapper asíncrono para _get_tenant_from_hostname"""
        return self._get_tenant_from_hostname(hostname)
    
    @database_sync_to_async
    def _set_tenant_async(self, tenant):
        """Configura el tenant de forma asíncrona"""
        connection.set_tenant(tenant)
    
    @database_sync_to_async
    def _set_schema_to_public_async(self):
        """Configura el schema público de forma asíncrona"""
        connection.set_schema_to_public()

