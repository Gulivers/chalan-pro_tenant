"""
spending_timeseries — monthly PINV spend series.

Spend = PINV + is_active only; NOT document_type__is_purchase.
"""

from __future__ import annotations

from typing import Any

from django.db.models import Sum
from django.db.models.functions import TruncMonth

from appassistant.services.blocks import line_chart_block, table_block
from appassistant.services.copy import timeseries_message
from appassistant.services.money import as_money_str, coerce_money, zero_money
from appassistant.services.periods import iter_month_labels, resolve_period
from appassistant.services.spend import SPEND_DEFINITION, SPEND_METRIC_LABEL
from appassistant.tools._common import (
    filtered_spend_qs,
    optional_int,
    optional_str,
    parse_months,
    parse_period_bounds,
    require_view_document,
    resolve_vendor_or_raise,
    tool_result,
)
from appassistant.tools.base import AssistantTool
from appassistant.tools.errors import validation_error


class SpendingTimeseriesTool(AssistantTool):
    name = 'spending_timeseries'
    description = (
        'Monthly Net invoiced spending time series. '
        'Accepts months (1..12) or period (e.g. this_month). Optional vendor. '
        f'Spend definition: {SPEND_DEFINITION}'
    )
    spend_definition = SPEND_DEFINITION

    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        params = dict(params or {})
        months = parse_months(params, required=False)
        period = optional_str(params, 'period', max_len=64)
        has_explicit_range = bool(params.get('date_from') or params.get('date_to'))
        try:
            if months is not None and not period and not has_explicit_range:
                date_from, date_to = resolve_period(months=months)
            elif period or has_explicit_range or months is not None:
                # period=this_month, last_3_months, or months+period from planners.
                date_from, date_to = parse_period_bounds(params)
                if months is None:
                    months = max(
                        1,
                        (date_to.year - date_from.year) * 12
                        + (date_to.month - date_from.month)
                        + 1,
                    )
            else:
                raise validation_error(
                    'Provide months (1..12) or period (e.g. this_month).'
                )
        except Exception as exc:  # noqa: BLE001
            from appassistant.services.periods import PeriodValidationError
            from appassistant.tools.errors import ToolError

            if isinstance(exc, ToolError):
                raise
            if isinstance(exc, PeriodValidationError):
                raise validation_error(str(exc)) from exc
            raise
        return {
            'months': months,
            'date_from': date_from,
            'date_to': date_to,
            'vendor': optional_str(params, 'vendor'),
            'vendor_id': optional_int(params, 'vendor_id', min_v=1),
        }

    def execute(self, *, user, params: dict[str, Any]) -> dict[str, Any]:
        require_view_document(user)
        p = self.validate_params(params)
        builder = resolve_vendor_or_raise(
            vendor=p['vendor'],
            vendor_id=p['vendor_id'],
            required=False,
        )
        qs = filtered_spend_qs(
            date_from=p['date_from'],
            date_to=p['date_to'],
            builder=builder,
        )
        invoice_count = qs.count()
        month_meta = iter_month_labels(p['date_from'], p['date_to'])
        labels = [m[0] for m in month_meta]

        monthly_totals = {
            row['month'].strftime('%Y-%m'): (
                coerce_money(row['total']) if row['total'] is not None else zero_money()
            )
            for row in (
                qs.annotate(month=TruncMonth('date'))
                .values('month')
                .annotate(total=Sum('total_amount'))
            )
            if row['month']
        }

        values = [as_money_str(monthly_totals.get(label, zero_money())) for label in labels]
        rows = [
            {'month': label, 'total_amount': value}
            for label, value in zip(labels, values)
        ]

        vendor_label = builder.name if builder else 'all vendors'
        blocks = [
            line_chart_block(
                block_id='spending-timeseries',
                title=f'{SPEND_METRIC_LABEL} ({vendor_label})',
                labels=labels,
                values=values,
                series_name=SPEND_METRIC_LABEL,
            ),
            table_block(
                block_id='spending-timeseries-table',
                title=f'Monthly {SPEND_METRIC_LABEL.lower()}',
                columns=[
                    {'key': 'month', 'label': 'Month'},
                    {'key': 'total_amount', 'label': 'Net spending', 'format': 'currency'},
                ],
                rows=rows,
            ),
        ]
        message = timeseries_message(
            vendor_name=builder.name if builder else None,
            months=p['months'],
            invoice_count=invoice_count,
            date_from=p['date_from'],
            date_to=p['date_to'],
        )
        return tool_result(
            tool_name=self.name,
            message=message,
            blocks=blocks,
            row_count=len(rows),
            invoice_count=invoice_count,
            partial=False,
        )
