"""Build response-facing active_filters from validated conversation state."""

from __future__ import annotations

from datetime import date
from typing import Any

from appassistant.services.conversation_state import (
    METRIC_NET_INVOICED_SPEND,
    validate_state,
)
from appassistant.services.copy import period_phrase
from appassistant.services.spend import SPEND_METRIC_LABEL


def active_filters_payload(state: dict[str, Any] | None) -> dict[str, Any]:
    """
    Compact, UI-ready filters from server-validated state.

    Never trust client-supplied filters; only emit what Django stored.
    """
    try:
        validated = validate_state(state)
    except Exception:
        validated = validate_state(None)

    filters = validated.get('filters') or {}
    chips: list[dict[str, Any]] = []

    metric = validated.get('metric') or METRIC_NET_INVOICED_SPEND
    tool = validated.get('tool')

    # Parameter-trace chips (UI). Order: tool → vendors → amount → period → metric.
    if tool:
        chips.append({
            'key': 'tool',
            'label': _tool_chip_label(tool),
            'value': tool,
            'removable': False,
        })

    for vendor in filters.get('vendors') or []:
        chips.append({
            'key': 'vendor',
            'label': vendor.get('name') or f"Vendor #{vendor.get('id')}",
            'value': vendor.get('id'),
            'removable': True,
        })

    if filters.get('min_amount') is not None:
        chips.append({
            'key': 'min_amount',
            'label': f"Over ${filters['min_amount']}",
            'value': filters['min_amount'],
            'removable': True,
        })

    date_from = filters.get('date_from')
    date_to = filters.get('date_to')
    period_label = filters.get('period_label')
    months = filters.get('months')
    if date_from and date_to:
        chips.append({
            'key': 'period',
            'label': _period_chip_label(date_from, date_to, period_label, months),
            'value': {
                'period_label': period_label,
                'date_from': date_from,
                'date_to': date_to,
                'timezone': filters.get('timezone'),
                'months': months,
            },
            # Period is required for spend tools; clear via "Clear filters".
            'removable': False,
        })
    elif period_label or months:
        label = period_label or f'last {months} months'
        chips.append({
            'key': 'period',
            'label': str(label).replace('_', ' '),
            'value': {'period_label': period_label, 'months': months},
            'removable': False,
        })

    comparison = filters.get('comparison_period')
    if comparison:
        chips.append({
            'key': 'comparison_period',
            'label': (
                f"vs {comparison.get('date_from')} – {comparison.get('date_to')}"
            ),
            'value': comparison,
            'removable': True,
        })

    chips.append({
        'key': 'metric',
        'label': SPEND_METRIC_LABEL,
        'value': metric,
        'removable': False,
    })

    return {
        'domain': validated.get('domain'),
        'metric': metric,
        'tool': tool,
        'filters': filters,
        'presentation': validated.get('presentation') or [],
        'chips': chips,
        'inherited': bool(filters or tool),
    }


_TOOL_LABELS = {
    'list_purchase_transactions': 'Transactions',
    'sum_purchase_spending': 'Total spending',
    'purchases_by_vendor': 'By vendor',
    'compare_purchases_by_vendor': 'Compare vendors',
    'top_vendors_by_spending': 'Top vendors',
    'spending_timeseries': 'Spending trend',
    'compare_vendor_spending_periods': 'Compare periods',
}


def _tool_chip_label(tool: str) -> str:
    return _TOOL_LABELS.get(tool, tool.replace('_', ' '))


def _period_chip_label(
    date_from: str,
    date_to: str,
    period_label: str | None,
    months: int | None = None,
) -> str:
    try:
        start = date.fromisoformat(str(date_from)[:10])
        end = date.fromisoformat(str(date_to)[:10])
        phrase = period_phrase(start, end, months=months)
        if phrase and ' to ' not in phrase:
            return phrase
        # Readable absolute range for parameter tracing.
        return (
            f'{start.strftime("%b")} {start.day}, {start.year}'
            f' – {end.strftime("%b")} {end.day}, {end.year}'
        )
    except Exception:
        pass
    if period_label and period_label not in ('custom_range', 'last_n_months'):
        return period_label.replace('_', ' ')
    return f'{date_from} – {date_to}'
