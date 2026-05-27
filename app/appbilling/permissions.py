"""DRF permission for billing-gated endpoints."""

from rest_framework.permissions import BasePermission

from tenants.services.access import get_tenant_access
from utils.tenant_branding import _resolve_tenant


class BillingAccessPermission(BasePermission):
    message = 'An active trial or subscription is required.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        tenant = _resolve_tenant(request)
        if tenant is None:
            return True
        return get_tenant_access(tenant).allowed
