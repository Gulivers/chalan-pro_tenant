"""Unified tenant workspace access (active flag + billing)."""

from __future__ import annotations

from dataclasses import dataclass

from appbilling.services.access import BillingAccess, get_billing_access
from appbilling.services.plans import get_effective_plan_for_tenant, get_plan_by_slug


@dataclass
class TenantAccess:
    """Single decision for API, admin, SPA guard, and login."""

    allowed: bool
    reason: str
    tenant_active: bool
    billing: BillingAccess | None = None

    @property
    def redirect_path(self) -> str:
        if not self.tenant_active:
            return '/account-suspended'
        if not self.allowed:
            return '/billing'
        return '/'


def get_tenant_access(tenant) -> TenantAccess:
    """
    Order: is_active → billing (trial / Stripe).
    Inactive tenants are blocked regardless of trial or subscription.
    """
    if tenant is None:
        return TenantAccess(
            allowed=True,
            reason='no_tenant',
            tenant_active=True,
            billing=None,
        )

    if not getattr(tenant, 'is_active', True):
        return TenantAccess(
            allowed=False,
            reason='tenant_inactive',
            tenant_active=False,
            billing=None,
        )

    billing = get_billing_access(tenant)
    return TenantAccess(
        allowed=billing.allowed,
        reason=billing.reason,
        tenant_active=True,
        billing=billing,
    )


def tenant_access_status_payload(tenant) -> dict:
    """JSON for GET /api/billing/status/ (SPA guard + billing page)."""
    access = get_tenant_access(tenant)
    plan = get_effective_plan_for_tenant(tenant)
    billing = access.billing

    payload = {
        'tenant_active': access.tenant_active,
        'access_allowed': access.allowed,
        'access_reason': access.reason,
        'redirect': access.redirect_path,
        'landing_selected_plan': getattr(tenant, 'landing_selected_plan', None),
        'recommended_plan': getattr(tenant, 'recommended_plan', None),
        'plan_limits': {
            'max_crews': plan.max_crews if plan else None,
            'max_users': plan.max_users if plan else None,
        },
    }

    if billing is None:
        payload.update({
            'trial_active': False,
            'trial_days_left': 0,
            'trial_end': None,
            'subscription_status': None,
            'suggested_plan_slug': None,
            'needs_payment': False,
            'in_grace_period': False,
            'current_plan_slug': None,
            'suggested_plan': None,
        })
        return payload

    suggested_plan = get_plan_by_slug(billing.suggested_plan_slug)
    payload.update({
        'trial_active': billing.trial_active,
        'trial_days_left': billing.trial_days_left,
        'trial_end': billing.trial_end,
        'subscription_status': billing.subscription_status,
        'suggested_plan_slug': billing.suggested_plan_slug,
        'needs_payment': billing.needs_payment,
        'in_grace_period': billing.in_grace_period,
        'current_plan_slug': billing.current_plan_slug,
        'suggested_plan': _serialize_plan_brief(suggested_plan) if suggested_plan else None,
    })
    return payload


def _serialize_plan_brief(plan) -> dict:
    return {
        'slug': plan.slug,
        'name': plan.name,
        'monthly_price': str(plan.monthly_price),
        'yearly_price': str(plan.yearly_price) if plan.yearly_price else None,
        'is_recommended': plan.is_recommended,
        'max_crews': plan.max_crews,
    }


def assert_login_allowed(tenant) -> tuple[bool, str | None]:
    """
    Login policy: block only deactivated workspaces.
    Billing issues still allow login → SPA redirects to /billing.
    """
    access = get_tenant_access(tenant)
    if not access.tenant_active:
        return False, 'This workspace has been deactivated. Contact support.'
    return True, None
