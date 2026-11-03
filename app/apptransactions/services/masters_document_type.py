# -*- coding: utf-8 -*-
"""
Carga de DocumentType + DocumentStatus desde masters_document_type.json.

No usa loaddata con PKs fijos: en tenants nuevos la migración 0008 crea MR y,
por el setval del serial, suele ocupar id=2 — el mismo pk que el fixture asigna
a PO. Eso hace fallar loaddata con UniqueViolation y deja el tenant sin masters.

Esta carga es idempotente y resuelve tipos por type_code (y statuses por code).
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

from django.conf import settings

from apptransactions.models import DocumentStatus, DocumentType

logger = logging.getLogger(__name__)

# Alineado con generate_masters_document_type_fixture / migración 0008.
EXCLUDED_TYPE_CODES = frozenset(
    getattr(DocumentType, 'PROTECTED_TYPE_CODES', frozenset({'MR'}))
)

FIXTURE_RELATIVE = os.path.join(
    'apptransactions',
    'fixtures',
    'masters_document_type.json',
)

DOCUMENT_TYPE_FIELD_NAMES = frozenset(
    f.name
    for f in DocumentType._meta.fields
    if f.name not in ('id',)
)


def default_fixture_path() -> str:
    return os.path.join(settings.BASE_DIR, FIXTURE_RELATIVE)


def _load_fixture_objects(fixture_path: str) -> list[dict[str, Any]]:
    with open(fixture_path, encoding='utf-8') as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f'Fixture inválido (se esperaba lista): {fixture_path}')
    return data


def seed_tenant_document_masters(
    fixture_path: str | None = None,
    *,
    seed_statuses_fallback: bool = True,
    seed_work_orders: bool = True,
) -> dict[str, int]:
    """
    Siembra DocumentType/DocumentStatus del fixture maestro en el schema actual.

    Debe llamarse dentro de schema_context(tenant). Idempotente.
    """
    path = fixture_path or default_fixture_path()
    result = {
        'types_created': 0,
        'types_updated': 0,
        'statuses_created': 0,
        'statuses_skipped': 0,
        'fallback_statuses': 0,
        'types_skipped_protected': 0,
    }

    if not os.path.exists(path):
        logger.warning('masters_document_type fixture no encontrado: %s', path)
        return result

    objects = _load_fixture_objects(path)
    type_rows = [
        obj
        for obj in objects
        if obj.get('model') == 'apptransactions.documenttype'
    ]
    status_rows = [
        obj
        for obj in objects
        if obj.get('model') == 'apptransactions.documentstatus'
    ]

    # pk del fixture → type_code (para remapeo de FKs de DocumentStatus)
    fixture_pk_to_code: dict[Any, str] = {}
    live_by_code: dict[str, DocumentType] = {}

    for obj in type_rows:
        fields = dict(obj.get('fields') or {})
        type_code = fields.get('type_code')
        if not type_code:
            continue
        fixture_pk = obj.get('pk')
        if fixture_pk is not None:
            fixture_pk_to_code[fixture_pk] = type_code

        if type_code in EXCLUDED_TYPE_CODES:
            result['types_skipped_protected'] += 1
            existing = DocumentType.objects.filter(type_code=type_code).first()
            if existing:
                live_by_code[type_code] = existing
            continue

        defaults = {
            key: value
            for key, value in fields.items()
            if key in DOCUMENT_TYPE_FIELD_NAMES and key != 'type_code'
        }
        doc_type, created = DocumentType.objects.get_or_create(
            type_code=type_code,
            defaults=defaults,
        )
        if created:
            result['types_created'] += 1
        else:
            # No sobrescribir personalizaciones del tenant.
            result['types_updated'] += 0
        live_by_code[type_code] = doc_type

    # Solo sembrar statuses del fixture cuando el tipo aún no tiene ninguno.
    # Evita mezclar workflows (fixture vs seed_default) y choques de sequence /
    # is_initial cuando el tenant ya tiene estados.
    types_already_with_statuses = set(
        DocumentStatus.objects.filter(
            document_type_id__in=[dt.pk for dt in live_by_code.values()]
        ).values_list('document_type_id', flat=True)
    )

    for obj in status_rows:
        fields = dict(obj.get('fields') or {})
        code = fields.get('code')
        if not code:
            continue

        raw_type_ref = fields.get('document_type')
        if isinstance(raw_type_ref, str) and not str(raw_type_ref).isdigit():
            type_code = raw_type_ref
        else:
            type_code = fixture_pk_to_code.get(raw_type_ref)

        if not type_code or type_code in EXCLUDED_TYPE_CODES:
            result['statuses_skipped'] += 1
            continue

        doc_type = live_by_code.get(type_code) or DocumentType.objects.filter(
            type_code=type_code
        ).first()
        if doc_type is None:
            result['statuses_skipped'] += 1
            continue

        if doc_type.pk in types_already_with_statuses:
            result['statuses_skipped'] += 1
            continue

        DocumentStatus.objects.create(
            document_type=doc_type,
            code=code,
            name=fields.get('name') or code,
            sequence=fields.get('sequence') or 1,
            is_initial=bool(fields.get('is_initial', False)),
            is_terminal=bool(fields.get('is_terminal', False)),
            is_active=bool(fields.get('is_active', True)),
        )
        result['statuses_created'] += 1

    if seed_statuses_fallback:
        from apptransactions.services.document_status import (
            seed_default_document_statuses,
        )

        result['fallback_statuses'] = seed_default_document_statuses() or 0

    if seed_work_orders:
        from appschedule.services.work_order_status import seed_work_order_defaults

        wo = seed_work_order_defaults() or {}
        result['wo_statuses'] = int(wo.get('statuses') or 0)
        result['wo_templates'] = int(wo.get('templates') or 0)
        result['wo_items'] = int(wo.get('items') or 0)

    return result
