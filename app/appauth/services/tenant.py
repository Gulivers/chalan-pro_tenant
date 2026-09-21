"""
Tenant resolution for authentication flows.

Reuses the robust resolver in utils.tenant_branding (connection.tenant,
get_tenant, Domain lookup fallback) so login/me/password-reset stay
aligned with PDF branding and TenantAccessEnforcementMiddleware.
"""
from utils.tenant_branding import _resolve_tenant


def resolve_request_tenant(request):
    """Return the non-public tenant for this request, or None."""
    return _resolve_tenant(request)


def tenant_branding_payload(tenant) -> dict:
    """Public branding fields derived from the active tenant."""
    if tenant is None:
        return {
            'tenant_name': None,
            'tenant_logo_url': None,
            'client_type': None,
            'schema_name': None,
        }

    logo_url = None
    get_logo = getattr(tenant, 'get_logo_url', None)
    if callable(get_logo):
        logo_url = get_logo()

    return {
        'tenant_name': tenant.name,
        'tenant_logo_url': logo_url,
        'client_type': getattr(tenant, 'client_type', None) or 'general',
        'schema_name': getattr(tenant, 'schema_name', None),
    }


def is_tenant_owner(user, tenant) -> bool:
    if not getattr(user, 'is_authenticated', False):
        return False
    if tenant is None:
        return False
    return bool(
        user.is_staff
        and user.email
        and getattr(tenant, 'email', None)
        and user.email == tenant.email
    )
