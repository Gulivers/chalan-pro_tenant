"""
URLs para el schema 'public' (admin global de tenants)
Este archivo se usa cuando se accede al dominio público o al admin global
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
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

