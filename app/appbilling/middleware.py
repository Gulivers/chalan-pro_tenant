"""Block API usage when trial expired without subscription."""

from __future__ import annotations

import json

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django_tenants.utils import get_public_schema_name

from appbilling.services.access import get_billing_access
from utils.tenant_branding import _resolve_tenant

# Paths always allowed (prefix match on request.path)
BILLING_EXEMPT_PREFIXES = (
    '/api/billing/',
    '/api/validate-token/',
    '/api/login/',
    '/api/logout/',
    '/api/user_detail/',
    '/api/user-permissions/',
    '/api/request-password-reset/',
    '/api/password-reset-confirm/',
    '/stripe/webhook/',
    '/admin/',
    '/media/',
    '/static/',
)


class BillingEnforcementMiddleware(MiddlewareMixin):
    """Return 402 when tenant has no trial/subscription access."""

    def process_request(self, request):
        from django.conf import settings
        if not getattr(settings, 'BILLING_ENFORCEMENT_ENABLED', True):
            return None

        if not getattr(request, 'path', '').startswith('/api/'):
            return None

        for prefix in BILLING_EXEMPT_PREFIXES:
            if request.path.startswith(prefix):
                return None

        from django.db import connection
        public = get_public_schema_name()
        if getattr(connection, 'schema_name', None) == public:
            return None

        tenant = _resolve_tenant(request)
        if tenant is None:
            return None

        access = get_billing_access(tenant)
        if access.allowed:
            return None

        return JsonResponse(
            {
                'detail': 'Subscription required.',
                'code': 'subscription_required',
                'billing_reason': access.reason,
                'suggested_plan_slug': access.suggested_plan_slug,
                'redirect': '/billing',
            },
            status=402,
        )
