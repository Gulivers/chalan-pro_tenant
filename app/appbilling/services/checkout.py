"""Stripe Checkout Session creation."""

from __future__ import annotations

import logging

from django.conf import settings

from appbilling.models import Plan
from appbilling.services.customer import ensure_stripe_customer, get_or_create_subscription_row
from appbilling.services.stripe_client import get_stripe
from django_tenants.utils import get_public_schema_name, schema_context
from tenants.models import Domain

logger = logging.getLogger(__name__)


def _tenant_front_base(tenant, request) -> str:
    public = get_public_schema_name()
    with schema_context(public):
        domain = Domain.objects.filter(tenant=tenant, is_primary=True).first()
        if not domain:
            domain = Domain.objects.filter(tenant=tenant).first()
        host = domain.domain if domain else None
    if not host:
        return settings.FRONT_URL.rstrip('/')

    if settings.DEBUG:
        from urllib.parse import urlparse
        parsed = urlparse(settings.FRONT_URL)
        port = parsed.port or 8080
        return f'http://{host}:{port}'

    return f'https://{host}'


def create_checkout_session(tenant, request, plan_slug: str, interval: str) -> dict:
    interval = (interval or 'monthly').lower()
    if interval not in ('monthly', 'yearly'):
        raise ValueError('interval must be monthly or yearly')

    public = get_public_schema_name()
    with schema_context(public):
        plan = Plan.objects.filter(slug=plan_slug, is_active=True).first()
    if not plan:
        raise ValueError(f'Unknown or inactive plan: {plan_slug}')

    price_id = (
        plan.stripe_price_id_yearly if interval == 'yearly' else plan.stripe_price_id_monthly
    )
    if not price_id:
        raise ValueError(f'Stripe price not configured for {plan_slug} ({interval}).')

    sub = ensure_stripe_customer(tenant)
    stripe = get_stripe()
    base = _tenant_front_base(tenant, request)

    success = getattr(settings, 'STRIPE_SUCCESS_URL', '') or f'{base}/billing/success'
    cancel = getattr(settings, 'STRIPE_CANCEL_URL', '') or f'{base}/billing'

    session = stripe.checkout.Session.create(
        customer=sub.stripe_customer_id,
        mode='subscription',
        line_items=[{'price': price_id, 'quantity': 1}],
        success_url=success + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=cancel,
        client_reference_id=str(tenant.id),
        metadata={
            'tenant_id': str(tenant.id),
            'tenant_schema': tenant.schema_name,
            'plan_slug': plan.slug,
            'billing_interval': interval,
        },
        subscription_data={
            'metadata': {
                'tenant_id': str(tenant.id),
                'tenant_schema': tenant.schema_name,
                'plan_slug': plan.slug,
            },
        },
        allow_promotion_codes=True,
    )

    public = get_public_schema_name()
    with schema_context(public):
        sub.stripe_checkout_session_id = session.id
        sub.save(update_fields=['stripe_checkout_session_id', 'updated_at'])

    logger.info('Checkout session %s for tenant %s plan %s', session.id, tenant.schema_name, plan_slug)
    return {'checkout_url': session.url, 'session_id': session.id}
