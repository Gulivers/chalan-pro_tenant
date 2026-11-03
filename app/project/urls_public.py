"""
URLs para el schema 'public' (admin global de tenants)
Este archivo se usa cuando se accede al dominio público o al admin global
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.http import Http404
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os

from project.media_access import serve_signed_media

# Vista raíz del API
@api_view(['GET'])
def api_root(request):
    """
    Vista raíz del API REST que muestra los endpoints disponibles.
    """
    return Response({
        'message': 'JobRhythm API',
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
    path('', include('appcore.urls')),
    path('', include('ctrctsapp.urls')),
    path('', include('auditapp.urls')),
    path('', include('crewsapp.urls')),
    path('', include('appschedule.urls')),
    path('', include('appinventory.urls')),
    path('', include('apptransactions.urls')),
    path('', include('tenants.urls')),  # Incluir URLs de onboarding
    path('', include('appbilling.urls')),
]

os.makedirs(settings.MEDIA_ROOT, exist_ok=True)


@require_GET
def _media_unauthenticated(request, path=''):
    raise Http404('Not found')


urlpatterns += [
    path('media/s/<str:token>/', serve_signed_media, name='signed-media-public'),
    re_path(r'^media/(?P<path>.*)$', _media_unauthenticated),
]

