"""
URLs para el módulo de tenants y onboarding
"""
from django.urls import path
from . import views

urlpatterns = [
    path('api/', views.api_root, name='api-root'),
    path('api/landing/contact/', views.landing_contact, name='landing-contact'),
    path('api/onboarding/config/', views.onboarding_public_config, name='onboarding-config'),
    path('api/onboarding/verify/', views.verify_onboarding_email, name='onboarding-verify'),
    path('api/onboarding/', views.create_tenant_onboarding, name='onboarding'),
    path('api/onboarding/create-tenant/', views.create_tenant_onboarding, name='create-tenant-onboarding'),
]

