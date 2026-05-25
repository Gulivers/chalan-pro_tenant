"""Plan resolution and tenant label mapping."""

from __future__ import annotations

from django_tenants.utils import schema_context, get_public_schema_name

from appbilling.models import Plan

PLAN_LABEL_TO_SLUG = {
    'starter': 'starter',
    'professional': 'professional',
    'pro': 'professional',
    'enterprise': 'enterprise',
    'Starter': 'starter',
    'Professional': 'professional',
    'Enterprise': 'enterprise',
}

DEFAULT_PLAN_SLUG = 'professional'


def plan_slug_from_label(raw) -> str | None:
    if raw is None or raw == '':
        return None
    s = str(raw).strip()
    if not s:
        return None
    if s in PLAN_LABEL_TO_SLUG:
        return PLAN_LABEL_TO_SLUG[s]
    lower = s.lower().replace(' ', '-')
    return PLAN_LABEL_TO_SLUG.get(lower)


def get_plan_by_slug(slug: str) -> Plan | None:
    public = get_public_schema_name()
    with schema_context(public):
        return Plan.objects.filter(slug=slug, is_active=True).first()


def get_suggested_plan_slug(tenant) -> str:
    slug = plan_slug_from_label(getattr(tenant, 'landing_selected_plan', None))
    if slug:
        return slug
    slug = plan_slug_from_label(getattr(tenant, 'recommended_plan', None))
    if slug:
        return slug
    return DEFAULT_PLAN_SLUG


def get_effective_plan_for_tenant(tenant) -> Plan | None:
    """Plan used for crew limits and UI hints."""
    public = get_public_schema_name()
    with schema_context(public):
        from appbilling.models import Subscription

        sub = (
            Subscription.objects.select_related('plan')
            .filter(tenant=tenant, plan__isnull=False)
            .first()
        )
        if sub and sub.plan_id and sub.status in ('active', 'trialing', 'past_due'):
            return sub.plan

    slug = get_suggested_plan_slug(tenant)
    return get_plan_by_slug(slug) or get_plan_by_slug(DEFAULT_PLAN_SLUG)


def get_max_crews_for_tenant(tenant) -> int | None:
    plan = get_effective_plan_for_tenant(tenant)
    if not plan:
        return None
    return plan.max_crews
