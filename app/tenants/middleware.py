"""Enforce tenant workspace access on API routes and tenant Django admin."""

from __future__ import annotations

from urllib.parse import urlsplit

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django_tenants.utils import get_public_schema_name

from tenants.services.access import get_tenant_access
from utils.tenant_branding import _resolve_tenant


def _spa_url(request, path: str) -> str:
    """Build an absolute SPA URL on the *current tenant host*.

    The Django admin is served by the backend (e.g. :8000 in dev), while SPA
    routes (/login, /billing) live on the frontend (e.g. :8080 in dev, same host
    via Nginx in prod). A relative link would resolve against the backend and
    404, and FRONT_URL points to the global/legacy domain (wrong host for a
    tenant). So we keep the tenant hostname from the request and borrow only the
    scheme/port from FRONT_URL.
    """
    raw_host = request.META.get('HTTP_HOST') or request.META.get('SERVER_NAME') or ''
    host = raw_host.split(':')[0]
    front = urlsplit(getattr(settings, 'FRONT_URL', '') or '')
    scheme = front.scheme or request.scheme
    port = f':{front.port}' if front.port else ''
    return f'{scheme}://{host}{port}{path}'

# API paths always allowed (prefix match on request.path)
TENANT_ACCESS_API_EXEMPT_PREFIXES = (
    '/api/billing/',
    '/api/validate-token/',
    '/api/login/',
    '/api/logout/',
    '/api/user_detail/',
    '/api/user-permissions/',
    '/api/request-password-reset/',
    '/api/password-reset-confirm/',
    '/stripe/webhook/',
    '/media/',
    '/static/',
)


def _is_public_schema_request(request) -> bool:
    from django.db import connection
    public = get_public_schema_name()
    if getattr(connection, 'schema_name', None) == public:
        return True
    tenant = getattr(request, 'tenant', None)
    if tenant is not None and getattr(tenant, 'schema_name', None) == public:
        return True
    return False


def _admin_denied_html(access, request) -> str:
    if access.reason == 'tenant_inactive':
        title = 'Workspace deactivated'
        detail = (
            'This JobRhythm workspace has been deactivated by the platform operator. '
            'Contact support if you believe this is an error.'
        )
        cta_label = 'Back to sign in'
        cta_href = _spa_url(request, '/login')
    else:
        title = 'Subscription required'
        detail = (
            'Your trial has ended or payment needs attention. '
            'Update billing in the app to restore access, including the Administrative Panel.'
        )
        cta_label = 'Open billing'
        cta_href = _spa_url(request, '/billing')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} – JobRhythm</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0;
           display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }}
    .card {{ max-width: 28rem; padding: 2rem; border-radius: 1rem;
             background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); }}
    h1 {{ font-size: 1.35rem; margin: 0 0 1rem; color: #f8fafc; }}
    p {{ line-height: 1.5; color: #94a3b8; margin: 0 0 1.5rem; }}
    a {{ display: inline-block; padding: 0.65rem 1.25rem; border-radius: 0.5rem;
         background: linear-gradient(90deg, #6366f1, #22d3ee); color: #0f172a;
         font-weight: 600; text-decoration: none; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{title}</h1>
    <p>{detail}</p>
    <a href="{cta_href}">{cta_label}</a>
  </div>
</body>
</html>"""


class TenantAccessEnforcementMiddleware(MiddlewareMixin):
    """
    Tenant schema only:
    - /api/* → 403 tenant_inactive or 402 subscription_required
    - /admin/* → HTML 403 (blocks login and all admin when access denied)
    Public schema (api.jobrhythm.net admin) is never affected.
    """

    def process_request(self, request):
        if not getattr(settings, 'BILLING_ENFORCEMENT_ENABLED', True):
            return None

        if _is_public_schema_request(request):
            return None

        path = getattr(request, 'path', '') or ''

        tenant = _resolve_tenant(request)
        if tenant is None:
            return None

        access = get_tenant_access(tenant)
        if access.allowed:
            return None

        if path.startswith('/admin/'):
            return HttpResponse(
                _admin_denied_html(access, request),
                status=403,
                content_type='text/html; charset=utf-8',
            )

        if not path.startswith('/api/'):
            return None

        for prefix in TENANT_ACCESS_API_EXEMPT_PREFIXES:
            if path.startswith(prefix):
                return None

        if access.reason == 'tenant_inactive':
            return JsonResponse(
                {
                    'detail': 'This workspace has been deactivated.',
                    'code': 'tenant_inactive',
                    'access_reason': access.reason,
                    'redirect': access.redirect_path,
                },
                status=403,
            )

        return JsonResponse(
            {
                'detail': 'Subscription required.',
                'code': 'subscription_required',
                'billing_reason': access.reason,
                'access_reason': access.reason,
                'suggested_plan_slug': (
                    access.billing.suggested_plan_slug if access.billing else None
                ),
                'redirect': access.redirect_path,
            },
            status=402,
        )
