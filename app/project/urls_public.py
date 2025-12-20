"""
URLs para el schema 'public' (admin global de tenants)
Este archivo se usa cuando se accede al dominio público o al admin global
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os

# Vista raíz del API
@api_view(['GET'])
def api_root(request):
    """
    Vista raíz del API REST que muestra los endpoints disponibles.
    """
    return Response({
        'message': 'Chalan-Pro API',
        'version': '1.0',
        'endpoints': {
            'contracts': '/api/contract/',
            'builders': '/api/builder/',
            'jobs': '/api/job/',
            'house_models': '/api/house_model/',
            'workprices': '/api/workprice/',
            'crews': '/api/crews/',
            'trucks': '/api/trucks/',
            'schedule': '/api/schedule/',
            'events': '/api/event/',
            'products': '/api/products/',
            'warehouses': '/api/warehouses/',
            'parties': '/api/parties/',
            'documents': '/api/documents/',
            'admin': '/admin/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('api/', api_root, name='api-root'),  # Vista raíz del API
    # Incluir URLs de las apps (ya tienen el prefijo api/ en sus rutas)
    path('', include('ctrctsapp.urls')),
    path('', include('auditapp.urls')),
    path('', include('crewsapp.urls')),
    path('', include('appschedule.urls')),
    path('', include('appinventory.urls')),
    path('', include('apptransactions.urls')),
    path('', include('tenants.urls')),  # Incluir URLs de onboarding
]

# Configurar archivos media (imágenes y PDFs) para desarrollo y producción
# Asegurar que el directorio media existe
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # En producción, servir archivos media usando django.views.static.serve
    # Nota: Esto funciona pero no es ideal para alta carga. Para producción a gran escala,
    # considera usar un servicio de almacenamiento en la nube como AWS S3
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

