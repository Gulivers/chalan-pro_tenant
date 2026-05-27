"""Billing access decisions (source of truth for API/UI gates)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django_tenants.utils import get_public_schema_name, schema_context

from appbilling.models import Subscription
from appbilling.services.plans import get_suggested_plan_slug, get_effective_plan_for_tenant


GRACE_DAYS = getattr(settings, 'BILLING_PAST_DUE_GRACE_DAYS', 7)


@dataclass
class BillingAccess:
    allowed: bool
    reason: str
    trial_active: bool
    trial_days_left: int | None
    trial_end: str | None
    subscription_status: str | None
    suggested_plan_slug: str
    needs_payment: bool
    in_grace_period: bool
    current_plan_slug: str | None


def _trial_bounds(tenant):
    from datetime import datetime, time as dt_time

    start = getattr(tenant, 'trial_start', None)
    end = getattr(tenant, 'trial_end', None)
    if end is None and getattr(tenant, 'created_on', None):
        if start is None:
            start = datetime.combine(tenant.created_on, dt_time.min)
        if timezone.is_naive(start):
            start = timezone.make_aware(start)
        end = start + timedelta(days=30)
    return start, end


def _get_subscription(tenant) -> Subscription | None:
    public = get_public_schema_name()
    with schema_context(public):
        try:
            return Subscription.objects.select_related('plan').get(tenant=tenant)
        except Subscription.DoesNotExist:
            return None


def _stripe_access(sub: Subscription | None, now) -> tuple[bool, str, bool]:
    if not sub or not sub.stripe_subscription_id:
        return False, 'no_subscription', False

    status = sub.status or 'incomplete'
    if status in ('active', 'trialing'):
        return True, status, False

    if status == 'past_due':
        since = sub.past_due_since or sub.updated_at
        if since and (now - since) <= timedelta(days=GRACE_DAYS):
            return True, 'past_due_grace', True
        return False, 'past_due', False

    if status in ('canceled', 'unpaid', 'incomplete_expired', 'incomplete'):
        return False, status, False

    return False, status, False


def get_billing_access(tenant) -> BillingAccess:
    now = timezone.now()
    suggested = get_suggested_plan_slug(tenant)
    trial_start, trial_end = _trial_bounds(tenant)

    trial_active = False
    trial_days_left = None
    trial_end_iso = None

    if trial_end:
        if timezone.is_naive(trial_end):
            trial_end = timezone.make_aware(trial_end)
        trial_end_iso = trial_end.isoformat()
        if getattr(tenant, 'on_trial', True) and now < trial_end:
            trial_active = True
            trial_days_left = max(0, (trial_end.date() - now.date()).days)

    sub = _get_subscription(tenant)
    stripe_ok, stripe_reason, in_grace = _stripe_access(sub, now)

    if trial_active:
        plan = get_effective_plan_for_tenant(tenant)
        return BillingAccess(
            allowed=True,
            reason='trial',
            trial_active=True,
            trial_days_left=trial_days_left,
            trial_end=trial_end_iso,
            subscription_status=sub.status if sub else None,
            suggested_plan_slug=suggested,
            needs_payment=False,
            in_grace_period=False,
            current_plan_slug=plan.slug if plan else None,
        )

    if stripe_ok:
        plan = sub.plan if sub else None
        return BillingAccess(
            allowed=True,
            reason=stripe_reason,
            trial_active=False,
            trial_days_left=0,
            trial_end=trial_end_iso,
            subscription_status=sub.status if sub else None,
            suggested_plan_slug=suggested,
            needs_payment=stripe_reason == 'past_due_grace',
            in_grace_period=in_grace,
            current_plan_slug=plan.slug if plan else None,
        )

    return BillingAccess(
        allowed=False,
        reason='trial_expired' if trial_end and now >= trial_end else stripe_reason,
        trial_active=False,
        trial_days_left=0,
        trial_end=trial_end_iso,
        subscription_status=sub.status if sub else None,
        suggested_plan_slug=suggested,
        needs_payment=True,
        in_grace_period=False,
        current_plan_slug=sub.plan.slug if sub and sub.plan else None,
    )


def billing_status_payload(tenant) -> dict:
    from tenants.services.access import tenant_access_status_payload
    return tenant_access_status_payload(tenant)
