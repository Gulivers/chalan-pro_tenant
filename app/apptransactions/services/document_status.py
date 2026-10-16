"""
Status tracking compartido para DocumentType.uses_status_tracking.

Material Request sigue usando su API y reglas de stock propias; solo reutiliza
ensure_initial_tracking / transition_document_status para no duplicar la
escritura atómica de DocumentTracking + DocumentTrackingHistory.
"""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apptransactions.models import (
    Document,
    DocumentStatus,
    DocumentTracking,
    DocumentTrackingHistory,
)

# Semilla idempotente para tenants nuevos / migraciones. Tracking queda OFF.
DEFAULT_DOCUMENT_STATUS_SEEDS = {
    'PO': (
        ('draft', 'Draft', 1, True, False),
        ('submitted', 'Submitted', 2, False, False),
        ('approved', 'Approved', 3, False, False),
        ('ordered', 'Ordered', 4, False, False),
        ('closed', 'Closed', 5, False, True),
    ),
    'PK': (
        ('requested', 'Requested', 1, True, False),
        ('approved', 'Approved', 2, False, False),
        ('preparing', 'Preparing', 3, False, False),
        ('picked', 'Picked', 4, False, False),
        ('closed', 'Closed', 5, False, True),
    ),
    'PR': (
        ('requested', 'Requested', 1, True, False),
        ('approved', 'Approved', 2, False, False),
        ('ordered', 'Ordered', 3, False, False),
        ('closed', 'Closed', 4, False, True),
    ),
}


def initial_status_for(document_type):
    status = (
        DocumentStatus.objects.filter(
            document_type=document_type,
            is_initial=True,
            is_active=True,
        )
        .order_by('sequence')
        .first()
    )
    if status is None:
        raise ValidationError({'status': 'This document type has no initial status.'})
    return status


def seed_default_document_statuses(document_type_model=None, document_status_model=None):
    """
    Crea estados predeterminados para PO/PK/PR si faltan.

    Idempotente: get_or_create por (document_type, code). No actualiza filas
    existentes (los admins del tenant conservan personalizaciones).
    No activa uses_status_tracking.
    """
    from apptransactions.models import DocumentStatus as LiveStatus
    from apptransactions.models import DocumentType as LiveType

    DocumentType = document_type_model or LiveType
    DocumentStatusModel = document_status_model or LiveStatus
    created = 0
    for type_code, rows in DEFAULT_DOCUMENT_STATUS_SEEDS.items():
        document_type = DocumentType.objects.filter(type_code=type_code).first()
        if document_type is None:
            continue
        # Si el tenant ya tiene estados para este tipo, no tocar nada.
        if DocumentStatusModel.objects.filter(document_type=document_type).exists():
            continue
        for code, name, sequence, is_initial, is_terminal in rows:
            DocumentStatusModel.objects.create(
                document_type=document_type,
                code=code,
                name=name,
                sequence=sequence,
                is_initial=is_initial,
                is_terminal=is_terminal,
                is_active=True,
            )
            created += 1
    return created


@transaction.atomic
def ensure_initial_tracking(*, document, user=None, notes='', force=False):
    """
    Crea DocumentTracking + primera entrada de historial si corresponde.

    - Sin uses_status_tracking y sin force: no-op.
    - Si ya hay tracking: no-op (idempotente; evita carrera con MR/signal).
    """
    if document is None or document.pk is None:
        return None

    doc_type = document.document_type
    if not force and not getattr(doc_type, 'uses_status_tracking', False):
        return None

    existing = (
        DocumentTracking.objects.select_for_update()
        .filter(document_id=document.pk)
        .first()
    )
    if existing is not None:
        return existing

    initial = initial_status_for(doc_type)
    now = timezone.now()
    actor = user if getattr(user, 'is_authenticated', False) else None
    note = (notes or '').strip()
    tracking = DocumentTracking.objects.create(
        document=document,
        current_status=initial,
        status_changed_at=now,
        changed_by=actor,
        notes='',
    )
    DocumentTrackingHistory.objects.create(
        document=document,
        from_status=None,
        to_status=initial,
        changed_by=actor,
        changed_at=now,
        notes=note,
    )
    return tracking


@transaction.atomic
def transition_document_status(*, document, status_code, notes='', user=None):
    """
    Avanza o revierte un solo paso de sequence (mismo contrato que MR).

    Actualiza DocumentTracking y escribe DocumentTrackingHistory en la misma
    transacción atómica, con select_for_update sobre el tracking.
    """
    if document is None or document.pk is None:
        raise ValidationError({'document': 'Document is required.'})

    tracking = (
        DocumentTracking.objects.select_for_update()
        .select_related('current_status', 'document__document_type')
        .filter(document_id=document.pk)
        .first()
    )
    if tracking is None:
        raise ValidationError({'status': 'This document has no tracking record.'})

    current = tracking.current_status
    target = DocumentStatus.objects.filter(
        document_type_id=document.document_type_id,
        code=status_code,
        is_active=True,
    ).first()
    if target is None:
        raise ValidationError({'status': 'Unknown status for this document type.'})
    if abs(target.sequence - current.sequence) != 1:
        raise ValidationError({
            'status': (
                f'Cannot move from {current.name} to {target.name}. '
                'Only the next or previous status is allowed.'
            ),
        })

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
    DocumentTrackingHistory.objects.create(
        document=document,
        from_status=current,
        to_status=target,
        changed_by=actor,
        changed_at=now,
        notes=note,
    )
    return document


def get_document_tracking(document: Document):
    return (
        DocumentTracking.objects.select_related('current_status', 'changed_by')
        .filter(document_id=document.pk)
        .first()
    )


def next_previous_statuses(document: Document):
    tracking = get_document_tracking(document)
    if tracking is None or tracking.current_status_id is None:
        return None, None
    current = tracking.current_status
    qs = DocumentStatus.objects.filter(
        document_type_id=document.document_type_id,
        is_active=True,
    )
    nxt = qs.filter(sequence=current.sequence + 1).first()
    prev = qs.filter(sequence=current.sequence - 1).first()
    return nxt, prev
