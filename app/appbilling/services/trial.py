"""Tenant trial / payment-required helpers (public schema).

Sales-led default: new workspaces are created without a free product trial
(`mark_payment_required_for_tenant`). A multi-day trial is only for legacy
tenants or when staff enable it manually (Admin / `start_trial_for_tenant`).
"""

from __future__ import annotations

from datetime import timedelta

from django.utils import timezone


# Used only by start_trial_for_tenant (Admin, CLI, backfill) — not by onboarding.
TRIAL_DAYS = 30


def mark_payment_required_for_tenant(tenant):
    """Post-demo sales-led: workspace exists; product locked until Stripe."""
    tenant.trial_start = None
    tenant.trial_end = timezone.now()
    tenant.on_trial = False
    tenant.paid_until = None
    return tenant


def start_trial_for_tenant(tenant, days: int = TRIAL_DAYS):
    """Grant an explicit local trial window (Admin / CLI / legacy tools)."""
    now = timezone.now()
    tenant.trial_start = now
    tenant.trial_end = now + timedelta(days=days)
    tenant.on_trial = True
    tenant.paid_until = None
    return tenant
