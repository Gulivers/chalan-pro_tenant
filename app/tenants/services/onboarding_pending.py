"""Pending onboarding registrations until email is verified."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Optional
from uuid import UUID

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from tenants.models import OnboardingPendingRegistration, Tenant
from tenants.services.onboarding_parse import (
    OnboardingFormData,
    form_data_to_payload,
    payload_to_form_data,
)
from tenants.services.onboarding_provision import OnboardingProvisionError, provision_tenant_workspace
from tenants.services.onboarding_secrets import seal_admin_password

logger = logging.getLogger(__name__)


def _verification_expiry_hours() -> int:
    return int(getattr(settings, 'ONBOARDING_VERIFY_EXPIRY_HOURS', 24))


def _build_verify_url(token: UUID) -> str:
    base = (settings.FRONT_URL or '').rstrip('/')
    return f'{base}/onboarding/verify?token={token}'


def create_pending_registration(
    data: OnboardingFormData,
    *,
    logo=None,
    client_ip: Optional[str] = None,
) -> OnboardingPendingRegistration:
    OnboardingPendingRegistration.objects.filter(
        email__iexact=data.email,
        consumed_at__isnull=True,
    ).delete()

    sealed_password = seal_admin_password(data.admin_password or '')
    payload = form_data_to_payload(data, sealed_password)
    expires_at = timezone.now() + timedelta(hours=_verification_expiry_hours())

    return OnboardingPendingRegistration.objects.create(
        email=data.email.lower(),
        company_name=data.company_name,
        payload=payload,
        logo=logo,
        expires_at=expires_at,
        client_ip=client_ip,
    )


def send_verification_email(pending: OnboardingPendingRegistration) -> bool:
    verify_url = _build_verify_url(pending.token)
    context = {
        'company_name': pending.company_name,
        'verify_url': verify_url,
        'expiry_hours': _verification_expiry_hours(),
    }
    text_body = (
        f'Confirm your email to create your JobRhythm workspace for {pending.company_name}.\n\n'
        f'Open this link to continue:\n{verify_url}\n\n'
        f'This link expires in {_verification_expiry_hours()} hours.\n'
    )
    html_body = render_to_string('onboarding_verify_email.html', context)
    msg = EmailMultiAlternatives(
        'Confirm your email to start your JobRhythm trial',
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        [pending.email],
    )
    msg.attach_alternative(html_body, 'text/html')

    if not getattr(settings, 'EMAIL_HOST_PASSWORD', ''):
        if settings.DEBUG:
            logger.warning(
                'onboarding_verify: SMTP not configured; verification link for %s: %s',
                pending.email,
                verify_url,
            )
            return False
        raise OnboardingProvisionError(
            'Email delivery is not configured. Please try again later.',
            status_code=503,
        )

    msg.send(fail_silently=False)
    logger.info('onboarding_verify: email sent to %s', pending.email)
    return True


def complete_pending_registration(token: UUID) -> dict:
    try:
        pending = OnboardingPendingRegistration.objects.get(token=token)
    except OnboardingPendingRegistration.DoesNotExist:
        raise OnboardingProvisionError(
            'This verification link is invalid or has already been used.',
            status_code=400,
        )

    now = timezone.now()
    if pending.consumed_at:
        raise OnboardingProvisionError(
            'This verification link has already been used.',
            status_code=400,
        )
    if pending.expires_at < now:
        raise OnboardingProvisionError(
            'This verification link has expired. Please start onboarding again.',
            status_code=400,
        )

    data = payload_to_form_data(pending.payload)
    if Tenant.objects.filter(email=data.email).exists():
        pending.consumed_at = now
        pending.save(update_fields=['consumed_at'])
        raise OnboardingProvisionError(
            'This email is already registered. Please sign in instead.',
            status_code=400,
        )

    pending.verified_at = now
    pending.save(update_fields=['verified_at'])

    result = provision_tenant_workspace(data, logo=pending.logo)
    pending.consumed_at = timezone.now()
    pending.save(update_fields=['consumed_at'])
    return result
