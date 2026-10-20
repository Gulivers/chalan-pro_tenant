"""
Work Order status, progress checkpoints, and Work Account rollup.

Status catalog is tenant-wide (one list). Progress templates are per crew
category. Publishing an Event assigns Scheduled + clones progress items.
Date/crew changes never reset status.
"""

from __future__ import annotations

from django.db import transaction
from django.db.models import Prefetch
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from appschedule.models import (
    Event,
    WorkOrderProgressCheck,
    WorkOrderProgressItem,
    WorkOrderProgressTemplate,
    WorkOrderStatus,
    WorkOrderStatusHistory,
    WorkOrderTracking,
)

DEFAULT_WORK_ORDER_STATUSES = (
    # code, name, sequence, is_initial, is_terminal, req_insp, req_comp, description
    (
        'scheduled',
        'Scheduled',
        1,
        True,
        False,
        False,
        False,
        'Work is scheduled in JobRhythm or the Builder schedule. The Work Order is created here.',
    ),
    (
        'pending_prereqs',
        'Pending Prereqs',
        2,
        False,
        False,
        False,
        False,
        'Waiting on construction conditions, materials, or other work before advancing.',
    ),
    (
        'in_progress',
        'In Progress',
        3,
        False,
        False,
        False,
        False,
        'The crew is performing the installation.',
    ),
    (
        'corrections_required',
        'Corrections Required',
        4,
        False,
        False,
        False,
        False,
        'Corrections are pending from the crew, supervisor, or an inspection.',
    ),
    (
        'pending_inspection',
        'Pending Inspection',
        5,
        False,
        False,
        True,
        False,
        'Installation is waiting for an inspection.',
    ),
    (
        'passed_closed',
        'Passed & Closed',
        6,
        False,
        True,
        False,
        True,
        'Work was approved and is considered complete.',
    ),
)

# Initial progress templates keyed by Category.name match (case-insensitive contains).
DEFAULT_PROGRESS_TEMPLATES = {
    'underground': {
        'name': 'Underground / Slabs',
        'match': ('underground', 'slab'),
        'items': (
            ('site_ready', 'Site Ready', 1, True, True, False),
            ('material_delivered', 'Material Delivered', 2, True, True, False),
            ('installation_finished', 'Installation Finished', 3, True, True, False),
            ('supervisor_qc', 'Supervisor QC', 4, True, True, False),
            ('underground_inspection_passed', 'Underground Inspection Passed', 5, False, True, False),
        ),
    },
    'tug': {
        'name': 'TUG',
        'match': ('tug',),
        'items': (
            ('underground_approved', 'Underground Approved', 1, True, True, False),
            ('meter_equipment_ready', 'Meter Equipment Ready', 2, True, True, False),
            ('material_delivered', 'Material Delivered', 3, True, True, False),
            ('installation_finished', 'Installation Finished', 4, True, True, False),
            ('supervisor_qc', 'Supervisor QC', 5, True, True, False),
            ('tug_inspection_passed', 'TUG Inspection Passed', 6, False, True, False),
        ),
    },
    'rough': {
        'name': 'Rough-in',
        'match': ('rough',),
        'items': (
            ('frame_ready', 'Frame Ready', 1, True, True, False),
            ('roof_ready', 'Roof Ready', 2, True, True, False),
            ('plumbing_ready', 'Plumbing Ready', 3, True, True, False),
            ('hvac_ready', 'HVAC Ready', 4, True, True, False),
            ('material_delivered', 'Material Delivered', 5, True, True, False),
            ('installation_finished', 'Installation Finished', 6, True, True, False),
            ('supervisor_qc', 'Supervisor QC', 7, True, True, False),
            ('rough_inspection_passed', 'Rough Inspection Passed', 8, False, True, False),
        ),
    },
    'trim': {
        'name': 'Trim',
        'match': ('trim',),
        'items': (
            ('drywall_finished', 'Drywall Finished', 1, True, True, False),
            ('painting_ready', 'Painting Ready', 2, True, True, False),
            ('rough_approved', 'Rough Approved', 3, True, True, False),
            ('tug_approved', 'TUG Approved', 4, True, True, False),
            ('material_delivered', 'Material Delivered', 5, True, True, False),
            ('final_qc', 'Final QC', 6, True, True, False),
            ('final_electrical_inspection_passed', 'Final Electrical Inspection Passed', 7, False, True, False),
        ),
    },
}


def seed_work_order_statuses(status_model=None):
    """Idempotent: create default statuses only when the catalog is empty."""
    Status = status_model or WorkOrderStatus
    if Status.objects.exists():
        return 0
    created = 0
    for row in DEFAULT_WORK_ORDER_STATUSES:
        code, name, sequence, is_initial, is_terminal, req_insp, req_comp, description = row
        Status.objects.create(
            code=code,
            name=name,
            sequence=sequence,
            is_initial=is_initial,
            is_terminal=is_terminal,
            requires_inspection_ready=req_insp,
            requires_completion_ready=req_comp,
            is_active=True,
            description=description,
        )
        created += 1
    return created


def seed_work_order_progress_templates(
    *,
    category_model=None,
    template_model=None,
    item_model=None,
):
    """
    Create electrical-phase templates when matching Category rows exist and
    that category still has no template. Never overwrites custom items.
    """
    from crewsapp.models import Category as LiveCategory

    Category = category_model or LiveCategory
    Template = template_model or WorkOrderProgressTemplate
    Item = item_model or WorkOrderProgressItem
    created_templates = 0
    created_items = 0

    categories = list(Category.objects.all())
    for _key, spec in DEFAULT_PROGRESS_TEMPLATES.items():
        matches = [
            cat
            for cat in categories
            if any(token in (cat.name or '').lower() for token in spec['match'])
        ]
        if not matches:
            continue
        for category in matches:
            if Template.objects.filter(category=category).exists():
                continue
            template = Template.objects.create(
                name=spec['name'],
                category=category,
                is_active=True,
                is_expected_for_work_account=True,
                description=f'Default progress checklist for {category.name}.',
            )
            created_templates += 1
            for code, name, sequence, req_insp, req_comp, informational in spec['items']:
                Item.objects.create(
                    template=template,
                    code=code,
                    name=name,
                    sequence=sequence,
                    is_required_for_inspection=req_insp,
                    is_required_for_completion=req_comp,
                    is_informational=informational,
                    is_active=True,
                )
                created_items += 1
    return created_templates, created_items


def seed_work_order_defaults():
    statuses = seed_work_order_statuses()
    templates, items = seed_work_order_progress_templates()
    return {
        'statuses': statuses,
        'templates': templates,
        'items': items,
    }


def initial_status():
    status = (
        WorkOrderStatus.objects.filter(is_initial=True, is_active=True)
        .order_by('sequence')
        .first()
    )
    if status is None:
        raise ValidationError({
            'status': 'No initial Work Order status is configured for this company.',
        })
    return status


def resolve_progress_template_for_event(event: Event):
    if event is None or event.is_absence:
        return None
    category = getattr(getattr(event, 'crew', None), 'category', None)
    if category is None:
        return None
    return (
        WorkOrderProgressTemplate.objects.filter(
            category=category,
            is_active=True,
        )
        .prefetch_related(
            Prefetch(
                'items',
                queryset=WorkOrderProgressItem.objects.filter(is_active=True).order_by(
                    'sequence', 'id'
                ),
            )
        )
        .first()
    )


@transaction.atomic
def ensure_progress_checks(*, event, force_template=None):
    """
    Clone active template items onto the Event. Idempotent: existing checks
    are kept (including done state); only missing items are added.
    """
    if event is None or event.pk is None or event.is_absence or event.deleted:
        return []

    template = force_template or resolve_progress_template_for_event(event)
    if template is None:
        return list(event.progress_checks.select_related('item').all())

    existing = {
        check.item_id: check
        for check in WorkOrderProgressCheck.objects.filter(event=event)
    }
    created = []
    for item in template.items.filter(is_active=True).order_by('sequence', 'id'):
        if item.id in existing:
            continue
        created.append(
            WorkOrderProgressCheck.objects.create(
                event=event,
                item=item,
                is_done=False,
                source=WorkOrderProgressCheck.SOURCE_MANUAL,
            )
        )
    return list(event.progress_checks.select_related('item').order_by('item__sequence', 'id'))


@transaction.atomic
def ensure_initial_work_order_status(*, event, user=None, notes=''):
    """
    Assign Scheduled + first history row + progress checks.
    No-op for absences / soft-deleted. Idempotent if tracking already exists.
    """
    if event is None or event.pk is None:
        return None
    if event.is_absence or event.deleted:
        return None

    existing = (
        WorkOrderTracking.objects.select_for_update()
        .filter(event_id=event.pk)
        .first()
    )
    if existing is not None:
        ensure_progress_checks(event=event)
        return existing

    status = initial_status()
    now = timezone.now()
    if user is not None and getattr(user, 'is_authenticated', False):
        actor = user
    else:
        actor = getattr(event, 'created_by', None)
    note = (notes or '').strip()
    tracking = WorkOrderTracking.objects.create(
        event=event,
        current_status=status,
        status_changed_at=now,
        changed_by=actor,
        notes='',
    )
    WorkOrderStatusHistory.objects.create(
        event=event,
        from_status=None,
        to_status=status,
        changed_by=tracking.changed_by,
        changed_at=now,
        notes=note,
    )
    ensure_progress_checks(event=event)
    return tracking


def missing_progress_requirements(event: Event, *, for_inspection=False, for_completion=False):
    qs = (
        WorkOrderProgressCheck.objects.filter(event=event, is_done=False)
        .select_related('item')
        .order_by('item__sequence', 'id')
    )
    missing = []
    for check in qs:
        item = check.item
        if not item.is_active or item.is_informational:
            continue
        if for_inspection and item.is_required_for_inspection:
            missing.append(item)
        elif for_completion and item.is_required_for_completion:
            missing.append(item)
    return missing


def _raise_missing(missing, *, gate_label: str):
    if not missing:
        return
    names = [item.name for item in missing]
    raise ValidationError({
        'status': (
            f'Cannot move to {gate_label} while required progress items are pending: '
            + ', '.join(names)
            + '.'
        ),
        'missing_requirements': [
            {'id': item.id, 'code': item.code, 'name': item.name}
            for item in missing
        ],
    })


@transaction.atomic
def transition_work_order_status(*, event, status_code, notes='', user=None):
    """
    Flexible transition between active statuses, with inspection/completion gates.
    Does not auto-reset on schedule date changes.
    """
    if event is None or event.pk is None:
        raise ValidationError({'event': 'Work Order is required.'})
    if event.is_absence:
        raise ValidationError({'event': 'Absence entries do not use Work Order status.'})
    if event.deleted:
        raise ValidationError({'event': 'This Work Order is deleted.'})

    tracking = (
        WorkOrderTracking.objects.select_for_update()
        .select_related('current_status')
        .filter(event_id=event.pk)
        .first()
    )
    if tracking is None:
        tracking = ensure_initial_work_order_status(event=event, user=user)
    if tracking is None:
        raise ValidationError({'status': 'This Work Order has no status tracking.'})

    current = tracking.current_status
    target = WorkOrderStatus.objects.filter(code=status_code, is_active=True).first()
    if target is None:
        raise ValidationError({'status': 'Unknown or inactive Work Order status.'})
    if target.pk == current.pk:
        raise ValidationError({'status': 'The Work Order is already in that status.'})

    if target.requires_inspection_ready:
        _raise_missing(
            missing_progress_requirements(event, for_inspection=True),
            gate_label=target.name,
        )
    if target.requires_completion_ready or target.is_terminal:
        _raise_missing(
            missing_progress_requirements(event, for_completion=True),
            gate_label=target.name,
        )

    now = timezone.now()
    note = (notes or '').strip()
    actor = user if getattr(user, 'is_authenticated', False) else None
    tracking.current_status = target
    tracking.status_changed_at = now
    tracking.changed_by = actor
    tracking.notes = note
    tracking.save(
        update_fields=['current_status', 'status_changed_at', 'changed_by', 'notes']
    )
    WorkOrderStatusHistory.objects.create(
        event=event,
        from_status=current,
        to_status=target,
        changed_by=actor,
        changed_at=now,
        notes=note,
    )
    return tracking


@transaction.atomic
def set_progress_check(*, check, is_done, notes='', user=None):
    actor = user if getattr(user, 'is_authenticated', False) else None
    note = (notes or '').strip()
    check.is_done = bool(is_done)
    check.notes = note
    if check.is_done:
        check.completed_at = timezone.now()
        check.completed_by = actor
    else:
        check.completed_at = None
        check.completed_by = None
    check.save(
        update_fields=['is_done', 'notes', 'completed_at', 'completed_by']
    )
    return check


def get_work_order_tracking(event: Event):
    return (
        WorkOrderTracking.objects.select_related('current_status', 'changed_by')
        .filter(event_id=event.pk)
        .first()
    )


def list_active_statuses():
    return list(WorkOrderStatus.objects.filter(is_active=True).order_by('sequence', 'id'))


def suggest_material_delivered_from_transactions(event: Event):
    """
    Read-only helper for future UI: related documents that may imply material
    delivery. Does NOT mark progress checks automatically.
    """
    if event is None or event.pk is None:
        return {
            'can_suggest': False,
            'reason': 'no_event',
            'documents': [],
        }
    docs = (
        event.documents.filter(is_active=True)
        .select_related('document_type')
    )
    suggestions = []
    for doc in docs:
        type_code = getattr(doc.document_type, 'type_code', '') or ''
        status_code = ''
        try:
            tracking = doc.tracking
        except Exception:
            tracking = None
        if tracking is not None and tracking.current_status_id:
            status_code = tracking.current_status.code
        suggestions.append({
            'document_id': doc.id,
            'document_number': doc.document_number,
            'document_type': type_code,
            'status_code': status_code,
            'uses_status_tracking': bool(
                getattr(doc.document_type, 'uses_status_tracking', False)
            ),
        })
    return {
        'can_suggest': False,
        'reason': 'manual_confirmation_required',
        'message': (
            'Related transaction documents are listed for reference only. '
            'Material delivery is not marked automatically while quantities may remain pending.'
        ),
        'documents': suggestions,
    }


def work_account_status_summary(work_account):
    """
    Derived Work Account progress from expected templates + existing WOs.
    Never invents a separate WA status catalog.
    """
    expected_templates = list(
        WorkOrderProgressTemplate.objects.filter(
            is_active=True,
            is_expected_for_work_account=True,
            category__isnull=False,
        ).select_related('category')
    )
    events = list(
        Event.objects.filter(
            work_account=work_account,
            deleted=False,
            is_absence=False,
        )
        .select_related(
            'crew__category',
            'work_order_tracking__current_status',
        )
        .order_by('date', 'id')
    )

    by_category = {}
    for event in events:
        category = getattr(getattr(event, 'crew', None), 'category', None)
        if category is None:
            continue
        bucket = by_category.setdefault(category.id, {
            'category_id': category.id,
            'category_name': category.name,
            'work_orders': [],
            'has_terminal': False,
            'has_active': False,
        })
        tracking = getattr(event, 'work_order_tracking', None)
        status = tracking.current_status if tracking else None
        is_terminal = bool(status and status.is_terminal)
        bucket['work_orders'].append({
            'event_id': event.id,
            'title': event.title,
            'date': event.date.isoformat() if event.date else None,
            'status_code': status.code if status else None,
            'status_name': status.name if status else None,
            'is_terminal': is_terminal,
        })
        if is_terminal:
            bucket['has_terminal'] = True
        else:
            bucket['has_active'] = True

    phases = []
    expected_done = 0
    expected_total = 0
    for template in expected_templates:
        expected_total += 1
        category = template.category
        bucket = by_category.get(category.id)
        if bucket is None:
            phase_state = 'not_started'
            work_orders = []
        elif bucket['has_terminal'] and not bucket['has_active']:
            phase_state = 'completed'
            expected_done += 1
            work_orders = bucket['work_orders']
        elif bucket['work_orders']:
            phase_state = 'in_progress'
            work_orders = bucket['work_orders']
        else:
            phase_state = 'not_started'
            work_orders = []
        phases.append({
            'template_id': template.id,
            'template_name': template.name,
            'category_id': category.id,
            'category_name': category.name,
            'state': phase_state,
            'work_orders': work_orders,
        })

    # Extra WOs whose category is not in expected templates.
    expected_cat_ids = {t.category_id for t in expected_templates}
    extras = [
        bucket
        for cat_id, bucket in by_category.items()
        if cat_id not in expected_cat_ids
    ]

    if expected_total == 0:
        if not events:
            overall = 'not_started'
        elif all(
            getattr(getattr(e, 'work_order_tracking', None), 'current_status', None)
            and e.work_order_tracking.current_status.is_terminal
            for e in events
        ):
            overall = 'completed'
        else:
            overall = 'in_progress'
    elif expected_done == expected_total:
        overall = 'completed'
    elif expected_done == 0 and all(p['state'] == 'not_started' for p in phases):
        overall = 'not_started' if not events else 'in_progress'
    else:
        overall = 'in_progress'

    return {
        'work_account_id': work_account.id,
        'overall_state': overall,
        'expected_phases_total': expected_total,
        'expected_phases_completed': expected_done,
        'phases': phases,
        'additional_work_orders': extras,
        'note': (
            'Overall state is derived from expected phases with active progress '
            'templates. Completing only the Work Orders created so far does not '
            'mark the Work Account completed while expected phases are missing.'
        ),
    }
