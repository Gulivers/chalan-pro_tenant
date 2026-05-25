"""Sync Stripe subscription/invoice state into local DB."""

from __future__ import annotations

import logging
from datetime import datetime, timezone as dt_timezone

from django.utils import timezone
from django_tenants.utils import get_public_schema_name, schema_context

from appbilling.models import Plan, Subscription
from appbilling.services.plans import get_plan_by_slug
from tenants.models import Tenant

logger = logging.getLogger(__name__)


def _ts(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=dt_timezone.utc)
    return value


def _resolve_tenant_from_metadata(meta: dict) -> Tenant | None:
    if not meta:
        return None
    tenant_id = meta.get('tenant_id')
    schema = meta.get('tenant_schema')
    public = get_public_schema_name()
    with schema_context(public):
        if tenant_id:
            t = Tenant.objects.filter(pk=tenant_id).first()
            if t:
                return t
        if schema:
            return Tenant.objects.filter(schema_name=schema).first()
    return None


def _plan_from_price_id(price_id: str) -> Plan | None:
    if not price_id:
        return None
    public = get_public_schema_name()
    with schema_context(public):
        from django.db.models import Q
        return Plan.objects.filter(
            Q(stripe_price_id_monthly=price_id) | Q(stripe_price_id_yearly=price_id)
        ).first()


def sync_subscription_from_stripe(stripe_sub: dict, tenant: Tenant | None = None) -> Subscription | None:
    meta = stripe_sub.get('metadata') or {}
    tenant = tenant or _resolve_tenant_from_metadata(meta)
    if not tenant:
        customer_id = stripe_sub.get('customer')
        if customer_id:
            public = get_public_schema_name()
            with schema_context(public):
                sub_row = Subscription.objects.filter(stripe_customer_id=customer_id).first()
                if sub_row:
                    tenant = sub_row.tenant
    if not tenant:
        logger.warning('Could not resolve tenant for subscription %s', stripe_sub.get('id'))
        return None

    items = stripe_sub.get('items', {}).get('data') or []
    price_id = None
    if items:
        price_id = (items[0].get('price') or {}).get('id')

    plan = _plan_from_price_id(price_id)
    if not plan:
        plan = get_plan_by_slug(meta.get('plan_slug') or '')

    status = stripe_sub.get('status') or 'incomplete'
    public = get_public_schema_name()
    with schema_context(public):
        sub, _ = Subscription.objects.get_or_create(tenant=tenant)
        sub.stripe_subscription_id = stripe_sub.get('id') or sub.stripe_subscription_id
        sub.stripe_customer_id = stripe_sub.get('customer') or sub.stripe_customer_id
        if plan:
            sub.plan = plan
        sub.status = status
        sub.trial_start = _ts(stripe_sub.get('trial_start'))
        sub.trial_end = _ts(stripe_sub.get('trial_end'))
        sub.current_period_start = _ts(stripe_sub.get('current_period_start'))
        sub.current_period_end = _ts(stripe_sub.get('current_period_end'))
        sub.cancel_at_period_end = bool(stripe_sub.get('cancel_at_period_end'))
        sub.canceled_at = _ts(stripe_sub.get('canceled_at'))

        if status == 'past_due' and not sub.past_due_since:
            sub.past_due_since = timezone.now()
        elif status != 'past_due':
            sub.past_due_since = None

        sub.metadata = {**(sub.metadata or {}), 'stripe_status': status}
        sub.save()

        tenant.on_trial = False
        if sub.current_period_end:
            tenant.paid_until = sub.current_period_end.date()
        tenant.save(update_fields=['on_trial', 'paid_until', 'trial_start', 'trial_end'])

    logger.info('Synced subscription %s for %s status=%s', sub.stripe_subscription_id, tenant.schema_name, status)
    return sub


def sync_checkout_completed(session: dict) -> Subscription | None:
    tenant = _resolve_tenant_from_metadata(session.get('metadata') or {})
    if not tenant and session.get('client_reference_id'):
        public = get_public_schema_name()
        with schema_context(public):
            tenant = Tenant.objects.filter(pk=session['client_reference_id']).first()

    if not tenant:
        return None

    customer_id = session.get('customer')
    subscription_id = session.get('subscription')
    public = get_public_schema_name()
    with schema_context(public):
        sub, _ = Subscription.objects.get_or_create(tenant=tenant)
        if customer_id:
            sub.stripe_customer_id = customer_id
        if subscription_id:
            sub.stripe_subscription_id = subscription_id
        sub.stripe_checkout_session_id = session.get('id') or sub.stripe_checkout_session_id
        sub.save()

    if subscription_id:
        from appbilling.services.stripe_client import get_stripe
        stripe = get_stripe()
        stripe_sub = stripe.Subscription.retrieve(subscription_id)
        return sync_subscription_from_stripe(stripe_sub, tenant=tenant)

    return sub


def sync_invoice(invoice: dict, payment_status: str):
    customer_id = invoice.get('customer')
    if not customer_id:
        return
    public = get_public_schema_name()
    with schema_context(public):
        sub = Subscription.objects.filter(stripe_customer_id=customer_id).select_related('tenant').first()
    if not sub:
        return

    public = get_public_schema_name()
    with schema_context(public):
        sub.last_payment_status = payment_status
        sub.last_invoice_id = invoice.get('id') or ''
        if payment_status == 'paid' and invoice.get('status') == 'paid':
            period_end = invoice.get('lines', {}).get('data', [{}])
            if period_end:
                pe = period_end[0].get('period', {}).get('end')
                if pe:
                    sub.tenant.paid_until = datetime.fromtimestamp(pe, tz=dt_timezone.utc).date()
                    sub.tenant.on_trial = False
                    sub.tenant.save(update_fields=['paid_until', 'on_trial'])
        sub.save(update_fields=['last_payment_status', 'last_invoice_id', 'updated_at'])
