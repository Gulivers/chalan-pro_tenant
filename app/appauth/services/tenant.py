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


def _same_origin_media_url(logo_url: str | None) -> str | None:
    """Prefer relative /media/s/... for SPA <img> (same host + port).

    Absolute URLs from request.build_absolute_uri() often omit the Vite/dev
    port because the proxy strips it from Host, so the browser requests :80
    and the logo fails → JobRhythm fallback.
    """
    if not logo_url:
        return None
    if logo_url.startswith(('http://', 'https://')):
        from urllib.parse import urlparse

        parsed = urlparse(logo_url)
        return parsed.path or logo_url
    return logo_url


def tenant_branding_payload(tenant, request=None) -> dict:
    """Public branding fields derived from the active tenant."""
    if tenant is None:
        return {
            'tenant_name': None,
            'tenant_logo_url': None,
            'client_type': None,
            'schema_name': None,
            'schedule_show_crew_resources': True,
        }

    logo_url = None
    get_logo = getattr(tenant, 'get_logo_url', None)
    if callable(get_logo):
        try:
            # Relative path: SPA/Vite serve /media via same-origin proxy.
            logo_url = get_logo(request=None)
        except TypeError:
            logo_url = get_logo()
        logo_url = _same_origin_media_url(logo_url)

    return {
        'tenant_name': tenant.name,
        'tenant_logo_url': logo_url,
        'client_type': getattr(tenant, 'client_type', None) or 'general',
        'schema_name': getattr(tenant, 'schema_name', None),
        'schedule_show_crew_resources': bool(
            getattr(tenant, 'schedule_show_crew_resources', True)
        ),
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
