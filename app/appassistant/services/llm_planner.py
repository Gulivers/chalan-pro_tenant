"""
LLMToolRouter / planner for JobRhythm Assistant (Increment C4).

Uses OpenAI gpt-4.1-mini (configurable) to propose intent + filter_operations.
Django remains the source of truth: allowlists, vendor resolve, periods,
permissions, and tool execution are never delegated to the model.
"""

from __future__ import annotations

import json
import logging
import re
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from django.conf import settings
from django.utils import timezone

from appassistant.services.conversation_state import (
    ALLOWED_PRESENTATION,
    ALLOWED_TOOLS,
    compact_state_for_planner,
)
from appassistant.services.continuity_planner import resolved_period_value
from appassistant.services.filter_merger import ALLOWED_OPERATIONS, FilterOperation
from appassistant.services.periods import PeriodValidationError, resolve_period
from appassistant.services.spend import SPEND_DEFINITION, SPEND_METRIC_LABEL
from appassistant.services.vendors import (
    AmbiguousVendorError,
    VendorNotFoundError,
    resolve_vendor,
)
from appassistant.tools.registry import get_default_registry

logger = logging.getLogger('appassistant.llm')

# Params the model may propose for a brand-new query.
# Vendor names/labels only for entities; date_* accepted as ISO after Django validate.
_LLM_PARAM_KEYS = frozenset({
    'vendor',
    'min_amount',
    'period',
    'months',
    'limit',
    'top_n',
    'include_chart',
    'include_table',
    'date_from',
    'date_to',
})


@dataclass
class LLMPlan:
    ok: bool = False
    intent: str = ''
    is_new_query: bool = False
    tool: str | None = None
    operations: list[FilterOperation] = field(default_factory=list)
    params: dict[str, Any] = field(default_factory=dict)
    clarification: str | None = None
    needs_clarification: bool = False
    start_over: bool = False
    presentation: list[str] | None = None
    error: str | None = None
    model: str = ''
    # Safe subset for audit (never full prompts / completions).
    audit: dict[str, Any] = field(default_factory=dict)


def llm_planner_enabled() -> bool:
    flag = getattr(settings, 'ASSISTANT_LLM_ENABLED', False)
    if flag not in (True, 'True', 'true', '1', 1):
        return False
    key = (getattr(settings, 'OPENAI_API_KEY', None) or '').strip()
    return bool(key)


def llm_planner_primary_enabled() -> bool:
    """
    LLM-first orchestration (Fase 1).

    Requires ASSISTANT_LLM_PRIMARY plus a usable LLM (enabled + API key).
    When False, DeterministicRouter remains first authority (legacy).
    """
    if not llm_planner_enabled():
        return False
    flag = getattr(settings, 'ASSISTANT_LLM_PRIMARY', False)
    return flag in (True, 'True', 'true', '1', 1)


def plan_with_llm(
    message: str,
    *,
    previous_state: dict[str, Any] | None,
    state_expired: bool = False,
    page_context: dict[str, Any] | None = None,
) -> LLMPlan:
    """
    Call OpenAI and return a sanitized plan.

    On any failure returns LLMPlan(ok=False) so the orchestrator can fall back.
    """
    if not llm_planner_enabled():
        return LLMPlan(ok=False, error='llm_disabled')

    model = getattr(settings, 'ASSISTANT_LLM_MODEL', 'gpt-4.1-mini') or 'gpt-4.1-mini'
    compact = compact_state_for_planner(None if state_expired else previous_state)
    tools_catalog = _tools_catalog()
    tz_name = getattr(settings, 'TIME_ZONE', 'UTC') or 'UTC'
    today_iso = timezone.localdate().isoformat()

    system = _system_prompt(today_iso=today_iso, timezone_name=tz_name)
    user_payload = {
        'user_message': (message or '').strip()[:2000],
        'conversation_state': compact,
        'state_expired': bool(state_expired),
        'today': today_iso,
        'timezone': tz_name,
        'page_context': {
            k: (page_context or {}).get(k)
            for k in ('view', 'route_name', 'entity_type', 'entity_id')
        },
        'available_tools': tools_catalog,
        'allowed_operations': sorted(ALLOWED_OPERATIONS),
        'allowed_periods': [
            'today',
            'yesterday',
            'this_week',
            'last_week',
            'this_month',
            'month_to_date',
            'calendar_month',
            'last_month',
            'previous_calendar_month',
            'previous_2_calendar_months',
            'previous_3_calendar_months',
            'this_quarter',
            'last_quarter',
            'this_year',
            'year_to_date',
            'last_n_months',
            'last_six_months',
        ],
        'temporal_contract': {
            'prefer_period_labels_for': 'common fixed periods in allowed_periods',
            'use_date_from_date_to_for': (
                'variable natural-language spans (e.g. last 3 weeks) as ISO YYYY-MM-DD'
            ),
            'date_bounds': 'inclusive calendar dates in timezone',
            'ambiguous_relative': 'clarify; do not invent dates',
        },
    }

    try:
        raw_text = _call_openai(system=system, user_payload=user_payload, model=model)
        data = json.loads(raw_text)
    except Exception as exc:
        logger.warning('assistant.llm_planner_failed error=%s', type(exc).__name__)
        return LLMPlan(ok=False, error='llm_call_failed', model=model)

    if not isinstance(data, dict):
        return LLMPlan(ok=False, error='llm_invalid_json', model=model)

    try:
        return _sanitize_plan(data, model=model)
    except Exception as exc:
        logger.warning('assistant.llm_plan_sanitize_failed error=%s', type(exc).__name__)
        return LLMPlan(ok=False, error='llm_sanitize_failed', model=model)


def _call_openai(*, system: str, user_payload: dict[str, Any], model: str) -> str:
    from openai import OpenAI

    timeout = int(getattr(settings, 'ASSISTANT_LLM_TIMEOUT_SECONDS', 30) or 30)
    max_tokens = int(getattr(settings, 'ASSISTANT_LLM_MAX_TOKENS', 800) or 800)
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        timeout=timeout,
    )
    completion = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=max_tokens,
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': system},
            {
                'role': 'user',
                'content': json.dumps(user_payload, ensure_ascii=True, default=str),
            },
        ],
    )
    content = completion.choices[0].message.content if completion.choices else None
    if not content or not isinstance(content, str):
        raise ValueError('Empty LLM content')
    return content


def _system_prompt(*, today_iso: str, timezone_name: str) -> str:
    tool_names = ', '.join(sorted(ALLOWED_TOOLS))
    return f"""You are the JobRhythm Assistant planner (Level 1, read-only spend analytics).
Users ask in natural language; they do not know tool names, period labels, or internal schemas.
You interpret intent and propose a tool + typed params. Django validates and executes.
Return ONLY a JSON object (no markdown) with this shape:
{{
  "intent": "string",
  "is_new_query": boolean,
  "start_over": boolean,
  "tool": "tool_name or null",
  "params": {{
    "vendor": "name",
    "min_amount": "1500.00",
    "period": "this_month",
    "months": 6,
    "date_from": "YYYY-MM-DD",
    "date_to": "YYYY-MM-DD"
  }},
  "filter_operations": [{{"field": "vendor|min_amount|period|tool|presentation", "operation": "set|add|remove|clear|replace_period|compare_with_period|change_tool|change_presentation|reset|clarify", "value": ...}}],
  "presentation": ["message","kpi","table","bar_chart","sources"] or null,
  "clarification": "short question or null"
}}

Temporal contract (hybrid):
- Product today={today_iso}, timezone={timezone_name}. Compute relative dates from that today.
- For common fixed periods, prefer period labels from allowed_periods
  (this_month, last_month, this_week, last_week, year_to_date, …).
- For variable natural-language spans with no matching label (e.g. "last three weeks",
  "últimas 3 semanas", "from June 1 to June 20"), set date_from and date_to as inclusive
  ISO dates YYYY-MM-DD. Do not invent a fake period label for those.
- this_month / month_to_date = month start through today (not the full calendar month).
- Ambiguous time ("recently", "around May", "hace poco") → clarification; do not invent dates.
- Do not send only one of date_from/date_to. Inclusive span must be ≤ 366 days.
- When using date_from/date_to, omit period/months unless a label clearly also applies.

Rules:
- Metric is always Net invoiced spending (active PINV only). Spend definition: {SPEND_DEFINITION}
- User-facing metric label: {SPEND_METRIC_LABEL}
- Allowed tools: {tool_names}
- NEVER invent SQL, code, tenant IDs, user IDs, or numeric vendor/document IDs.
- Prefer vendor NAMES in params/operations; Django will resolve IDs.
- Vendor is optional for sum_purchase_spending and list_purchase_transactions.
  "How much did we spend this month?" → tool sum_purchase_spending, params {{"period": "this_month"}} (no vendor).
  "¿Cuánto gasté en las últimas tres semanas?" → sum_purchase_spending with date_from/date_to
  covering the last 21 days ending today (no vendor).
- "Compare purchases by supplier for the last six months." → compare_purchases_by_vendor
  with months=6 (or period last_n_months / last_six_months).
- "Compare purchases by supplier for the last three weeks." /
  "Compara compras por proveedor en las últimas tres semanas." →
  compare_purchases_by_vendor with date_from/date_to for the last 21 days ending today.
  Do NOT invent months for week-based spans; months is only for month windows.
- is_new_query=true when the user starts a different complete question with enough params.
- is_new_query=false for follow-ups that refine/replace/remove filters or change presentation/tool.
- Explicit new vendor name in a full question → replace (is_new_query=true or set vendor), do not keep the previous vendor.
- "include X too" / "also X" → operation add on vendor.
- "any vendor" → clear vendor.
- "only those over $X" → set min_amount.
- "include all amounts" → clear min_amount.
- "what about last month" / "previous calendar month" → replace_period with period_label last_month
  (full previous calendar month; no absolute dates needed).
- "two previous calendar months" → replace_period with period_label previous_2_calendar_months
  (the two full calendar months before the current month; current month excluded).
- Follow-up with a variable span → replace_period value {{"date_from":"...","date_to":"..."}}.
- "compare with last month" → compare_with_period + tool compare_vendor_spending_periods.
- "Graph spending/purchases for this month" → tool spending_timeseries with
  params {{"period": "this_month", "months": 1}} (never omit months for that tool
  unless period or an explicit date range is set).
- "Graph spending for the last N months" → spending_timeseries with months=N.
- "show the documents" → change_tool to list_purchase_transactions, inherit filters.
- "graph it" / "as a table" → change_presentation only.
- "start over" / "new question" → start_over=true.
- If ambiguous (multiple vendors for "its"), set clarification and operation clarify; do not pick silently.
- If the domain is outside purchase spend (crews/jobs/etc.), clarification explaining it is not available; tool=null.
- Do not include prompts, secrets, or chain-of-thought in the JSON.
"""


def _tools_catalog() -> list[dict[str, str]]:
    reg = get_default_registry()
    out = []
    for name in reg.names():
        tool = reg.get(name)
        if tool is None:
            continue
        out.append({
            'name': tool.name,
            'description': (tool.description or '')[:400],
        })
    return out


def _sanitize_plan(data: dict[str, Any], *, model: str) -> LLMPlan:
    intent = data.get('intent') if isinstance(data.get('intent'), str) else ''
    intent = intent.strip()[:64]
    start_over = bool(data.get('start_over'))
    is_new_query = bool(data.get('is_new_query'))
    clarification = data.get('clarification')
    if clarification is not None and not isinstance(clarification, str):
        clarification = None
    if isinstance(clarification, str):
        clarification = clarification.strip()[:500] or None

    tool = data.get('tool')
    if tool is not None:
        if not isinstance(tool, str) or tool not in ALLOWED_TOOLS:
            tool = None

    presentation = data.get('presentation')
    if presentation is not None:
        if not isinstance(presentation, list) or not all(isinstance(x, str) for x in presentation):
            presentation = None
        else:
            presentation = [p for p in presentation if p in ALLOWED_PRESENTATION]
            if not presentation:
                presentation = None

    params = _sanitize_params(data.get('params') or {})
    operations: list[FilterOperation] = []
    raw_ops = data.get('filter_operations') or []
    if isinstance(raw_ops, list):
        for item in raw_ops[:20]:
            op = _sanitize_operation(item)
            if op is not None:
                operations.append(op)

    needs_clarification = bool(clarification) or any(
        op.operation == 'clarify' for op in operations
    )
    if needs_clarification and not clarification:
        for op in operations:
            if op.operation == 'clarify' and isinstance(op.value, str):
                clarification = op.value
                break
        clarification = clarification or 'Please clarify your request.'

    audit = {
        'intent': intent,
        'is_new_query': is_new_query,
        'start_over': start_over,
        'tool': tool or '',
        'ops_count': len(operations),
        'has_clarification': bool(clarification),
        'param_keys': sorted(params.keys()),
        'model': model,
    }

    if start_over:
        return LLMPlan(
            ok=True,
            intent=intent or 'start_over',
            start_over=True,
            model=model,
            audit=audit,
        )

    if needs_clarification:
        return LLMPlan(
            ok=True,
            intent=intent or 'clarify',
            needs_clarification=True,
            clarification=clarification,
            tool=tool,
            operations=operations,
            model=model,
            audit=audit,
        )

    if not tool and not operations:
        return LLMPlan(
            ok=True,
            intent=intent or 'unsupported',
            needs_clarification=True,
            clarification=clarification or (
                'I could not map that to a supported spend query. '
                'Try asking about purchase invoices, vendor spending, or a period comparison.'
            ),
            model=model,
            audit=audit,
        )

    return LLMPlan(
        ok=True,
        intent=intent or ('new_query' if is_new_query else 'follow_up'),
        is_new_query=is_new_query,
        tool=tool,
        operations=operations,
        params=params,
        presentation=presentation,
        model=model,
        audit=audit,
    )


def _sanitize_params(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {}
    out: dict[str, Any] = {}
    for key in _LLM_PARAM_KEYS:
        if key in ('date_from', 'date_to'):
            continue
        if key not in raw or raw[key] is None or raw[key] == '':
            continue
        value = raw[key]
        if key == 'vendor':
            if isinstance(value, str) and value.strip():
                out['vendor'] = value.strip()[:255]
        elif key == 'min_amount':
            if isinstance(value, (str, int)) and not isinstance(value, bool):
                out['min_amount'] = str(value).strip()
        elif key == 'period':
            if isinstance(value, str) and value.strip():
                out['period'] = value.strip().lower()[:64]
        elif key == 'months':
            if isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 12:
                out['months'] = value
        elif key in ('limit', 'top_n'):
            if isinstance(value, int) and not isinstance(value, bool) and value >= 1:
                out[key] = value
        elif key in ('include_chart', 'include_table'):
            if isinstance(value, bool):
                out[key] = value
    # Explicit ISO range: accepted only after Django period validation.
    # Never accept vendor_id / vendor_ids from the model as authority.
    if raw.get('date_from') not in (None, '') or raw.get('date_to') not in (None, ''):
        try:
            start, end = resolve_period(
                date_from=raw.get('date_from'),
                date_to=raw.get('date_to'),
            )
            out['date_from'] = start.isoformat()
            out['date_to'] = end.isoformat()
        except PeriodValidationError:
            pass
    return out


def _sanitize_operation(raw: Any) -> FilterOperation | None:
    if not isinstance(raw, dict):
        return None
    field = raw.get('field')
    operation = raw.get('operation')
    if not isinstance(field, str) or not field.strip():
        return None
    if not isinstance(operation, str) or operation not in ALLOWED_OPERATIONS:
        return None
    field = field.strip()
    value = raw.get('value')

    if operation == 'clarify':
        if not isinstance(value, str) or not value.strip():
            value = 'Please clarify your request.'
        return FilterOperation(field=field, operation=operation, value=value.strip()[:500])

    if operation == 'reset':
        return FilterOperation(field='*', operation='reset', value=None)

    if field in ('vendor', 'vendors', 'vendor_id', 'vendor_ids') and operation in (
        'set',
        'add',
        'remove',
    ):
        resolved = _resolve_vendor_value(value, operation=operation)
        if resolved is None and operation != 'remove':
            return None
        if isinstance(resolved, dict) and resolved.get('clarify'):
            return FilterOperation(
                field='vendor',
                operation='clarify',
                value=resolved['clarify'],
            )
        return FilterOperation(field='vendor', operation=operation, value=resolved)

    if operation in ('replace_period', 'compare_with_period'):
        period_val = _normalize_period_value(value)
        if period_val is None:
            return None
        return FilterOperation(field='period', operation=operation, value=period_val)

    if operation == 'change_tool':
        if not isinstance(value, str) or value not in ALLOWED_TOOLS:
            return None
        return FilterOperation(field='tool', operation=operation, value=value)

    if operation == 'change_presentation':
        if not isinstance(value, list):
            return None
        cleaned = [p for p in value if isinstance(p, str) and p in ALLOWED_PRESENTATION]
        if not cleaned:
            return None
        return FilterOperation(field='presentation', operation=operation, value=cleaned)

    if field == 'min_amount' and operation in ('set', 'clear', 'remove'):
        if operation == 'set':
            if isinstance(value, (str, int)) and not isinstance(value, bool):
                return FilterOperation(field='min_amount', operation='set', value=str(value).strip())
            return None
        return FilterOperation(field='min_amount', operation='clear', value=None)

    if operation in ('clear', 'remove') and value is None:
        return FilterOperation(field=field, operation='clear', value=None)

    if operation == 'set' and field in ('months', 'limit', 'group_by', 'sort', 'period'):
        if field == 'period' and isinstance(value, str):
            period_val = _normalize_period_value({'period_label': value})
            if period_val:
                return FilterOperation(
                    field='period',
                    operation='replace_period',
                    value=period_val,
                )
        return FilterOperation(field=field, operation=operation, value=value)

    return None


def _resolve_vendor_value(value: Any, *, operation: str) -> Any:
    if operation == 'remove':
        if isinstance(value, int) and not isinstance(value, bool) and value >= 1:
            # IDs only accepted for remove when already in conversation; still
            # re-check existence in tenant schema.
            try:
                builder = resolve_vendor(vendor_id=value)
            except (VendorNotFoundError, AmbiguousVendorError):
                return None
            return {'id': builder.pk, 'name': builder.name}
        if isinstance(value, str) and value.strip():
            try:
                builder = resolve_vendor(name=value.strip())
            except AmbiguousVendorError as exc:
                labels = ', '.join(f'{c.name}' for c in exc.candidates[:5])
                return {'clarify': f'Multiple vendors match. Please clarify: {labels}.'}
            except VendorNotFoundError:
                return None
            return {'id': builder.pk, 'name': builder.name}
        return None

    # set / add — names preferred; ignore bare IDs from the model.
    name = None
    if isinstance(value, str):
        name = value.strip()
    elif isinstance(value, dict):
        # Accept name; ignore client/model-supplied id unless name resolves to it.
        if isinstance(value.get('name'), str):
            name = value['name'].strip()
    if not name:
        return None
    # Strip trailing "too"
    name = re.sub(r'\s+too$', '', name, flags=re.IGNORECASE).strip()
    try:
        builder = resolve_vendor(name=name)
    except AmbiguousVendorError as exc:
        labels = ', '.join(f'{c.name}' for c in exc.candidates[:5])
        return {'clarify': f'Multiple vendors match. Please clarify: {labels}.'}
    except VendorNotFoundError:
        return {'clarify': f'I could not find a vendor named "{name}".'}
    return {'id': builder.pk, 'name': builder.name}


def _normalize_period_value(value: Any) -> dict[str, str] | None:
    if isinstance(value, str) and value.strip():
        label = value.strip().lower()
        try:
            return resolved_period_value(label)
        except PeriodValidationError:
            return None
    if not isinstance(value, dict):
        return None
    label = value.get('period_label') or value.get('label') or value.get('period')
    date_from = value.get('date_from')
    date_to = value.get('date_to')
    if isinstance(label, str) and label.strip() and (not date_from or not date_to):
        try:
            return resolved_period_value(label.strip().lower())
        except PeriodValidationError:
            return None
    if isinstance(date_from, str) and isinstance(date_to, str) and date_from and date_to:
        try:
            start, end = resolve_period(
                date_from=date_from.strip(),
                date_to=date_to.strip(),
            )
        except PeriodValidationError:
            return None
        out = {
            'period_label': (
                label.strip().lower()
                if isinstance(label, str) and label.strip()
                else 'custom_range'
            ),
            'date_from': start.isoformat(),
            'date_to': end.isoformat(),
            'timezone': getattr(settings, 'TIME_ZONE', 'UTC') or 'UTC',
        }
        tz = value.get('timezone')
        if isinstance(tz, str) and tz.strip():
            out['timezone'] = tz.strip()
        return out
    return None


def build_new_query_params_from_llm(plan: LLMPlan) -> dict[str, Any]:
    """
    Convert sanitized LLM params into tool params for an authoritative new query.
    Resolves vendor names; never trusts model IDs.
    """
    params = deepcopy(plan.params)
    vendor_name = params.pop('vendor', None)
    if vendor_name:
        builder = resolve_vendor(name=vendor_name)
        params['vendor'] = builder.name
        params['vendor_id'] = builder.pk
    if plan.presentation:
        wants_chart = bool(set(plan.presentation) & {'bar_chart', 'line_chart', 'donut_chart'})
        wants_table = 'table' in plan.presentation
        if wants_chart or wants_table:
            params['include_chart'] = wants_chart
            params['include_table'] = wants_table or not wants_chart
    return params
