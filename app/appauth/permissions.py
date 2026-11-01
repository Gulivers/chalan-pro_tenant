from rest_framework.permissions import BasePermission

from appauth.services.tenant import is_tenant_owner, resolve_request_tenant


class IsTenantStaff(BasePermission):
    """
    Tenant admins and staff may manage users/groups/permissions in the SPA.

    Superuser is never granted via these APIs; Django Admin remains the
    only place for platform-level superuser work.
    """

    message = 'Staff access is required to manage users and permissions.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated or not user.is_active:
            return False
        if user.is_staff:
            return True
        tenant = resolve_request_tenant(request)
        return is_tenant_owner(user, tenant)
