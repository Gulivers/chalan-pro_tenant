"""
Structured conversational state for JobRhythm Assistant (Level 1).

The LLM / client never author the persisted state. Django validates and stores
only allowlisted fields after tool execution.
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import timedelta
from typing import Any

from django.utils import timezone

STATE_SCHEMA_VERSION = '1'
DOMAIN_PURCHASE_DOCUMENTS = 'purchase_documents'
METRIC_NET_INVOICED_SPEND = 'net_invoiced_spend'

# Retention / limits (product decisions D2).
STATE_INACTIVITY_TTL = timedelta(hours=24)
CONVERSATION_RETENTION = timedelta(days=14)
MAX_TURN_COUNT = 30
MAX_STATE_JSON_BYTES = 16_384

ALLOWED_DOMAINS = frozenset({DOMAIN_PURCHASE_DOCUMENTS})
ALLOWED_METRICS = frozenset({METRIC_NET_INVOICED_SPEND})
ALLOWED_TOOLS = frozenset({
    'list_purchase_transactions',
    'sum_purchase_spending',
    'purchases_by_vendor',
    'compare_purchases_by_vendor',
    'top_vendors_by_spending',
    'spending_timeseries',
    'compare_vendor_spending_periods',
})
ALLOWED_PRESENTATION = frozenset({
    'message',
    'kpi',
    'table',
    'bar_chart',
    'line_chart',
    'sources',
    'entity_link',
})

# Fields that may appear under state["filters"].
FILTER_KEYS = frozenset({
    'vendor_ids',
    'vendors',
    'min_amount',
    'period_label',
    'date_from',
    'date_to',
    'timezone',
    'comparison_period',
    'months',
})


class ConversationStateError(ValueError):
    """Invalid or oversized conversational state."""


def empty_state(
    *,
    domain: str = DOMAIN_PURCHASE_DOCUMENTS,
    metric: str = METRIC_NET_INVOICED_SPEND,
) -> dict[str, Any]:
    return {
        'domain': domain,
        'metric': metric,
        'tool': None,
        'filters': {},
        'group_by': None,
        'sort': None,
        'limit': None,
        'presentation': ['message', 'kpi', 'sources'],
        'active_entities': {'vendor_ids': [], 'document_ids': []},
        'last_result_summary': {},
        'last_filter_operations': [],
    }


def state_json_size(state: dict[str, Any]) -> int:
    return len(json.dumps(state, separators=(',', ':'), default=str).encode('utf-8'))


def validate_state(state: Any) -> dict[str, Any]:
    """Return a normalized deep copy or raise ConversationStateError."""
    if state is None:
        return empty_state()
    if not isinstance(state, dict):
        raise ConversationStateError('state must be an object.')

    out = empty_state()
    domain = state.get('domain') or DOMAIN_PURCHASE_DOCUMENTS
    metric = state.get('metric') or METRIC_NET_INVOICED_SPEND
    if domain not in ALLOWED_DOMAINS:
        raise ConversationStateError(f'Unsupported domain "{domain}".')
    if metric not in ALLOWED_METRICS:
        raise ConversationStateError(f'Unsupported metric "{metric}".')
    out['domain'] = domain
    out['metric'] = metric

    tool = state.get('tool')
    if tool is not None:
        if not isinstance(tool, str) or tool not in ALLOWED_TOOLS:
            raise ConversationStateError(f'Unsupported tool "{tool}".')
        out['tool'] = tool

    filters = state.get('filters') or {}
    if not isinstance(filters, dict):
        raise ConversationStateError('filters must be an object.')
    out['filters'] = _normalize_filters(filters)

    for key in ('group_by', 'sort'):
        value = state.get(key)
        if value is not None and not isinstance(value, str):
            raise ConversationStateError(f'{key} must be a string or null.')
        out[key] = value

    limit = state.get('limit')
    if limit is not None:
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            raise ConversationStateError('limit must be a positive integer or null.')
        out['limit'] = limit

    presentation = state.get('presentation')
    if presentation is None:
        presentation = out['presentation']
    if not isinstance(presentation, list) or not all(isinstance(x, str) for x in presentation):
        raise ConversationStateError('presentation must be a list of strings.')
    unknown = [p for p in presentation if p not in ALLOWED_PRESENTATION]
    if unknown:
        raise ConversationStateError(f'Unsupported presentation types: {unknown}.')
    out['presentation'] = list(presentation)

    entities = state.get('active_entities') or {}
    if not isinstance(entities, dict):
        raise ConversationStateError('active_entities must be an object.')
    out['active_entities'] = {
        'vendor_ids': _normalize_id_list(entities.get('vendor_ids')),
        'document_ids': _normalize_id_list(entities.get('document_ids')),
    }

    summary = state.get('last_result_summary') or {}
    if not isinstance(summary, dict):
        raise ConversationStateError('last_result_summary must be an object.')
    out['last_result_summary'] = _sanitize_summary(summary)

    ops = state.get('last_filter_operations') or []
    if not isinstance(ops, list):
        raise ConversationStateError('last_filter_operations must be a list.')
    # Keep a short audit trail of ops (no free text prompts).
    out['last_filter_operations'] = ops[:20]

    if state_json_size(out) > MAX_STATE_JSON_BYTES:
        raise ConversationStateError(
            f'state exceeds {MAX_STATE_JSON_BYTES} bytes after normalization.'
        )
    return out


def _normalize_filters(filters: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in filters.items():
        if key not in FILTER_KEYS or value is None:
            continue
        if key == 'vendor_ids':
            out[key] = _normalize_id_list(value)
        elif key == 'vendors':
            out[key] = _normalize_vendors(value)
        elif key == 'min_amount':
            out[key] = _normalize_money_str(value)
        elif key in ('period_label', 'date_from', 'date_to', 'timezone'):
            if not isinstance(value, str) or not value.strip():
                raise ConversationStateError(f'{key} must be a non-empty string.')
            out[key] = value.strip()
        elif key == 'months':
            if not isinstance(value, int) or isinstance(value, bool) or not (1 <= value <= 12):
                raise ConversationStateError('months must be an integer in [1..12].')
            out[key] = value
        elif key == 'comparison_period':
            out[key] = _normalize_comparison_period(value)
    return out


def _normalize_id_list(value: Any) -> list[int]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ConversationStateError('id list must be a list of positive integers.')
    out: list[int] = []
    for item in value:
        if not isinstance(item, int) or isinstance(item, bool) or item < 1:
            raise ConversationStateError('ids must be positive integers.')
        if item not in out:
            out.append(item)
    return out


def _normalize_vendors(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ConversationStateError('vendors must be a list.')
    out: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ConversationStateError('each vendor must be an object.')
        vid = item.get('id')
        name = item.get('name')
        if not isinstance(vid, int) or isinstance(vid, bool) or vid < 1:
            raise ConversationStateError('vendor.id must be a positive integer.')
        if not isinstance(name, str) or not name.strip():
            raise ConversationStateError('vendor.name must be a non-empty string.')
        out.append({'id': vid, 'name': name.strip()[:255]})
    return out


def _normalize_money_str(value: Any) -> str:
    if isinstance(value, str):
        text = value.strip()
    else:
        text = str(value)
    # Structural check only; Decimal coercion happens in tools.
    if not text:
        raise ConversationStateError('min_amount must be a non-empty money string.')
    return text


def _normalize_comparison_period(value: Any) -> dict[str, str] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ConversationStateError('comparison_period must be an object or null.')
    label = value.get('period_label')
    date_from = value.get('date_from')
    date_to = value.get('date_to')
    for field, raw in (
        ('period_label', label),
        ('date_from', date_from),
        ('date_to', date_to),
    ):
        if not isinstance(raw, str) or not raw.strip():
            raise ConversationStateError(
                f'comparison_period.{field} must be a non-empty string.'
            )
    out = {
        'period_label': label.strip(),
        'date_from': date_from.strip(),
        'date_to': date_to.strip(),
    }
    tz = value.get('timezone')
    if tz is not None:
        if not isinstance(tz, str) or not tz.strip():
            raise ConversationStateError('comparison_period.timezone must be a string.')
        out['timezone'] = tz.strip()
    return out


def _sanitize_summary(summary: dict[str, Any]) -> dict[str, Any]:
    """Keep only small, non-sensitive summary keys."""
    allowed = {
        'row_count',
        'kpi_value',
        'document_count',
        'vendor_count',
        'partial',
    }
    out: dict[str, Any] = {}
    for key in allowed:
        if key not in summary:
            continue
        value = summary[key]
        if isinstance(value, bool) or value is None:
            out[key] = value
        elif isinstance(value, int) and not isinstance(value, bool):
            out[key] = value
        elif isinstance(value, str):
            out[key] = value[:64]
    return out


def is_state_reusable(
    *,
    is_active: bool,
    last_activity_at,
    turn_count: int,
    now=None,
) -> bool:
    """
    Whether previous filters may be inherited.

    Expired / inactive / over turn cap → do not inherit automatically.
    """
    if not is_active:
        return False
    if turn_count >= MAX_TURN_COUNT:
        return False
    if last_activity_at is None:
        return False
    current = now or timezone.now()
    return (current - last_activity_at) <= STATE_INACTIVITY_TTL


def compact_state_for_planner(state: dict[str, Any] | None) -> dict[str, Any]:
    """
    Limited summary handed to a future LLM planner (C4).
    Never includes prompts, blocks, or raw result payloads.
    """
    validated = validate_state(state)
    filters = validated.get('filters') or {}
    vendors = filters.get('vendors') or []
    active_vendor = vendors[0] if len(vendors) == 1 else None
    return {
        'active_domain': validated.get('domain'),
        'active_metric': validated.get('metric'),
        'active_tool': validated.get('tool'),
        'active_vendor': active_vendor,
        'active_vendors': vendors,
        'active_period': {
            'label': filters.get('period_label'),
            'date_from': filters.get('date_from'),
            'date_to': filters.get('date_to'),
            'timezone': filters.get('timezone'),
        },
        'active_filters': {
            k: filters[k]
            for k in ('min_amount', 'months', 'vendor_ids')
            if k in filters
        },
        'presentation': validated.get('presentation'),
        'last_result': deepcopy(validated.get('last_result_summary') or {}),
    }
