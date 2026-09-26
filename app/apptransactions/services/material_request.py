"""
Este archivo contiene la lógica de alta y procesamiento lineal de solicitudes de materiales (Material Request, tipo MR) en el sistema JobRhythm.

En este servicio se definen funciones clave para:

- Generar y reservar el número secuencial de documento correspondiente al tipo MR, asegurando integridad transaccional.
- Recuperar el estado inicial válido para el tipo de documento MR, validando su existencia.
- Crear una solicitud de materiales (Material Request) a partir de los datos recibidos, incluyendo referencia a la cuenta de trabajo, orden de trabajo y detalle de los materiales a solicitar.
- Integrarse con el modelo de documentos y líneas de documento para registrar correctamente la solicitud en el sistema, siguiendo los procesos de negocio y trazabilidad definidos para los movimientos de material.

Este archivo centraliza la gestión de las solicitudes de materiales, desde su creación hasta su transición inicial de estatus, como parte del flujo operativo de control de inventario y abastecimiento en la plataforma.
"""

from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apptransactions.models import (
    Document,
    DocumentLine,
    DocumentSequence,
    DocumentStatus,
    DocumentTracking,
    DocumentTrackingHistory,
    DocumentType,
)

MR_TYPE_CODE = 'MR'


def allocate_document_number(document_type):
    """Reserva el siguiente número del tipo. Llamar dentro de transaction.atomic."""
    sequence, _created = DocumentSequence.objects.get_or_create(
        document_type=document_type,
    )
    sequence = DocumentSequence.objects.select_for_update().get(pk=sequence.pk)
    sequence.last_number += 1
    sequence.save(update_fields=['last_number'])
    return f'{document_type.type_code}-{sequence.last_number:06d}'


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


@transaction.atomic
def create_material_request(*, work_account, work_order, lines, notes, user):
    document_type = DocumentType.objects.filter(
        type_code=MR_TYPE_CODE,
        is_active=True,
    ).first()
    if document_type is None:
        raise ValidationError({'document_type': 'Material Request type (MR) is not configured.'})

    if work_order.work_account_id != work_account.id:
        raise ValidationError({
            'work_order': 'The work order does not belong to this work account.',
        })
    if getattr(work_order, 'deleted', False):
        raise ValidationError({'work_order': 'This work order is no longer active.'})
    if not lines:
        raise ValidationError({'lines': 'Add at least one material.'})

    merged = {}
    for line in lines:
        product = line['product']
        if not product.is_active:
            raise ValidationError({'lines': f'{product.name} is not active.'})
        quantity = Decimal(line['quantity'])
        if quantity <= 0:
            raise ValidationError({'lines': 'Quantity must be greater than zero.'})
        current = merged.get(product.id)
        if current is None:
            merged[product.id] = {'product': product, 'quantity': quantity}
        else:
            current['quantity'] += quantity

    # Available es informativo: no se reserva stock ni se rechaza por falta de inventario.
    initial = initial_status_for(document_type)
    document = Document(
        document_type=document_type,
        work_account=work_account,
        work_order=work_order,
        builder_id=work_account.builder_id,
        notes=(notes or '').strip() or None,
        created_by=user if getattr(user, 'is_authenticated', False) else None,
        document_number=allocate_document_number(document_type),
    )
    document.save()

    for item in merged.values():
        product = item['product']
        DocumentLine.objects.create(
            document=document,
            product=product,
            quantity=item['quantity'],
            unit=product.unit_default,
            unit_price=Decimal('0'),
            discount_percentage=Decimal('0'),
            pricing_rule=DocumentLine.PRICING_MANUAL,
        )

    now = timezone.now()
    DocumentTracking.objects.create(
        document=document,
        current_status=initial,
        status_changed_at=now,
        changed_by=document.created_by,
        notes='',
    )
    DocumentTrackingHistory.objects.create(
        document=document,
        from_status=None,
        to_status=initial,
        changed_by=document.created_by,
        changed_at=now,
        notes=(notes or '').strip(),
    )
    return document


@transaction.atomic
def update_material_request_lines(*, document, lines):
    """Cambia cantidades de un MR. Cantidad 0 quita el ítem. Debe quedar al menos uno."""
    locked = {
        line.id: line
        for line in DocumentLine.objects.select_for_update().filter(document=document)
    }
    if not locked:
        raise ValidationError({'lines': 'This request has no items.'})

    merged = {}
    for item in lines:
        line_id = item['id']
        if line_id not in locked:
            raise ValidationError({'lines': 'One of the items does not belong to this request.'})
        quantity = item['quantity']
        if quantity < 0:
            raise ValidationError({'lines': 'Quantity cannot be negative.'})
        merged[line_id] = quantity

    deletions = [locked[line_id] for line_id, quantity in merged.items() if quantity == 0]
    changes = [
        (locked[line_id], quantity)
        for line_id, quantity in merged.items()
        if quantity > 0 and locked[line_id].quantity != quantity
    ]
    if len(locked) - len(deletions) < 1:
        raise ValidationError({
            'lines': 'A material request must keep at least one item. Delete the request instead.',
        })

    for line, quantity in changes:
        line.quantity = quantity
        line.save()
    for line in deletions:
        line.delete()
    if deletions:
        document.calculate_totals()
    return document


def delete_material_request(*, document):
    """Un Material Request cerrado no se puede borrar."""
    tracking = (
        DocumentTracking.objects.select_related('current_status')
        .filter(document_id=document.pk)
        .first()
    )
    current = tracking.current_status if tracking else None
    if current is not None and current.code == 'closed':
        raise ValidationError({'status': 'A closed material request cannot be deleted.'})
    document.delete()
    return document


@transaction.atomic
def transition_material_request(*, document, status_code, notes, user):
    """
    Avanza o revierte un solo paso de sequence.

    sequence controla el flujo (Requested → Approved → Preparing → Delivered → Closed).
    Se puede volver al estado anterior, incluido salir de Closed. Los saltos se rechazan.
    """
    tracking = (
        DocumentTracking.objects.select_for_update()
        .select_related('current_status', 'document__document_type')
        .filter(document=document)
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
    tracking.current_status = target
    tracking.status_changed_at = now
    tracking.changed_by = user if getattr(user, 'is_authenticated', False) else None
    tracking.notes = note
    tracking.save(update_fields=['current_status', 'status_changed_at', 'changed_by', 'notes'])
    DocumentTrackingHistory.objects.create(
        document=document,
        from_status=current,
        to_status=target,
        changed_by=tracking.changed_by,
        changed_at=now,
        notes=note,
    )
    return document
