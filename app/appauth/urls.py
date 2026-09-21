from django.urls import path

from appauth.views import (
    LoginView,
    MeView,
    PasswordForgotView,
    PasswordResetView,
    TenantContextView,
    logout_view,
    permissions_view,
    refresh_view,
    validate_token_view,
)

urlpatterns = [
    path('api/auth/login/', LoginView.as_view(), name='auth_login'),
    path('api/auth/logout/', logout_view, name='auth_logout'),
    path('api/auth/refresh/', refresh_view, name='auth_refresh'),
    path('api/auth/me/', MeView.as_view(), name='auth_me'),
    path(
        'api/auth/tenant-context/',
        TenantContextView.as_view(),
        name='auth_tenant_context',
    ),
    path('api/auth/permissions/', permissions_view, name='auth_permissions'),
    path('api/auth/validate/', validate_token_view, name='auth_validate'),
    path(
        'api/auth/password/forgot/',
        PasswordForgotView.as_view(),
        name='auth_password_forgot',
    ),
    path(
        'api/auth/password/reset/',
        PasswordResetView.as_view(),
        name='auth_password_reset',
    ),
]
