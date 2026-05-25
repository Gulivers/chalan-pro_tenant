"""Stripe Customer Portal."""

from __future__ import annotations

from django.conf import settings

from appbilling.services.customer import ensure_stripe_customer, _primary_domain
from appbilling.services.stripe_client import get_stripe
from appbilling.services.checkout import _tenant_front_base


def create_portal_session(tenant, request) -> dict:
    sub = ensure_stripe_customer(tenant)
    stripe = get_stripe()
    base = _tenant_front_base(tenant, request)
    return_url = (
        getattr(settings, 'STRIPE_CUSTOMER_PORTAL_RETURN_URL', '')
        or f'{base}/billing'
    )

    session = stripe.billing_portal.Session.create(
        customer=sub.stripe_customer_id,
        return_url=return_url,
    )
    return {'portal_url': session.url}
