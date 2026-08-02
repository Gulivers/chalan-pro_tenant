"""
Deterministic filter merge for conversational continuity (Level 1).

The planner (LLM or deterministic) proposes filter_operations.
Django applies them here; the result is the only state worth persisting.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from appassistant.services.conversation_state import (
    ALLOWED_DOMAINS,
    ALLOWED_METRICS,
    ALLOWED_PRESENTATION,
    ALLOWED_TOOLS,
    ConversationStateError,
    DOMAIN_PURCHASE_DOCUMENTS,
    METRIC_NET_INVOICED_SPEND,
    empty_state,
    validate_state,
)

ALLOWED_OPERATIONS = frozenset({
    'set',
    'add',
    'remove',
    'clear',
    'replace_period',
    'compare_with_period',
    'change_tool',
    'change_presentation',
    'change_domain',
    'reset',
    'clarify',
})

# Fields that FilterMerger can mutate under filters{}.
MUTABLE_FILTER_FIELDS = frozenset({
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

# Filters kept when switching among purchase spend tools.
PURCHASE_COMPATIBLE_FILTERS = frozenset({
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

# Tools that do not use vendor filters (drop vendor_* on change_tool).
TOOLS_WITHOUT_VENDOR_FILTER = frozenset({
    'purchases_by_vendor',
    'compare_purchases_by_vendor',
    'top_vendors_by_spending',
})


@dataclass
class FilterOperation:
    field: str
    operation: str
    value: Any = None

    @classmethod
    def from_dict(cls, raw: Any) -> 'FilterOperation':
        if not isinstance(raw, dict):
            raise ConversationStateError('filter operation must be an object.')
        field_name = raw.get('field')
        operation = raw.get('operation')
        if not isinstance(field_name, str) or not field_name.strip():
            raise ConversationStateError('filter operation.field is required.')
        if not isinstance(operation, str) or operation not in ALLOWED_OPERATIONS:
            raise ConversationStateError(
                f'Unsupported filter operation "{operation}".'
            )
        return cls(
            field=field_name.strip(),
            operation=operation,
            value=raw.get('value'),
        )


@dataclass
class MergeResult:
    state: dict[str, Any]
    inherited: bool = False
    clarification: str | None = None
    needs_clarification: bool = False
    applied_operations: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and not self.needs_clarification


def merge_conversation_state(
    previous: dict[str, Any] | None,
    *,
    operations: list[FilterOperation | dict[str, Any]] | None = None,
    intent: str | None = None,
    tool: str | None = None,
    domain: str | None = None,
    metric: str | None = None,
    state_expired: bool = False,
    presentation: list[str] | None = None,
    group_by: str | None = None,
    sort: str | None = None,
    limit: int | None = None,
    last_result_summary: dict[str, Any] | None = None,
) -> MergeResult:
    """
    Apply structured filter operations onto previous validated state.

    When ``state_expired`` is True, previous filters are not inherited
    (equivalent to starting from empty_state for filter purposes).
    """
    ops = [_coerce_op(op) for op in (operations or [])]

    # Global reset / clarify short-circuit.
    if any(op.operation == 'reset' for op in ops):
        state = empty_state(
            domain=domain or DOMAIN_PURCHASE_DOCUMENTS,
            metric=metric or METRIC_NET_INVOICED_SPEND,
        )
        if tool:
            state['tool'] = tool
        if presentation is not None:
            state['presentation'] = presentation
        state['last_filter_operations'] = [_op_to_dict(op) for op in ops]
        try:
            return MergeResult(
                state=validate_state(state),
                inherited=False,
                applied_operations=state['last_filter_operations'],
            )
        except ConversationStateError as exc:
            return MergeResult(state=empty_state(), error=str(exc))

    clarify_ops = [op for op in ops if op.operation == 'clarify']
    if clarify_ops:
        base = empty_state() if state_expired else _safe_previous(previous)
        message = None
        for op in clarify_ops:
            if isinstance(op.value, str) and op.value.strip():
                message = op.value.strip()
                break
        return MergeResult(
            state=base,
            inherited=not state_expired and bool(previous),
            clarification=message or 'Please clarify your request.',
            needs_clarification=True,
            applied_operations=[_op_to_dict(op) for op in ops],
        )

    if state_expired or not previous:
        state = empty_state(
            domain=domain or DOMAIN_PURCHASE_DOCUMENTS,
            metric=metric or METRIC_NET_INVOICED_SPEND,
        )
        inherited = False
    else:
        try:
            state = validate_state(previous)
        except ConversationStateError:
            state = empty_state(
                domain=domain or DOMAIN_PURCHASE_DOCUMENTS,
                metric=metric or METRIC_NET_INVOICED_SPEND,
            )
            inherited = False
        else:
            inherited = bool(state.get('filters') or state.get('tool'))

    # Domain change drops incompatible filters.
    target_domain = domain or state.get('domain') or DOMAIN_PURCHASE_DOCUMENTS
    if target_domain not in ALLOWED_DOMAINS:
        return MergeResult(
            state=empty_state(),
            error=f'Unsupported domain "{target_domain}".',
        )
    if state.get('domain') != target_domain:
        state = empty_state(domain=target_domain, metric=metric or METRIC_NET_INVOICED_SPEND)
        inherited = False
    else:
        state['domain'] = target_domain

    if metric is not None:
        if metric not in ALLOWED_METRICS:
            return MergeResult(state=state, error=f'Unsupported metric "{metric}".')
        state['metric'] = metric

    if tool is not None:
        if tool not in ALLOWED_TOOLS:
            return MergeResult(state=state, error=f'Unsupported tool "{tool}".')
        state = _apply_tool_change(state, tool)

    if presentation is not None:
        state['presentation'] = presentation
    if group_by is not None:
        state['group_by'] = group_by
    if sort is not None:
        state['sort'] = sort
    if limit is not None:
        state['limit'] = limit

    applied: list[dict[str, Any]] = []
    for op in ops:
        err = _apply_operation(state, op)
        if err:
            return MergeResult(
                state=validate_state(state) if state else empty_state(),
                inherited=inherited,
                error=err,
                applied_operations=applied,
            )
        applied.append(_op_to_dict(op))

    # Intent is observational for audit; optional mapping of known intents.
    _ = intent

    if last_result_summary is not None:
        state['last_result_summary'] = last_result_summary

    state['last_filter_operations'] = applied
    _sync_active_entities(state)

    try:
        validated = validate_state(state)
    except ConversationStateError as exc:
        return MergeResult(state=empty_state(), inherited=inherited, error=str(exc))

    return MergeResult(
        state=validated,
        inherited=inherited,
        applied_operations=applied,
    )


def filters_for_tool(state: dict[str, Any], tool_name: str) -> dict[str, Any]:
    """
    Project conversational filters into tool params (no DB / no vendor resolve).

    Period labels are passed through; absolute dates are preferred when present.
    """
    validated = validate_state(state)
    filters = validated.get('filters') or {}
    params: dict[str, Any] = {}

    vendor_ids = filters.get('vendor_ids') or []
    vendors = filters.get('vendors') or []
    if len(vendor_ids) == 1:
        params['vendor_id'] = vendor_ids[0]
        if vendors:
            params['vendor'] = vendors[0].get('name')
    elif len(vendor_ids) > 1:
        params['vendor_ids'] = list(vendor_ids)

    if 'min_amount' in filters:
        params['min_amount'] = filters['min_amount']

    if filters.get('date_from') and filters.get('date_to'):
        params['date_from'] = filters['date_from']
        params['date_to'] = filters['date_to']
    elif filters.get('period_label'):
        params['period'] = filters['period_label']

    if 'months' in filters:
        params['months'] = filters['months']

    if validated.get('limit') is not None:
        params['limit'] = validated['limit']

    presentation = set(validated.get('presentation') or [])
    wants_chart = bool(presentation & {'bar_chart', 'line_chart', 'donut_chart'})
    wants_table = 'table' in presentation
    if tool_name in (
        'purchases_by_vendor',
        'compare_purchases_by_vendor',
        'spending_timeseries',
    ):
        # Presentation-only follow-ups set these explicitly.
        if wants_chart or wants_table:
            params['include_chart'] = wants_chart
            params['include_table'] = wants_table or not wants_chart
        else:
            params['include_chart'] = True
            params['include_table'] = True

    if tool_name == 'compare_vendor_spending_periods':
        comparison = filters.get('comparison_period')
        if comparison:
            params['comparison_period'] = deepcopy(comparison)
        if filters.get('period_label'):
            params['period'] = filters['period_label']
        if 'min_amount' in filters:
            params['min_amount'] = filters['min_amount']

    return params


def _coerce_op(op: FilterOperation | dict[str, Any]) -> FilterOperation:
    if isinstance(op, FilterOperation):
        return op
    return FilterOperation.from_dict(op)


def _op_to_dict(op: FilterOperation) -> dict[str, Any]:
    return {
        'field': op.field,
        'operation': op.operation,
        'value': op.value,
    }


def _safe_previous(previous: dict[str, Any] | None) -> dict[str, Any]:
    try:
        return validate_state(previous)
    except ConversationStateError:
        return empty_state()


def _apply_tool_change(state: dict[str, Any], tool: str) -> dict[str, Any]:
    previous_tool = state.get('tool')
    state['tool'] = tool
    if previous_tool == tool:
        return state

    filters = state.get('filters') or {}
    kept = {
        key: value
        for key, value in filters.items()
        if key in PURCHASE_COMPATIBLE_FILTERS
    }
    if tool in TOOLS_WITHOUT_VENDOR_FILTER:
        kept.pop('vendor_ids', None)
        kept.pop('vendors', None)
    # Comparison period only meaningful for the compare-periods tool.
    if tool != 'compare_vendor_spending_periods':
        kept.pop('comparison_period', None)
    state['filters'] = kept
    return state


def _apply_operation(state: dict[str, Any], op: FilterOperation) -> str | None:
    if op.operation == 'change_tool':
        if not isinstance(op.value, str) or op.value not in ALLOWED_TOOLS:
            return f'Unsupported tool "{op.value}".'
        _apply_tool_change(state, op.value)
        return None

    if op.operation == 'change_domain':
        if not isinstance(op.value, str) or op.value not in ALLOWED_DOMAINS:
            return f'Unsupported domain "{op.value}".'
        if state.get('domain') != op.value:
            new_state = empty_state(domain=op.value, metric=state.get('metric') or METRIC_NET_INVOICED_SPEND)
            state.clear()
            state.update(new_state)
        return None

    if op.operation == 'change_presentation':
        if not isinstance(op.value, list) or not all(isinstance(x, str) for x in op.value):
            return 'presentation value must be a list of strings.'
        unknown = [p for p in op.value if p not in ALLOWED_PRESENTATION]
        if unknown:
            return f'Unsupported presentation types: {unknown}.'
        state['presentation'] = list(op.value)
        return None

    if op.operation == 'replace_period':
        return _replace_period(state, op.value, compare=False)

    if op.operation == 'compare_with_period':
        return _replace_period(state, op.value, compare=True)

    if op.field in ('group_by', 'sort', 'limit', 'tool', 'metric', 'domain', 'presentation'):
        return _apply_top_level(state, op)

    if op.field not in MUTABLE_FILTER_FIELDS and op.field not in (
        'vendor',
        'period',
        'amount',
        'min_amount',
    ):
        return f'Unsupported filter field "{op.field}".'

    field = _canonicalize_field(op.field)
    filters = state.setdefault('filters', {})

    if op.operation == 'clear' or (op.operation == 'remove' and op.value is None):
        _clear_field(filters, field)
        return None

    if op.operation == 'remove':
        return _remove_value(filters, field, op.value)

    if op.operation == 'add':
        return _add_value(filters, field, op.value)

    if op.operation == 'set':
        return _set_value(filters, field, op.value)

    return f'Unsupported operation "{op.operation}" for field "{op.field}".'


def _canonicalize_field(field: str) -> str:
    if field in ('vendor', 'vendors', 'vendor_id', 'vendor_ids'):
        return 'vendors'
    if field in ('period', 'period_label'):
        return 'period'
    if field in ('amount', 'min_amount'):
        return 'min_amount'
    return field


def _apply_top_level(state: dict[str, Any], op: FilterOperation) -> str | None:
    if op.operation not in ('set', 'clear', 'remove'):
        return f'Operation "{op.operation}" is not valid for {op.field}.'
    if op.operation in ('clear', 'remove') and op.value is None:
        state[op.field] = None if op.field != 'presentation' else ['message', 'kpi', 'sources']
        return None
    if op.field == 'tool':
        if not isinstance(op.value, str) or op.value not in ALLOWED_TOOLS:
            return f'Unsupported tool "{op.value}".'
        _apply_tool_change(state, op.value)
        return None
    if op.field == 'metric':
        if op.value not in ALLOWED_METRICS:
            return f'Unsupported metric "{op.value}".'
        state['metric'] = op.value
        return None
    if op.field == 'domain':
        return _apply_operation(
            state,
            FilterOperation(field='domain', operation='change_domain', value=op.value),
        )
    if op.field == 'presentation':
        return _apply_operation(
            state,
            FilterOperation(field='presentation', operation='change_presentation', value=op.value),
        )
    if op.field == 'limit':
        if not isinstance(op.value, int) or isinstance(op.value, bool) or op.value < 1:
            return 'limit must be a positive integer.'
        state['limit'] = op.value
        return None
    if op.field in ('group_by', 'sort'):
        if op.value is not None and not isinstance(op.value, str):
            return f'{op.field} must be a string or null.'
        state[op.field] = op.value
        return None
    return None


def _replace_period(state: dict[str, Any], value: Any, *, compare: bool) -> str | None:
    if not isinstance(value, dict):
        return 'period value must be an object with period_label/date_from/date_to.'
    label = value.get('period_label') or value.get('label')
    date_from = value.get('date_from')
    date_to = value.get('date_to')
    if not isinstance(date_from, str) or not isinstance(date_to, str):
        return 'period value requires date_from and date_to strings (already resolved).'
    if not isinstance(label, str) or not label.strip():
        return 'period value requires period_label.'

    filters = state.setdefault('filters', {})
    period_obj = {
        'period_label': label.strip(),
        'date_from': date_from.strip(),
        'date_to': date_to.strip(),
    }
    tz = value.get('timezone')
    if isinstance(tz, str) and tz.strip():
        period_obj['timezone'] = tz.strip()

    if compare:
        # Keep primary period; attach comparison. Do not overwrite primary.
        if not filters.get('date_from') or not filters.get('date_to'):
            return 'Cannot compare periods without a primary period in state.'
        filters['comparison_period'] = period_obj
        # Dedicated auditable compare op (D6); not two ad-hoc tool calls.
        state['tool'] = 'compare_vendor_spending_periods'
        return None

    filters['period_label'] = period_obj['period_label']
    filters['date_from'] = period_obj['date_from']
    filters['date_to'] = period_obj['date_to']
    if 'timezone' in period_obj:
        filters['timezone'] = period_obj['timezone']
    filters.pop('comparison_period', None)
    if 'months' in value and isinstance(value['months'], int):
        filters['months'] = value['months']
    elif period_obj['period_label'] not in (
        'last_n_months',
        'last_six_months',
        'last_3_months',
    ):
        filters.pop('months', None)
    return None


def _clear_field(filters: dict[str, Any], field: str) -> None:
    if field == 'vendors':
        filters.pop('vendor_ids', None)
        filters.pop('vendors', None)
        return
    if field == 'period':
        for key in (
            'period_label',
            'date_from',
            'date_to',
            'timezone',
            'comparison_period',
            'months',
        ):
            filters.pop(key, None)
        return
    if field == 'min_amount':
        filters.pop('min_amount', None)
        return
    filters.pop(field, None)


def _set_value(filters: dict[str, Any], field: str, value: Any) -> str | None:
    if field == 'vendors':
        return _set_vendors(filters, value, replace=True)
    if field == 'min_amount':
        if value is None:
            filters.pop('min_amount', None)
            return None
        if not isinstance(value, (str, int)) or isinstance(value, bool):
            return 'min_amount must be a money string.'
        filters['min_amount'] = str(value).strip()
        return None
    if field == 'period':
        return _replace_period({'filters': filters}, value, compare=False)
    if field == 'months':
        if not isinstance(value, int) or isinstance(value, bool) or not (1 <= value <= 12):
            return 'months must be an integer in [1..12].'
        filters['months'] = value
        return None
    if field == 'comparison_period':
        filters['comparison_period'] = value
        return None
    filters[field] = value
    return None


def _add_value(filters: dict[str, Any], field: str, value: Any) -> str | None:
    if field == 'vendors':
        return _set_vendors(filters, value, replace=False)
    if field == 'min_amount':
        # "Also over $X" → set/replace minimum (single-valued).
        return _set_value(filters, field, value)
    return f'add is not supported for field "{field}".'


def _remove_value(filters: dict[str, Any], field: str, value: Any) -> str | None:
    if field == 'vendors':
        remove_ids: set[int] = set()
        if isinstance(value, int) and not isinstance(value, bool):
            remove_ids.add(value)
        elif isinstance(value, dict) and isinstance(value.get('id'), int):
            remove_ids.add(value['id'])
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, int) and not isinstance(item, bool):
                    remove_ids.add(item)
                elif isinstance(item, dict) and isinstance(item.get('id'), int):
                    remove_ids.add(item['id'])
        else:
            return 'remove vendor requires id or list of ids.'
        vendor_ids = [vid for vid in (filters.get('vendor_ids') or []) if vid not in remove_ids]
        vendors = [
            v for v in (filters.get('vendors') or [])
            if v.get('id') not in remove_ids
        ]
        if vendor_ids:
            filters['vendor_ids'] = vendor_ids
            filters['vendors'] = vendors
        else:
            filters.pop('vendor_ids', None)
            filters.pop('vendors', None)
        return None
    if field == 'min_amount':
        filters.pop('min_amount', None)
        return None
    if field == 'period':
        _clear_field(filters, 'period')
        return None
    return f'remove is not supported for field "{field}".'


def _set_vendors(filters: dict[str, Any], value: Any, *, replace: bool) -> str | None:
    incoming = _coerce_vendors(value)
    if incoming is None:
        return 'vendor value must include id and name (resolved by Django).'
    if replace:
        filters['vendors'] = incoming
        filters['vendor_ids'] = [v['id'] for v in incoming]
        return None
    existing = {
        v['id']: v
        for v in (filters.get('vendors') or [])
        if isinstance(v, dict) and isinstance(v.get('id'), int)
    }
    for vendor in incoming:
        existing[vendor['id']] = vendor
    merged = list(existing.values())
    filters['vendors'] = merged
    filters['vendor_ids'] = [v['id'] for v in merged]
    return None


def _coerce_vendors(value: Any) -> list[dict[str, Any]] | None:
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list) or not value:
        return None
    out: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            return None
        vid = item.get('id')
        name = item.get('name')
        if not isinstance(vid, int) or isinstance(vid, bool) or vid < 1:
            return None
        if not isinstance(name, str) or not name.strip():
            return None
        out.append({'id': vid, 'name': name.strip()[:255]})
    return out


def _sync_active_entities(state: dict[str, Any]) -> None:
    filters = state.get('filters') or {}
    state['active_entities'] = {
        'vendor_ids': list(filters.get('vendor_ids') or []),
        'document_ids': list(
            (state.get('active_entities') or {}).get('document_ids') or []
        ),
    }
