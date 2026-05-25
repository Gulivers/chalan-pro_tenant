"""Stripe SDK wrapper."""

from __future__ import annotations

import stripe
from django.conf import settings


def configure_stripe():
    key = getattr(settings, 'STRIPE_SECRET_KEY', '') or ''
    if not key:
        raise ValueError('STRIPE_SECRET_KEY is not configured.')
    stripe.api_key = key
    return stripe


def get_stripe():
    configure_stripe()
    return stripe
