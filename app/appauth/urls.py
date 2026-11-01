from django.urls import include, path
from rest_framework.routers import DefaultRouter

from appauth.views import (
    LoginView,
    MeView,
    WsTicketView,
    PasswordForgotView,
    PasswordResetView,
    TenantContextView,
    logout_view,
    permissions_view,
    refresh_view,
    validate_token_view,
)
from appauth.views.user_admin import (
    GroupAdminViewSet,
    PermissionCatalogViewSet,
    UserAdminViewSet,
)

admin_router = DefaultRouter()
admin_router.register(
    r'permissions',
    PermissionCatalogViewSet,
    basename='auth-admin-permissions',
)
admin_router.register(r'groups', GroupAdminViewSet, basename='auth-admin-groups')
admin_router.register(r'users', UserAdminViewSet, basename='auth-admin-users')

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
    path('api/auth/ws-ticket/', WsTicketView.as_view(), name='auth_ws_ticket'),
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
    path('api/auth/admin/', include(admin_router.urls)),
]
