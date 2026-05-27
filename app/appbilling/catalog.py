"""Read-only plan catalog for API and marketing surfaces."""

from __future__ import annotations

from django_tenants.utils import get_public_schema_name, schema_context

from appbilling.models import Plan


def serialize_plan(plan: Plan) -> dict:
    return {
        'slug': plan.slug,
        'name': plan.name,
        'monthly_price': str(plan.monthly_price),
        'yearly_price': str(plan.yearly_price) if plan.yearly_price is not None else None,
        'is_recommended': plan.is_recommended,
        'max_crews': plan.max_crews,
        'max_users': plan.max_users,
        'display_order': plan.display_order,
    }


def list_active_plans() -> list[dict]:
    with schema_context(get_public_schema_name()):
        plans = Plan.objects.filter(is_active=True).order_by('display_order', 'slug')
        return [serialize_plan(p) for p in plans]
