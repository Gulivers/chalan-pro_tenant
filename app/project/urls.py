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

from tenants.views_setup import TenantSetupView

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', include('appauth.urls')),
    path('', include('appcore.urls')),
    path('', include('ctrctsapp.urls')),
    path('', include('auditapp.urls')),  # rutas de auditapp
    path('', include('crewsapp.urls')), 
    path('', include('appschedule.urls')),
    path('', include('appinventory.urls')),
    path('', include('apptransactions.urls')),
    path('', include('appassistant.urls')),
    path('', include('appbilling.urls')),
    path('api/tenant-setup/', TenantSetupView.as_view(), name='tenant-setup'),
]

# Media: solo URLs firmadas (sin listado público de MEDIA_ROOT).
import os
from django.http import Http404
from django.urls import re_path
from django.views.decorators.http import require_GET

from project.media_access import serve_signed_media

os.makedirs(settings.MEDIA_ROOT, exist_ok=True)


@require_GET
def _media_unauthenticated(request, path=''):
    raise Http404('Not found')


urlpatterns += [
    path('media/s/<str:token>/', serve_signed_media, name='signed-media'),
    re_path(r'^media/(?P<path>.*)$', _media_unauthenticated),
]