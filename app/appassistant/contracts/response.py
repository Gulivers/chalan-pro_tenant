"""Structured response contract for JobRhythm Assistant (Level 1)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import UUID

from django.conf import settings


SCHEMA_VERSION = '1'

ALLOWED_BLOCK_TYPES = frozenset({
    'text',
    'kpi',
    'kpi_group',
    'table',
    'bar_chart',
    'line_chart',
    'donut_chart',
    'entity_link',
    'source',
})

ALLOWED_ENTITY_TYPES = frozenset({'document', 'builder'})
ALLOWED_ROUTE_KEYS = frozenset({
    'transactions-form',
    'builder-view',
})

# Canonical path templates for entity_link (frontend allowlist).
ROUTE_PATH_TEMPLATES = {
    'transactions-form': '/transactions/form?id={id}',
    'builder-view': '/builder/view/{id}',
}

# Spend definition for Level 1 tools (enforced in services.spend / tools).
# Keep in sync with appassistant.services.spend.SPEND_DEFINITION.
SPEND_DEFINITION = (
    'Net invoiced spending = active PINV Document.total_amount only; '
    'not gross, not returns (PRN), not PO/committed, '
    'not the Sales vs Purchases chart (is_purchase) criterion'
)

# Temporary default until tenant/document currency exists in JobRhythm.
DEFAULT_CURRENCY = 'USD'


def _default_timezone() -> str:
    return getattr(settings, 'TIME_ZONE', 'UTC') or 'UTC'


def build_stub_response(
    *,
    request_id: str | UUID,
    context: dict,
    message: str | None = None,
) -> dict:
    """
    Increment A stub: valid schema, no tools executed, no financial data.
    Kept for contract tests; production path uses build_assistant_response.
    """
    return build_assistant_response(
        request_id=request_id,
        message=message or 'Assistant ready. No tools executed in this increment.',
        blocks=[],
        sources=[],
        context=context,
        tools_executed=[],
        partial=False,
        router='none',
    )


def build_assistant_response(
    *,
    request_id: str | UUID,
    message: str,
    blocks: list | None = None,
    sources: list | None = None,
    context: dict | None = None,
    tools_executed: list | None = None,
    partial: bool = False,
    router: str = 'deterministic',
    currency: str | None = None,
    timezone: str | None = None,
) -> dict:
    """Build a Level-1 Assistant API response with spend_definition injected."""
    ctx = deepcopy(context) if context else {}
    ctx['spend_definition'] = SPEND_DEFINITION
    return {
        'schema_version': SCHEMA_VERSION,
        'message': message,
        'blocks': list(blocks or []),
        'sources': list(sources or []),
        'context': ctx,
        'meta': {
            'request_id': str(request_id),
            'partial': bool(partial),
            'currency': currency or DEFAULT_CURRENCY,
            'timezone': timezone or _default_timezone(),
            'router': router,
            'tools_executed': list(tools_executed or []),
        },
    }


def _expected_entity_path(route_key: str, entity_id: int) -> str | None:
    template = ROUTE_PATH_TEMPLATES.get(route_key)
    if not template:
        return None
    return template.format(id=entity_id)


def _validate_block(block: dict, index: int) -> list[str]:
    errors: list[str] = []
    prefix = f'blocks[{index}]'
    btype = block.get('type')

    if btype not in ALLOWED_BLOCK_TYPES:
        errors.append(f'{prefix}.type "{btype}" is not an allowed Level-1 block type.')
    if 'id' not in block or not isinstance(block.get('id'), str) or not block['id']:
        errors.append(f'{prefix}.id must be a non-empty string.')

    if btype == 'kpi':
        value = block.get('value')
        if not isinstance(value, str) or not value:
            errors.append(f'{prefix}.value must be a non-empty string (never float).')
        if not isinstance(block.get('format'), str) or not block.get('format'):
            errors.append(f'{prefix}.format is required.')
        if isinstance(value, float):
            errors.append(f'{prefix}.value must not be a float.')

    elif btype == 'table':
        if not isinstance(block.get('columns'), list):
            errors.append(f'{prefix}.columns must be a list.')
        if not isinstance(block.get('rows'), list):
            errors.append(f'{prefix}.rows must be a list.')

    elif btype in ('bar_chart', 'line_chart', 'donut_chart'):
        labels = block.get('labels')
        values = block.get('values')
        if not isinstance(labels, list):
            errors.append(f'{prefix}.labels must be a list.')
        if not isinstance(values, list):
            errors.append(f'{prefix}.values must be a list.')
        if isinstance(labels, list) and isinstance(values, list) and len(labels) != len(values):
            errors.append(f'{prefix}.labels and values must have the same length.')
        if isinstance(values, list):
            for vi, v in enumerate(values):
                if isinstance(v, float):
                    errors.append(f'{prefix}.values[{vi}] must not be a float.')

    elif btype == 'entity_link':
        et = block.get('entity_type')
        if et not in ALLOWED_ENTITY_TYPES:
            errors.append(
                f'{prefix}.entity_type must be one of {sorted(ALLOWED_ENTITY_TYPES)}.'
            )
        eid = block.get('entity_id')
        if not isinstance(eid, int) or isinstance(eid, bool) or eid < 1:
            errors.append(f'{prefix}.entity_id must be a positive integer.')
        route_key = block.get('route_key')
        if route_key not in ALLOWED_ROUTE_KEYS:
            errors.append(
                f'{prefix}.route_key must be one of {sorted(ALLOWED_ROUTE_KEYS)}.'
            )
        path = block.get('path')
        if not isinstance(path, str) or not path:
            errors.append(f'{prefix}.path must be a non-empty string.')
        elif (
            route_key in ROUTE_PATH_TEMPLATES
            and isinstance(eid, int)
            and not isinstance(eid, bool)
            and eid >= 1
        ):
            expected = _expected_entity_path(route_key, eid)
            if expected is not None and path != expected:
                errors.append(
                    f'{prefix}.path must match template for route_key '
                    f'("{expected}", got "{path}").'
                )

    elif btype == 'text':
        if 'text' in block and not isinstance(block.get('text'), str):
            errors.append(f'{prefix}.text must be a string.')

    return errors


def validate_response_payload(payload: Any) -> list[str]:
    """Return a list of validation errors; empty means valid."""
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ['Response must be an object.']

    if payload.get('schema_version') != SCHEMA_VERSION:
        errors.append(f'schema_version must be "{SCHEMA_VERSION}".')

    if not isinstance(payload.get('message'), str):
        errors.append('message must be a string.')

    blocks = payload.get('blocks')
    if not isinstance(blocks, list):
        errors.append('blocks must be a list.')
    else:
        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                errors.append(f'blocks[{i}] must be an object.')
                continue
            errors.extend(_validate_block(block, i))

    for key in ('sources',):
        if not isinstance(payload.get(key), list):
            errors.append(f'{key} must be a list.')

    if not isinstance(payload.get('context'), dict):
        errors.append('context must be an object.')

    meta = payload.get('meta')
    if not isinstance(meta, dict):
        errors.append('meta must be an object.')
    else:
        if not meta.get('request_id'):
            errors.append('meta.request_id is required.')
        if 'partial' in meta and not isinstance(meta['partial'], bool):
            errors.append('meta.partial must be a boolean.')

    return errors
