"""Build validated conversation state from an executed tool turn."""

from __future__ import annotations

from typing import Any

from django.conf import settings

from appassistant.services.conversation_state import (
    DOMAIN_PURCHASE_DOCUMENTS,
    METRIC_NET_INVOICED_SPEND,
    empty_state,
    validate_state,
)
from appassistant.services.vendors import (
    AmbiguousVendorError,
    VendorNotFoundError,
    resolve_vendor,
)
from appassistant.tools.registry import get_default_registry


def build_state_after_tool(
    *,
    tool_name: str,
    params: dict[str, Any] | None,
    tool_result: dict[str, Any] | None = None,
    base_state: dict[str, Any] | None = None,
    filter_operations: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Snapshot structured state after a successful tool execution.

    Prefers absolute dates from validated tool params so open conversations
    do not silently shift when the calendar day changes.
    """
    raw = dict(params or {})
    if base_state:
        try:
            state = validate_state(base_state)
        except Exception:
            state = empty_state()
        filters = dict(state.get('filters') or {})
    else:
        state = empty_state(
            domain=DOMAIN_PURCHASE_DOCUMENTS,
            metric=METRIC_NET_INVOICED_SPEND,
        )
        filters = {}

    state['tool'] = tool_name
    state['domain'] = DOMAIN_PURCHASE_DOCUMENTS
    state['metric'] = METRIC_NET_INVOICED_SPEND

    normalized = _normalize_params(tool_name, raw)

    date_from = normalized.get('date_from')
    date_to = normalized.get('date_to')
    if date_from is not None and date_to is not None:
        filters['date_from'] = str(date_from)
        filters['date_to'] = str(date_to)
        filters['timezone'] = getattr(settings, 'TIME_ZONE', 'UTC') or 'UTC'
        period = raw.get('period') or filters.get('period_label')
        if isinstance(period, str) and period.strip():
            filters['period_label'] = period.strip()
        elif not filters.get('period_label'):
            filters['period_label'] = 'custom_range'

    if normalized.get('months') is not None:
        filters['months'] = normalized['months']
        filters.setdefault('period_label', 'last_n_months')

    if 'min_amount' in normalized:
        if normalized['min_amount'] is None:
            filters.pop('min_amount', None)
        else:
            filters['min_amount'] = str(normalized['min_amount'])
    elif not base_state:
        filters.pop('min_amount', None)

    vendors = _resolve_vendors_from_params(raw, normalized)
    if vendors is not None:
        if vendors:
            filters['vendors'] = vendors
            filters['vendor_ids'] = [v['id'] for v in vendors]
        else:
            filters.pop('vendors', None)
            filters.pop('vendor_ids', None)

    if tool_name in (
        'purchases_by_vendor',
        'compare_purchases_by_vendor',
        'top_vendors_by_spending',
    ) and not raw.get('vendor') and not raw.get('vendor_id') and not raw.get('vendor_ids'):
        filters.pop('vendors', None)
        filters.pop('vendor_ids', None)

    if tool_name == 'compare_vendor_spending_periods':
        comparison = raw.get('comparison_period') or filters.get('comparison_period')
        if comparison:
            filters['comparison_period'] = comparison
    else:
        filters.pop('comparison_period', None)

    state['filters'] = filters

    if normalized.get('limit') is not None:
        state['limit'] = normalized['limit']
    elif normalized.get('top_n') is not None:
        state['limit'] = normalized['top_n']

    state['presentation'] = _presentation_for_tool(tool_name, tool_result)

    summary: dict[str, Any] = {}
    if tool_result:
        summary['row_count'] = int(tool_result.get('row_count') or 0)
        summary['partial'] = bool(tool_result.get('partial', False))
        kpi_value = _first_kpi_value(tool_result.get('blocks') or [])
        if kpi_value is not None:
            summary['kpi_value'] = kpi_value
    state['last_result_summary'] = summary
    state['last_filter_operations'] = list(filter_operations or [])[:20]
    state['active_entities'] = {
        'vendor_ids': list(filters.get('vendor_ids') or []),
        'document_ids': _document_ids_from_blocks(tool_result),
    }
    return validate_state(state)


def _normalize_params(tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
    reg = get_default_registry()
    tool = reg.get(tool_name)
    if tool is None:
        return dict(params)
    try:
        return tool.validate_params(params)
    except Exception:
        return dict(params)


def _resolve_vendors_from_params(
    raw_params: dict[str, Any],
    normalized: dict[str, Any],
) -> list[dict[str, Any]] | None:
    if 'vendor_ids' in raw_params and isinstance(raw_params['vendor_ids'], list):
        out: list[dict[str, Any]] = []
        for vid in raw_params['vendor_ids']:
            if not isinstance(vid, int) or isinstance(vid, bool):
                continue
            try:
                builder = resolve_vendor(vendor_id=vid)
            except (VendorNotFoundError, AmbiguousVendorError):
                continue
            out.append({'id': builder.pk, 'name': builder.name})
        return out

    vendor_id = normalized.get('vendor_id')
    vendor_name = normalized.get('vendor') or raw_params.get('vendor')
    if vendor_id is None and not vendor_name:
        if 'vendor' in raw_params or 'vendor_id' in raw_params:
            return []
        return None
    try:
        builder = resolve_vendor(name=vendor_name, vendor_id=vendor_id)
    except (VendorNotFoundError, AmbiguousVendorError):
        return None
    return [{'id': builder.pk, 'name': builder.name}]


def _presentation_for_tool(tool_name: str, tool_result: dict[str, Any] | None) -> list[str]:
    blocks = (tool_result or {}).get('blocks') or []
    types = {b.get('type') for b in blocks if isinstance(b, dict)}
    presentation = ['message']
    for key in ('kpi', 'kpi_group', 'table', 'bar_chart', 'line_chart', 'donut_chart'):
        if key in types:
            presentation.append('kpi' if key == 'kpi_group' else key)
    presentation.append('sources')
    seen: set[str] = set()
    ordered: list[str] = []
    for item in presentation:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _first_kpi_value(blocks: list) -> str | None:
    for block in blocks:
        if isinstance(block, dict) and block.get('type') == 'kpi':
            value = block.get('value')
            if isinstance(value, str):
                return value
    return None


def _document_ids_from_blocks(tool_result: dict[str, Any] | None) -> list[int]:
    if not tool_result:
        return []
    ids: list[int] = []
    for block in tool_result.get('blocks') or []:
        if not isinstance(block, dict):
            continue
        if block.get('type') == 'entity_link' and block.get('entity_type') == 'document':
            eid = block.get('entity_id')
            if isinstance(eid, int) and not isinstance(eid, bool) and eid >= 1:
                if eid not in ids:
                    ids.append(eid)
    return ids[:50]
