"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.conf import settings
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', include('ctrctsapp.urls')),
    path('', include('auditapp.urls')),  # rutas de auditapp
    path('', include('crewsapp.urls')), 
    path('', include('appschedule.urls')),
    path('', include('appinventory.urls')),
    path('', include('apptransactions.urls')),
]

# Configurar archivos media (imágenes y PDFs) para desarrollo y producción
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

# Asegurar que el directorio media existe
import os
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # En producción (Render), servir archivos media usando django.views.static.serve
    # Nota: Esto funciona pero no es ideal para alta carga. Para producción a gran escala,
    # considera usar un servicio de almacenamiento en la nube como AWS S3
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]