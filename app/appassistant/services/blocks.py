"""Structured block builders for JobRhythm Assistant responses."""

from __future__ import annotations

from typing import Any

from appassistant.contracts.response import (
    ALLOWED_ENTITY_TYPES,
    ALLOWED_ROUTE_KEYS,
    DEFAULT_CURRENCY,
    ROUTE_PATH_TEMPLATES,
)
from appassistant.services.money import as_money_str

# Re-export for callers that import path templates from blocks.
__all__ = [
    'ALLOWED_ENTITY_TYPES',
    'ALLOWED_ROUTE_KEYS',
    'ROUTE_PATH_TEMPLATES',
    'text_block',
    'kpi_block',
    'kpi_currency',
    'table_block',
    'bar_chart_block',
    'line_chart_block',
    'entity_link_block',
    'document_entity_link',
    'builder_entity_link',
    'clarification_text',
    'tool_source',
]


def text_block(*, block_id: str, text: str, title: str | None = None) -> dict[str, Any]:
    block: dict[str, Any] = {
        'type': 'text',
        'id': block_id,
        'text': text,
    }
    if title:
        block['title'] = title
    return block


def kpi_block(
    *,
    block_id: str,
    title: str,
    value: str,
    format: str = 'number',
    currency: str | None = None,
    subtitle: str | None = None,
) -> dict[str, Any]:
    block: dict[str, Any] = {
        'type': 'kpi',
        'id': block_id,
        'title': title,
        'value': value,
        'format': format,
    }
    if format == 'currency':
        block['currency'] = currency or DEFAULT_CURRENCY
    if subtitle:
        block['subtitle'] = subtitle
    return block


def kpi_currency(
    *,
    block_id: str,
    title: str,
    amount,
    currency: str | None = None,
    subtitle: str | None = None,
) -> dict[str, Any]:
    return kpi_block(
        block_id=block_id,
        title=title,
        value=as_money_str(amount),
        format='currency',
        currency=currency,
        subtitle=subtitle,
    )


def table_block(
    *,
    block_id: str,
    columns: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    title: str | None = None,
    pagination: dict[str, Any] | None = None,
) -> dict[str, Any]:
    block: dict[str, Any] = {
        'type': 'table',
        'id': block_id,
        'columns': columns,
        'rows': rows,
    }
    if title:
        block['title'] = title
    if pagination is not None:
        block['pagination'] = pagination
    return block


def bar_chart_block(
    *,
    block_id: str,
    labels: list[str],
    values: list[str],
    title: str | None = None,
    series_name: str | None = None,
) -> dict[str, Any]:
    if len(labels) != len(values):
        raise ValueError('bar_chart labels and values must have the same length.')
    block: dict[str, Any] = {
        'type': 'bar_chart',
        'id': block_id,
        'labels': labels,
        'values': values,
    }
    if title:
        block['title'] = title
    if series_name:
        block['series_name'] = series_name
    return block


def line_chart_block(
    *,
    block_id: str,
    labels: list[str],
    values: list[str],
    title: str | None = None,
    series_name: str | None = None,
) -> dict[str, Any]:
    if len(labels) != len(values):
        raise ValueError('line_chart labels and values must have the same length.')
    block: dict[str, Any] = {
        'type': 'line_chart',
        'id': block_id,
        'labels': labels,
        'values': values,
    }
    if title:
        block['title'] = title
    if series_name:
        block['series_name'] = series_name
    return block


def entity_link_block(
    *,
    block_id: str,
    entity_type: str,
    entity_id: int,
    route_key: str,
    label: str | None = None,
) -> dict[str, Any]:
    if entity_type not in ALLOWED_ENTITY_TYPES:
        raise ValueError(f'Unsupported entity_type: {entity_type}')
    if route_key not in ALLOWED_ROUTE_KEYS:
        raise ValueError(f'Unsupported route_key: {route_key}')
    template = ROUTE_PATH_TEMPLATES[route_key]
    path = template.format(id=entity_id)
    block: dict[str, Any] = {
        'type': 'entity_link',
        'id': block_id,
        'entity_type': entity_type,
        'entity_id': entity_id,
        'route_key': route_key,
        'path': path,
    }
    if label:
        block['label'] = label
    return block


def document_entity_link(*, document_id: int, label: str | None = None) -> dict[str, Any]:
    return entity_link_block(
        block_id=f'document-{document_id}',
        entity_type='document',
        entity_id=document_id,
        route_key='transactions-form',
        label=label or f'Document #{document_id}',
    )


def builder_entity_link(*, builder_id: int, label: str | None = None) -> dict[str, Any]:
    return entity_link_block(
        block_id=f'builder-{builder_id}',
        entity_type='builder',
        entity_id=builder_id,
        route_key='builder-view',
        label=label or f'Builder #{builder_id}',
    )


def clarification_text(*, block_id: str, message: str, candidates: list[dict] | None = None) -> dict[str, Any]:
    """Text block for closed-failure clarification (e.g. ambiguous vendor)."""
    text = message
    if candidates:
        lines = [f"- id={c.get('id')}: {c.get('name')}" for c in candidates]
        text = f"{message}\n" + '\n'.join(lines)
    return text_block(block_id=block_id, text=text, title='Clarification needed')


def tool_source(*, tool_name: str, row_count: int) -> dict[str, Any]:
    return {'type': 'tool', 'name': tool_name, 'row_count': row_count}
