"""Stripe Customer lifecycle."""

from __future__ import annotations

import logging

from django_tenants.utils import get_public_schema_name, schema_context

from appbilling.models import Subscription
from appbilling.services.plans import get_suggested_plan_slug, plan_slug_from_label
from appbilling.services.stripe_client import get_stripe
from tenants.models import Domain

logger = logging.getLogger(__name__)


def _primary_domain(tenant) -> str:
    public = get_public_schema_name()
    with schema_context(public):
        domain = Domain.objects.filter(tenant=tenant, is_primary=True).first()
        if domain:
            return domain.domain
        domain = Domain.objects.filter(tenant=tenant).first()
        return domain.domain if domain else ''


def get_or_create_subscription_row(tenant) -> Subscription:
    public = get_public_schema_name()
    with schema_context(public):
        sub, _ = Subscription.objects.get_or_create(tenant=tenant)
        return sub


def ensure_stripe_customer(tenant) -> Subscription:
    """Create Stripe Customer on first billing visit; persist ID on Subscription."""
    sub = get_or_create_subscription_row(tenant)
    if sub.stripe_customer_id:
        return sub

    stripe = get_stripe()
    domain = _primary_domain(tenant)
    plan_slug = get_suggested_plan_slug(tenant)

    customer = stripe.Customer.create(
        email=tenant.email or None,
        name=tenant.name,
        metadata={
            'tenant_id': str(tenant.id),
            'tenant_schema': tenant.schema_name,
            'tenant_domain': domain,
            'suggested_plan_slug': plan_slug,
            'landing_selected_plan': plan_slug_from_label(tenant.landing_selected_plan) or '',
            'recommended_plan': plan_slug_from_label(tenant.recommended_plan) or '',
        },
    )

    public = get_public_schema_name()
    with schema_context(public):
        sub.stripe_customer_id = customer.id
        sub.save(update_fields=['stripe_customer_id', 'updated_at'])
        logger.info('Created Stripe customer %s for tenant %s', customer.id, tenant.schema_name)

    return sub
