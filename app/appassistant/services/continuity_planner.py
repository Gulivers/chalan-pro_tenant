"""
Deterministic continuity planner (C2).

Temporary bridge until C4 LLM planner. Maps follow-up utterances onto
structured filter_operations. Never invents entity IDs — vendor names are
resolved later by Django services.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

from django.conf import settings

from appassistant.services.conversation_state import empty_state
from appassistant.services.filter_merger import FilterOperation
from appassistant.services.periods import PeriodValidationError, resolve_period
from appassistant.services.vendors import (
    AmbiguousVendorError,
    VendorNotFoundError,
    resolve_vendor,
)

_MONEY = r'\$?\s*([\d,]+(?:\.\d{1,2})?)'


@dataclass
class ContinuityPlan:
    """Planner output for one user turn."""

    is_follow_up: bool = False
    intent: str = ''
    tool: str | None = None
    operations: list[FilterOperation] = field(default_factory=list)
    clarification: str | None = None
    needs_clarification: bool = False
    start_over: bool = False
    unsupported_message: str | None = None


def plan_continuity(
    message: str,
    *,
    previous_state: dict[str, Any] | None,
    state_expired: bool,
) -> ContinuityPlan:
    text = (message or '').strip()
    if not text:
        return ContinuityPlan()

    normalized = ' '.join(text.lower().split())

    if _is_start_over(normalized):
        return ContinuityPlan(is_follow_up=True, intent='start_over', start_over=True)

    if state_expired or not previous_state or not (previous_state.get('filters') or previous_state.get('tool')):
        return ContinuityPlan()

    # Compare before replace ("compare with last month" vs "last month").
    if re.search(r'\bcompare\b.*\b(last\s+month|previous\s+month)\b', normalized) or re.search(
        r'\b(last\s+month|previous\s+month)\b.*\bcompare\b',
        normalized,
    ):
        return _plan_compare_last_month(previous_state)

    # "and for the two previous calendar months please?"
    m_prev_n = re.search(
        r'(?:the\s+)?(\d+|two|three|four|five|six)\s+previous\s+calendar\s+months?',
        normalized,
    )
    if m_prev_n:
        n = _parse_int_word(m_prev_n.group(1))
        if n is not None:
            return _plan_replace_previous_calendar_months(previous_state, n)

    # "and for the previous calendar month please?" / "what about last month?"
    if re.search(
        r'\b(previous\s+calendar\s+month|last\s+calendar\s+month|'
        r'previous\s+month|last\s+month)\b',
        normalized,
    ):
        return _plan_replace_last_month(previous_state)

    # Follow-up only (whole utterance). Do NOT match "over $X" inside a full
    # new query like "Show me Home Depot transactions over $100 this month."
    m = re.search(
        r'^(?:only\s+(?:those|the\s+ones|invoices|purchases)\s+)?'
        r'(?:over|above|greater\s+than)\s+' + _MONEY + r'\.?$',
        normalized,
    )
    if m:
        amount = _parse_money(m.group(1))
        if amount is not None:
            return ContinuityPlan(
                is_follow_up=True,
                intent='add_min_amount',
                tool=previous_state.get('tool') or 'list_purchase_transactions',
                operations=[
                    FilterOperation(
                        field='min_amount',
                        operation='set',
                        value=str(amount),
                    )
                ],
            )

    if re.search(
        r'\b(include\s+all\s+amounts|any\s+amount|all\s+amounts|no\s+minimum|regardless\s+of\s+amount)\b',
        normalized,
    ):
        return ContinuityPlan(
            is_follow_up=True,
            intent='clear_min_amount',
            tool=previous_state.get('tool') or 'list_purchase_transactions',
            operations=[
                FilterOperation(field='min_amount', operation='clear', value=None),
            ],
        )

    if re.search(
        r'\b(show\s+(?:me\s+)?(?:the\s+)?(?:underlying\s+)?documents?|'
        r'show\s+(?:me\s+)?(?:the\s+)?details|list\s+(?:the\s+)?(?:invoices|documents))\b',
        normalized,
    ):
        return _plan_show_documents(previous_state)

    if re.search(r'\b(graph\s+it|chart\s+it|show\s+(?:it\s+)?as\s+a?\s*graph)\b', normalized):
        return ContinuityPlan(
            is_follow_up=True,
            intent='change_presentation',
            tool=previous_state.get('tool'),
            operations=[
                FilterOperation(
                    field='presentation',
                    operation='change_presentation',
                    value=['message', 'bar_chart', 'sources'],
                )
            ],
        )

    if re.search(r'\b(show\s+it\s+as\s+a?\s*table|as\s+a?\s*table\s+instead)\b', normalized):
        return ContinuityPlan(
            is_follow_up=True,
            intent='change_presentation',
            tool=previous_state.get('tool'),
            operations=[
                FilterOperation(
                    field='presentation',
                    operation='change_presentation',
                    value=['message', 'table', 'sources'],
                )
            ],
        )

    m = re.search(
        r'(?:use|switch\s+to|try)\s+(.+?)\s+instead',
        normalized,
    )
    if m:
        return _plan_vendor_replace(m.group(1), previous_state)

    m = re.search(
        r'(?:include|add|also\s+include)\s+(.+?)(?:\s+too)?\.?$',
        normalized,
    )
    if m and 'amount' not in m.group(1):
        return _plan_vendor_add(m.group(1), previous_state)

    if re.search(r'\b(any\s+vendor|all\s+vendors|regardless\s+of\s+vendor)\b', normalized):
        return ContinuityPlan(
            is_follow_up=True,
            intent='clear_vendor',
            tool=previous_state.get('tool'),
            operations=[
                FilterOperation(field='vendor', operation='clear', value=None),
            ],
        )

    if re.search(
        r'\b(clear\s+comparison|without\s+comparison|no\s+comparison|'
        r'remove\s+comparison)\b',
        normalized,
    ):
        return ContinuityPlan(
            is_follow_up=True,
            intent='clear_comparison',
            tool=previous_state.get('tool') or 'purchases_by_vendor',
            operations=[
                FilterOperation(
                    field='comparison_period',
                    operation='clear',
                    value=None,
                ),
            ],
        )

    # Chip UI: "Remove vendor Home Depot."
    m = re.search(
        r'^(?:remove|drop|without)\s+(?:vendor\s+|supplier\s+)?(.+?)\.?$',
        normalized,
    )
    if m:
        return _plan_vendor_remove(m.group(1), previous_state)

    # Ambiguous pronoun with multiple vendors.
    if re.search(r'\b(its|their)\s+documents?\b', normalized):
        vendors = (previous_state.get('filters') or {}).get('vendors') or []
        if len(vendors) > 1:
            names = ' or '.join(v.get('name', '?') for v in vendors)
            return ContinuityPlan(
                is_follow_up=True,
                intent='clarify_vendor',
                needs_clarification=True,
                clarification=f'Which vendor do you mean: {names}?',
                operations=[
                    FilterOperation(
                        field='vendor',
                        operation='clarify',
                        value=f'Which vendor do you mean: {names}?',
                    )
                ],
            )
        if len(vendors) == 1:
            return _plan_show_documents(previous_state)

    return ContinuityPlan()


def resolved_period_value(period_label: str) -> dict[str, str]:
    start, end = resolve_period(period=period_label)
    return {
        'period_label': period_label,
        'date_from': start.isoformat(),
        'date_to': end.isoformat(),
        'timezone': getattr(settings, 'TIME_ZONE', 'UTC') or 'UTC',
    }


def _plan_replace_last_month(previous_state: dict[str, Any]) -> ContinuityPlan:
    return _plan_replace_previous_calendar_months(previous_state, 1)


def _plan_replace_previous_calendar_months(
    previous_state: dict[str, Any],
    n: int,
) -> ContinuityPlan:
    label = 'last_month' if n == 1 else f'previous_{n}_calendar_months'
    try:
        period = resolved_period_value(label)
    except PeriodValidationError as exc:
        return ContinuityPlan(
            is_follow_up=True,
            needs_clarification=True,
            clarification=str(exc),
        )
    tool = previous_state.get('tool') or 'sum_purchase_spending'
    return ContinuityPlan(
        is_follow_up=True,
        intent='replace_period',
        tool=tool,
        operations=[
            FilterOperation(field='period', operation='replace_period', value=period),
        ],
    )


def _parse_int_word(token: str) -> int | None:
    token = (token or '').strip().lower()
    if token.isdigit():
        value = int(token)
        return value if 1 <= value <= 12 else None
    mapping = {
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
    }
    return mapping.get(token)


def _plan_compare_last_month(previous_state: dict[str, Any]) -> ContinuityPlan:
    try:
        period = resolved_period_value('last_month')
    except PeriodValidationError as exc:
        return ContinuityPlan(
            is_follow_up=True,
            needs_clarification=True,
            clarification=str(exc),
        )
    return ContinuityPlan(
        is_follow_up=True,
        intent='compare_period',
        tool='compare_vendor_spending_periods',
        operations=[
            FilterOperation(field='period', operation='compare_with_period', value=period),
        ],
    )


def _plan_show_documents(previous_state: dict[str, Any]) -> ContinuityPlan:
    # Multi-vendor lists are supported (C3). Ambiguous pronouns are handled
    # by the caller before invoking this helper.
    return ContinuityPlan(
        is_follow_up=True,
        intent='show_documents',
        tool='list_purchase_transactions',
        operations=[
            FilterOperation(
                field='tool',
                operation='change_tool',
                value='list_purchase_transactions',
            )
        ],
    )


def _plan_vendor_replace(raw_name: str, previous_state: dict[str, Any]) -> ContinuityPlan:
    vendor = _resolve_vendor_name(raw_name)
    if vendor.needs_clarification or vendor.clarification:
        return ContinuityPlan(
            is_follow_up=True,
            intent='replace_vendor',
            needs_clarification=vendor.needs_clarification,
            clarification=vendor.clarification,
            operations=vendor.operations,
        )
    assert vendor.vendor_payload is not None
    return ContinuityPlan(
        is_follow_up=True,
        intent='replace_vendor',
        tool=previous_state.get('tool') or 'list_purchase_transactions',
        operations=[
            FilterOperation(
                field='vendor',
                operation='set',
                value=vendor.vendor_payload,
            )
        ],
    )


def _plan_vendor_add(raw_name: str, previous_state: dict[str, Any]) -> ContinuityPlan:
    vendor = _resolve_vendor_name(raw_name)
    if vendor.needs_clarification or vendor.clarification:
        return ContinuityPlan(
            is_follow_up=True,
            intent='add_vendor',
            needs_clarification=vendor.needs_clarification,
            clarification=vendor.clarification,
            operations=vendor.operations,
        )
    assert vendor.vendor_payload is not None
    return ContinuityPlan(
        is_follow_up=True,
        intent='add_vendor',
        tool=previous_state.get('tool') or 'list_purchase_transactions',
        operations=[
            FilterOperation(
                field='vendor',
                operation='add',
                value=vendor.vendor_payload,
            )
        ],
    )


def _plan_vendor_remove(raw_name: str, previous_state: dict[str, Any]) -> ContinuityPlan:
    """
    Remove one vendor from state (chip dismiss).

    Prefer matching an already-active vendor by name so chip labels work
    without re-resolving ambiguous catalog names.
    """
    name = (raw_name or '').strip(' .,;:!?\'"')
    name_l = name.lower()
    active = (previous_state.get('filters') or {}).get('vendors') or []
    matched = [
        v for v in active
        if str(v.get('name') or '').strip().lower() == name_l
    ]
    if len(matched) == 1 and isinstance(matched[0].get('id'), int):
        return ContinuityPlan(
            is_follow_up=True,
            intent='remove_vendor',
            tool=previous_state.get('tool') or 'list_purchase_transactions',
            operations=[
                FilterOperation(
                    field='vendor',
                    operation='remove',
                    value=matched[0]['id'],
                )
            ],
        )

    vendor = _resolve_vendor_name(raw_name)
    if vendor.needs_clarification or vendor.clarification:
        return ContinuityPlan(
            is_follow_up=True,
            intent='remove_vendor',
            needs_clarification=vendor.needs_clarification,
            clarification=vendor.clarification,
            operations=vendor.operations,
        )
    assert vendor.vendor_payload is not None
    vendor_id = vendor.vendor_payload.get('id')
    return ContinuityPlan(
        is_follow_up=True,
        intent='remove_vendor',
        tool=previous_state.get('tool') or 'list_purchase_transactions',
        operations=[
            FilterOperation(
                field='vendor',
                operation='remove',
                value=vendor_id,
            )
        ],
    )


@dataclass
class _VendorResolve:
    vendor_payload: dict[str, Any] | None = None
    needs_clarification: bool = False
    clarification: str | None = None
    operations: list[FilterOperation] = field(default_factory=list)


def _resolve_vendor_name(raw: str) -> _VendorResolve:
    name = (raw or '').strip(' .,;:!?\'"')
    name = re.sub(r'\s+too$', '', name).strip()
    if not name:
        return _VendorResolve(
            needs_clarification=True,
            clarification='Which vendor should I use?',
        )
    try:
        builder = resolve_vendor(name=name)
    except AmbiguousVendorError as exc:
        labels = ', '.join(f'{c.name} (#{c.id})' for c in exc.candidates[:5])
        msg = f'Multiple vendors match. Please clarify: {labels}.'
        return _VendorResolve(
            needs_clarification=True,
            clarification=msg,
            operations=[
                FilterOperation(field='vendor', operation='clarify', value=msg),
            ],
        )
    except VendorNotFoundError:
        return _VendorResolve(
            needs_clarification=True,
            clarification=f'I could not find a vendor named "{name}".',
        )
    return _VendorResolve(
        vendor_payload={'id': builder.pk, 'name': builder.name},
    )


def _is_start_over(normalized: str) -> bool:
    return bool(
        re.search(
            r'^(start\s+over|new\s+(question|conversation|chat)|clear\s+(filters|context)|reset)\.?$',
            normalized,
        )
    )


def _parse_money(raw: str) -> Decimal | None:
    cleaned = (raw or '').replace(',', '').replace(' ', '').strip()
    if not cleaned:
        return None
    try:
        amount = Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None
    if amount < 0:
        return None
    return amount.quantize(Decimal('0.01'))


def empty_previous() -> dict[str, Any]:
    return empty_state()
