from django.urls import path

from appbilling import views

urlpatterns = [
    path('api/billing/status/', views.billing_status, name='billing-status'),
    path('api/billing/public-plans/', views.billing_public_plans, name='billing-public-plans'),
    path('api/billing/plans/', views.billing_plans, name='billing-plans'),
    path(
        'api/billing/create-checkout-session/',
        views.create_checkout,
        name='billing-create-checkout',
    ),
    path(
        'api/billing/create-customer-portal-session/',
        views.create_portal,
        name='billing-create-portal',
    ),
    path('stripe/webhook/', views.stripe_webhook, name='stripe-webhook'),
]
