"""Billing API views (tenant + public webhook)."""

from __future__ import annotations

import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django_tenants.utils import get_public_schema_name, schema_context

from appbilling.models import Plan
from appbilling.services.access import billing_status_payload
from appbilling.services.checkout import create_checkout_session
from appbilling.services.customer import ensure_stripe_customer
from appbilling.services.portal import create_portal_session
from appbilling.services.webhooks import process_webhook_payload
from utils.tenant_branding import _resolve_tenant

logger = logging.getLogger(__name__)


def _require_tenant(request):
    tenant = _resolve_tenant(request)
    if tenant is None:
        return None, Response(
            {'detail': 'Tenant context not found.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return tenant, None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billing_status(request):
    tenant, err = _require_tenant(request)
    if err:
        return err
    return Response(billing_status_payload(tenant))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billing_plans(request):
    with schema_context(get_public_schema_name()):
        plans = list(Plan.objects.filter(is_active=True).order_by('display_order'))
    data = [
        {
            'slug': p.slug,
            'name': p.name,
            'monthly_price': str(p.monthly_price),
            'yearly_price': str(p.yearly_price) if p.yearly_price else None,
            'is_recommended': p.is_recommended,
            'max_crews': p.max_crews,
            'max_users': p.max_users,
        }
        for p in plans
    ]
    return Response({'plans': data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout(request):
    tenant, err = _require_tenant(request)
    if err:
        return err

    plan_slug = (request.data.get('plan_slug') or '').strip().lower()
    interval = (request.data.get('billing_interval') or request.data.get('interval') or 'monthly').strip().lower()

    if not plan_slug:
        from appbilling.services.plans import get_suggested_plan_slug
        plan_slug = get_suggested_plan_slug(tenant)

    try:
        result = create_checkout_session(tenant, request, plan_slug, interval)
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        logger.exception('Checkout session failed')
        return Response(
            {'detail': 'Could not start checkout. Please try again later.'},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_portal(request):
    tenant, err = _require_tenant(request)
    if err:
        return err

    try:
        ensure_stripe_customer(tenant)
        result = create_portal_session(tenant, request)
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        logger.exception('Portal session failed')
        return Response(
            {'detail': 'Could not open billing portal.'},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response(result)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """POST https://api.jobrhythm.net/stripe/webhook/"""
    sig = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    try:
        process_webhook_payload(request.body, sig)
    except ValueError as exc:
        logger.warning('Webhook rejected: %s', exc)
        return HttpResponse(status=400)
    except Exception:
        return HttpResponse(status=500)
    return HttpResponse(status=200)
