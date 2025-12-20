"""
URLs para el módulo de tenants y onboarding
"""
from django.urls import path
from . import views

urlpatterns = [
    path('api/', views.api_root, name='api-root'),
    path('api/onboarding/', views.create_tenant_onboarding, name='onboarding'),
    path('api/onboarding/create-tenant/', views.create_tenant_onboarding, name='create-tenant-onboarding'),  # Mantener compatibilidad
]

