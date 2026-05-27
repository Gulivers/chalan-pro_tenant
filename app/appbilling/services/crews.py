"""Crew count limits by subscription plan."""

from __future__ import annotations

from tenants.services.access import get_tenant_access
from appbilling.services.plans import get_effective_plan_for_tenant, get_max_crews_for_tenant
from crewsapp.models import Crew


def count_active_crews() -> int:
    return Crew.objects.filter(status=True).count()


def validate_crew_create(tenant, *, adding: int = 1) -> str | None:
    """
    Return error message if creating `adding` crews would exceed plan limit.
    None if allowed.
    """
    access = get_tenant_access(tenant)
    if not access.allowed:
        if not access.tenant_active:
            return 'This workspace has been deactivated.'
        return (
            'Your trial has ended and there is no active subscription. '
            'Please upgrade in Billing to add crews.'
        )

    max_crews = get_max_crews_for_tenant(tenant)
    if max_crews is None:
        return None

    current = count_active_crews()
    if current + adding > max_crews:
        plan = get_effective_plan_for_tenant(tenant)
        plan_name = plan.name if plan else 'your plan'
        return (
            f'{plan_name} allows up to {max_crews} active crews. '
            f'You have {current}. Upgrade your plan to add more.'
        )
    return None
