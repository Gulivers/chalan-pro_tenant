"""
compare_vendor_spending_periods — same filters, two periods (D6).

Auditable comparison: Django computes both totals and the delta.
The LLM must not run two tools and invent the difference.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from django.conf import settings

from appassistant.services.blocks import kpi_currency, table_block, text_block
from appassistant.services.copy import format_money_display, period_phrase
from appassistant.services.money import as_money_str, coerce_money, zero_money
from appassistant.services.spend import SPEND_DEFINITION, SPEND_METRIC_LABEL, SPEND_METRIC_SHORT
from appassistant.tools._common import (
    filtered_spend_qs,
    optional_int,
    optional_str,
    parse_min_amount,
    parse_period_bounds,
    parse_vendor_ids,
    require_view_document,
    resolve_vendors_or_raise,
    sum_amount,
    tool_result,
)
from appassistant.tools.base import AssistantTool
from appassistant.tools.errors import validation_error

_PERCENT_Q = Decimal('0.01')


class CompareVendorSpendingPeriodsTool(AssistantTool):
    name = 'compare_vendor_spending_periods'
    description = (
        'Compare Net invoiced spending for the same vendor/filters across a '
        f'primary period and a comparison period. Spend definition: {SPEND_DEFINITION}'
    )
    spend_definition = SPEND_DEFINITION

    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        params = dict(params or {})
        primary_from, primary_to = parse_period_bounds(params)
        comparison = params.get('comparison_period')
        if not isinstance(comparison, dict):
            raise validation_error(
                'comparison_period is required '
                '(object with date_from, date_to, optional period_label).'
            )
        try:
            cmp_from = _as_date(comparison.get('date_from'), 'comparison_period.date_from')
            cmp_to = _as_date(comparison.get('date_to'), 'comparison_period.date_to')
        except ValueError as exc:
            raise validation_error(str(exc)) from exc
        if cmp_from > cmp_to:
            raise validation_error(
                'comparison_period.date_from must be on or before date_to.'
            )
        label = comparison.get('period_label') or comparison.get('label') or 'comparison'
        if not isinstance(label, str) or not label.strip():
            label = 'comparison'

        vendor = optional_str(params, 'vendor')
        vendor_id = optional_int(params, 'vendor_id', min_v=1)
        vendor_ids = parse_vendor_ids(params)
        if vendor is None and vendor_id is None and not vendor_ids:
            raise validation_error('vendor, vendor_id, or vendor_ids is required.')

        return {
            'vendor': vendor,
            'vendor_id': vendor_id,
            'vendor_ids': vendor_ids,
            'min_amount': parse_min_amount(params),
            'date_from': primary_from,
            'date_to': primary_to,
            'period_label': optional_str(params, 'period', max_len=64) or 'primary',
            'comparison_period': {
                'period_label': label.strip(),
                'date_from': cmp_from,
                'date_to': cmp_to,
                'timezone': comparison.get('timezone')
                or getattr(settings, 'TIME_ZONE', 'UTC')
                or 'UTC',
            },
        }

    def execute(self, *, user, params: dict[str, Any]) -> dict[str, Any]:
        require_view_document(user)
        p = self.validate_params(params)
        builders = resolve_vendors_or_raise(
            vendor=p['vendor'],
            vendor_id=p['vendor_id'],
            vendor_ids=p['vendor_ids'],
            required=True,
        )
        vendor_label = (
            builders[0].name
            if len(builders) == 1
            else ', '.join(b.name for b in builders)
        )

        primary_qs = filtered_spend_qs(
            date_from=p['date_from'],
            date_to=p['date_to'],
            builders=builders,
            min_amount=p['min_amount'],
        )
        cmp = p['comparison_period']
        comparison_qs = filtered_spend_qs(
            date_from=cmp['date_from'],
            date_to=cmp['date_to'],
            builders=builders,
            min_amount=p['min_amount'],
        )

        primary_total = sum_amount(primary_qs)
        comparison_total = sum_amount(comparison_qs)
        primary_count = primary_qs.count()
        comparison_count = comparison_qs.count()

        difference = coerce_money(primary_total - comparison_total)
        pct = _percent_change(primary_total, comparison_total)

        primary_phrase = period_phrase(p['date_from'], p['date_to'])
        comparison_phrase = period_phrase(cmp['date_from'], cmp['date_to'])

        blocks = [
            kpi_currency(
                block_id='primary-period-spending',
                title=f'Primary ({primary_phrase})',
                amount=primary_total,
                subtitle=f'{SPEND_METRIC_LABEL} · {primary_count} invoice(s)',
            ),
            kpi_currency(
                block_id='comparison-period-spending',
                title=f'Compared ({comparison_phrase})',
                amount=comparison_total,
                subtitle=f'{SPEND_METRIC_LABEL} · {comparison_count} invoice(s)',
            ),
            kpi_currency(
                block_id='period-difference',
                title='Absolute difference (primary − compared)',
                amount=difference,
                subtitle=_difference_subtitle(pct),
            ),
            table_block(
                block_id='period-comparison-table',
                title=f'{SPEND_METRIC_LABEL} period comparison',
                columns=[
                    {'key': 'period_role', 'label': 'Role'},
                    {'key': 'period', 'label': 'Period'},
                    {'key': 'invoices', 'label': 'Invoices'},
                    {'key': 'total', 'label': 'Net spending', 'format': 'currency'},
                ],
                rows=[
                    {
                        'period_role': 'primary',
                        'period': f"{p['date_from']} – {p['date_to']}",
                        'period_label': p['period_label'],
                        'invoices': primary_count,
                        'total': as_money_str(primary_total),
                    },
                    {
                        'period_role': 'compared',
                        'period': f"{cmp['date_from']} – {cmp['date_to']}",
                        'period_label': cmp['period_label'],
                        'invoices': comparison_count,
                        'total': as_money_str(comparison_total),
                    },
                ],
            ),
        ]

        if pct is None:
            blocks.append(
                text_block(
                    block_id='period-pct-note',
                    text=(
                        'Percent change is not available because the compared '
                        'period total is zero.'
                    ),
                    title='Percent change',
                )
            )

        message = (
            f'{SPEND_METRIC_SHORT} with {vendor_label}: '
            f'{format_money_display(primary_total)} for {primary_phrase} vs '
            f'{format_money_display(comparison_total)} for {comparison_phrase} '
            f'(difference {format_money_display(difference)}'
            + (
                f', {as_money_str(pct)}%'
                if pct is not None
                else ', percent change n/a'
            )
            + ').'
        )

        return tool_result(
            tool_name=self.name,
            message=message,
            blocks=blocks,
            row_count=primary_count + comparison_count,
            invoice_count=primary_count + comparison_count,
            partial=False,
        )


def _as_date(value: Any, field: str) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value.strip():
        try:
            return date.fromisoformat(value.strip())
        except ValueError as exc:
            raise ValueError(f'{field} must be an ISO date (YYYY-MM-DD).') from exc
    raise ValueError(f'{field} must be an ISO date string.')


def _percent_change(primary: Decimal, comparison: Decimal) -> Decimal | None:
    """(primary - comparison) / comparison * 100; None when comparison is zero."""
    if comparison == zero_money() or comparison == 0:
        return None
    return ((primary - comparison) / comparison * Decimal('100')).quantize(
        _PERCENT_Q,
        rounding=ROUND_HALF_UP,
    )


def _difference_subtitle(pct: Decimal | None) -> str:
    if pct is None:
        return 'Percent change n/a (compared period is zero)'
    return f'Change vs compared: {as_money_str(pct)}%'
