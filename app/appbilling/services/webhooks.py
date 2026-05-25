"""Stripe webhook dispatch."""

from __future__ import annotations

import logging

from django.conf import settings
from django.utils import timezone
from django_tenants.utils import get_public_schema_name, schema_context

from appbilling.models import PaymentEvent
from appbilling.services.stripe_client import configure_stripe
from appbilling.services.sync import (
    sync_checkout_completed,
    sync_invoice,
    sync_subscription_from_stripe,
)

logger = logging.getLogger(__name__)

HANDLED_EVENTS = {
    'checkout.session.completed',
    'customer.subscription.created',
    'customer.subscription.updated',
    'customer.subscription.deleted',
    'invoice.paid',
    'invoice.payment_failed',
    'invoice.payment_action_required',
}


def process_webhook_payload(payload: bytes, sig_header: str):
    import stripe

    configure_stripe()
    secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
    if not secret:
        raise ValueError('STRIPE_WEBHOOK_SECRET is not configured.')

    event = stripe.Webhook.construct_event(payload, sig_header, secret)
    event_id = event['id']
    event_type = event['type']

    public = get_public_schema_name()
    with schema_context(public):
        pe, created = PaymentEvent.objects.get_or_create(
            stripe_event_id=event_id,
            defaults={
                'event_type': event_type,
                'payload': event.to_dict() if hasattr(event, 'to_dict') else dict(event),
            },
        )
        if not created and pe.processed:
            return {'status': 'already_processed'}

    try:
        _handle_event(event_type, event['data']['object'])
        with schema_context(public):
            pe.processed = True
            pe.processing_error = ''
            pe.save(update_fields=['processed', 'processing_error'])
    except Exception as exc:
        logger.exception('Webhook processing failed for %s', event_id)
        with schema_context(public):
            pe.processing_error = str(exc)[:2000]
            pe.save(update_fields=['processing_error'])
        raise

    return {'status': 'ok', 'event_type': event_type}


def _handle_event(event_type: str, obj: dict):
    if event_type == 'checkout.session.completed':
        sync_checkout_completed(obj)
    elif event_type in (
        'customer.subscription.created',
        'customer.subscription.updated',
        'customer.subscription.deleted',
    ):
        sync_subscription_from_stripe(obj)
    elif event_type == 'invoice.paid':
        sync_invoice(obj, 'paid')
        sub_id = obj.get('subscription')
        if sub_id:
            import stripe
            configure_stripe()
            stripe_sub = stripe.Subscription.retrieve(sub_id)
            sync_subscription_from_stripe(stripe_sub)
    elif event_type == 'invoice.payment_failed':
        sync_invoice(obj, 'failed')
        customer = obj.get('customer')
        if customer:
            from appbilling.models import Subscription
            public = get_public_schema_name()
            with schema_context(public):
                sub = Subscription.objects.filter(stripe_customer_id=customer).first()
                if sub:
                    sub.status = 'past_due'
                    if not sub.past_due_since:
                        sub.past_due_since = timezone.now()
                    sub.last_payment_status = 'failed'
                    sub.save()
    elif event_type == 'invoice.payment_action_required':
        sync_invoice(obj, 'action_required')
