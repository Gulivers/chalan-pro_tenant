"""Local 30-day trial on tenant creation."""

from __future__ import annotations

from datetime import timedelta

from django.utils import timezone


TRIAL_DAYS = 30


def start_trial_for_tenant(tenant):
    now = timezone.now()
    tenant.trial_start = now
    tenant.trial_end = now + timedelta(days=TRIAL_DAYS)
    tenant.on_trial = True
    tenant.paid_until = None
    return tenant
