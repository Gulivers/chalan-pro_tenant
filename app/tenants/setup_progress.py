"""
Tenant-owner Welcome / company setup progress helpers.

Stored on Tenant.setup_progress (public schema). Entity counts live in the
tenant schema and are merged at read time so creating records outside the
assistant still advances steps.
"""
from __future__ import annotations

from copy import deepcopy

STATUS_PENDING = 'pending'
STATUS_DONE = 'done'
STATUS_SKIPPED = 'skipped'

# Critical for Schedule: cannot operate jobs without builder + community (job).
CRITICAL_STEPS = ('builder', 'communities')

# Ordered product journey (phases 1 → 2 → 3).
STEP_ORDER = (
    'inventory',
    'crew_categories',
    'crews',
    'party_types',
    'party_categories',
    'builder',
    'communities',
    'house_models',
    'first_event',
    'pick_ticket',
    'work_prices',
    'first_contract',
)

SKIPPABLE_STEPS = frozenset(
    {
        'inventory',
        'crew_categories',
        'crews',
        'party_types',
        'party_categories',
        'house_models',
        'first_event',
        'pick_ticket',
        'work_prices',
        'first_contract',
    }
)

COUNT_KEYS = {
    'inventory': 'seed_inventory_done',
    'crew_categories': 'crew_categories',
    'crews': 'crews',
    'party_types': 'party_types',
    'party_categories': 'party_categories',
    'builder': 'builders',
    'communities': 'communities',
    'house_models': 'house_models',
    'first_event': 'events',
    'pick_ticket': 'material_requests',
    'work_prices': 'work_prices',
    'first_contract': 'contracts',
}


def default_setup_progress() -> dict:
    return {
        'steps': {key: STATUS_PENDING for key in STEP_ORDER},
        'panel_dismissed': False,
        'banner_dismissed': False,
        'welcome_modal_dismissed': False,
    }


def normalize_progress(raw) -> dict:
    base = default_setup_progress()
    if not isinstance(raw, dict):
        return base
    steps = raw.get('steps') if isinstance(raw.get('steps'), dict) else {}
    for key in STEP_ORDER:
        value = steps.get(key, STATUS_PENDING)
        if value not in (STATUS_PENDING, STATUS_DONE, STATUS_SKIPPED):
            value = STATUS_PENDING
        base['steps'][key] = value
    base['panel_dismissed'] = bool(raw.get('panel_dismissed'))
    base['banner_dismissed'] = bool(raw.get('banner_dismissed'))
    base['welcome_modal_dismissed'] = bool(raw.get('welcome_modal_dismissed'))
    return base


def collect_entity_counts() -> dict:
    """Count operational masters in the current tenant schema."""
    from appschedule.models import Event
    from apptransactions.models import Document, PartyCategory, PartyType
    from crewsapp.models import Category, Crew
    from ctrctsapp.models import Builder, Contract, HouseModel, Job, WorkPrice

    mr_count = Document.objects.filter(document_type__type_code='MR').count()
    pick_count = Document.objects.filter(document_type__type_code='PICK').count()

    return {
        'builders': Builder.objects.count(),
        'communities': Job.objects.count(),
        'crew_categories': Category.objects.count(),
        'crews': Crew.objects.count(),
        'party_types': PartyType.objects.count(),
        'party_categories': PartyCategory.objects.count(),
        'house_models': HouseModel.objects.count(),
        'events': Event.objects.count(),
        'material_requests': mr_count,
        'pick_documents': pick_count,
        'work_prices': WorkPrice.objects.count(),
        'contracts': Contract.objects.count(),
    }


def _count_satisfies(step: str, counts: dict, seed_inventory_done: bool) -> bool:
    if step == 'inventory':
        return bool(seed_inventory_done)
    if step == 'pick_ticket':
        return (counts.get('material_requests') or 0) > 0 or (
            counts.get('pick_documents') or 0
        ) > 0
    key = COUNT_KEYS.get(step)
    if not key or key == 'seed_inventory_done':
        return False
    return (counts.get(key) or 0) > 0


def merge_auto_done(progress: dict, counts: dict, seed_inventory_done: bool) -> dict:
    """Promote pending → done when live data proves the step is satisfied."""
    merged = deepcopy(normalize_progress(progress))
    for step in STEP_ORDER:
        if merged['steps'][step] == STATUS_DONE:
            continue
        if _count_satisfies(step, counts, seed_inventory_done):
            merged['steps'][step] = STATUS_DONE
    return merged


def critical_ready(steps: dict) -> bool:
    return all(steps.get(key) == STATUS_DONE for key in CRITICAL_STEPS)


def next_recommended_step(steps: dict) -> str | None:
    for key in STEP_ORDER:
        if steps.get(key) == STATUS_PENDING:
            return key
    return None


def apply_action(progress: dict, *, action: str, step: str | None = None) -> dict:
    data = normalize_progress(progress)
    action = (action or '').strip().lower()

    if action == 'dismiss_panel':
        data['panel_dismissed'] = True
        return data
    if action == 'dismiss_banner':
        data['banner_dismissed'] = True
        return data
    if action == 'dismiss_welcome':
        data['welcome_modal_dismissed'] = True
        return data
    if action == 'reopen':
        data['panel_dismissed'] = False
        data['banner_dismissed'] = False
        # Keep welcome_modal_dismissed — reopen opens the step assistant, not the first-run modal
        return data
    if action == 'reopen_welcome':
        data['welcome_modal_dismissed'] = False
        data['panel_dismissed'] = False
        data['banner_dismissed'] = False
        return data
    if action == 'finish':
        # Caller still enforces critical_ready before setting setup_completed.
        return data

    if action in ('skip', 'complete') and step in STEP_ORDER:
        if action == 'skip' and step not in SKIPPABLE_STEPS:
            raise ValueError(f'Step "{step}" cannot be skipped.')
        data['steps'][step] = STATUS_SKIPPED if action == 'skip' else STATUS_DONE
        return data

    raise ValueError(f'Unsupported action "{action}".')
