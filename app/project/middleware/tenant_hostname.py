"""
Middleware personalizado para normalizar el hostname antes de que django-tenants lo procese.
Remueve el puerto del hostname en desarrollo local para que django-tenants pueda encontrar el tenant correctamente.
"""
import re
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import DisallowedHost


class TenantHostnameNormalizerMiddleware(MiddlewareMixin):
    """
    Normaliza el hostname removiendo el puerto antes de que django-tenants lo procese.
    
    En desarrollo local, cuando accedes a http://globo_dyned2.chalan-pro.net:8000/admin/,
    Django recibe el hostname como 'globo_dyned2.chalan-pro.net:8000', pero el dominio
    en la base de datos es solo 'globo_dyned2.chalan-pro.net' (sin puerto).
    
    Este middleware remueve el puerto del hostname para que django-tenants pueda
    encontrar el tenant correctamente.
    """
    
    def process_request(self, request):
        """
        Normaliza el hostname removiendo el puerto si existe.
        
        IMPORTANTE: Obtenemos el hostname directamente de HTTP_HOST sin usar get_host()
        porque get_host() valida contra ALLOWED_HOSTS antes de que podamos normalizar.
        
        Este middleware DEBE ejecutarse ANTES de SecurityMiddleware para que la normalización
        ocurra antes de la validación de ALLOWED_HOSTS.
        """
        # Obtener el hostname original directamente de HTTP_HOST (sin validación)
        hostname_with_port = request.META.get('HTTP_HOST', '')
        
        if not hostname_with_port:
            # Si no hay HTTP_HOST, intentar obtenerlo de otros headers
            hostname_with_port = (
                request.META.get('SERVER_NAME', '') or 
                request.META.get('HTTP_X_FORWARDED_HOST', '').split(',')[0].strip() or
                ''
            )
        
        # Normalizar el hostname: remover puerto y manejar guiones bajos
        if hostname_with_port:
            # Remover el puerto si existe (formato: hostname:port)
            # Ejemplo: 'globo_dyned2.chalan-pro.net:8000' -> 'globo_dyned2.chalan-pro.net'
            if ':' in hostname_with_port:
                hostname_without_port = hostname_with_port.split(':')[0]
            else:
                hostname_without_port = hostname_with_port
            
            # Actualizar el hostname en la petición ANTES de que Django lo valide
            # Esto afecta cómo django-tenants detecta el tenant y cómo Django valida ALLOWED_HOSTS
            request.META['HTTP_HOST'] = hostname_without_port
            
            # También actualizar SERVER_NAME si existe
            if 'SERVER_NAME' in request.META:
                request.META['SERVER_NAME'] = hostname_without_port
            
            # Limpiar cualquier caché de hostname que Django pueda tener
            if hasattr(request, '_cached_host'):
                delattr(request, '_cached_host')
            
            # Limpiar también _cached_remote_addr si existe
            if hasattr(request, '_cached_remote_addr'):
                delattr(request, '_cached_remote_addr')
        
        return None

